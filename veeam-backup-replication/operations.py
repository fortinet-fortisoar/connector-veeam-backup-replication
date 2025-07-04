"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

import re
import requests
from .constants import *
from .veeam_auth import *
from datetime import datetime
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('veeam-backup-replication')


class VeeamDataPlatform(object):
    def __init__(self, config):
        self.server_url = config.get('resource', '').strip('/')
        if not self.server_url.startswith('https://') and not self.server_url.startswith('http://'):
            self.server_url = 'https://' + self.server_url
        self.port = config.get("port")
        self.host = self.server_url + ':' + str(self.port)
        self.api_ver = config.get("api_revision")
        self.verify_ssl = config.get('verify_ssl')
        self.veeam_auth = VeeamAuth(config)
        self.connector_info = config.pop('connector_info', '')

    def make_rest_call(self, config, endpoint=None, params=None, json_body=None, payload=None, method='GET'):
        token = self.veeam_auth.validate_token(config, self.connector_info)
        headers = {'Authorization': token, 'x-api-version': self.api_ver}
        service_url = f'{self.host}/api/v1/{endpoint}'
        logger.debug('Request URL {0}'.format(service_url))
        # CURL UTILS CODE
        try:
            from connectors.debug_utils.curl_script import make_curl
            make_curl(method, service_url, headers=headers, params=params, data=json_body, verify_ssl=self.verify_ssl)
        except Exception as err:
            logger.debug(f"Error in curl utils: {str(err)}")

        try:
            response = requests.request(method, service_url, data=payload, headers=headers, json=json_body,
                                        params=params, verify=self.verify_ssl)
            if response.ok:
                if response.status_code == 204:
                    return response
                content_type = response.headers.get('Content-Type')
                if response.text != "" and 'application/json' in content_type:
                    return response.json()
                else:
                    return response.content
            else:
                if response.text != "":
                    try:
                        err_resp = response.json()
                        failure_msg = err_resp.get('message', '')
                        error_code = err_resp.get('errorCode', '')
                        error_msg = 'Response {0}: {1} Error Message: {2}'.format(
                            response.status_code,
                            error_code,
                            failure_msg
                        )
                    except ValueError:
                        error_msg = 'Response {0}: {1} Error Message: Invalid JSON in response'.format(
                            response.status_code,
                            response.reason
                        )
                else:
                    error_msg = '{0}:{1}'.format(response.status_code, response.reason)
                raise ConnectorError(error_msg)
        except requests.exceptions.SSLError:
            logger.error('An SSL error occurred')
            raise ConnectorError('An SSL error occurred')
        except requests.exceptions.ConnectionError:
            logger.error('A connection error occurred')
            raise ConnectorError('A connection error occurred')
        except requests.exceptions.Timeout:
            logger.error('The request timed out')
            raise ConnectorError('The request timed out')
        except requests.exceptions.RequestException:
            logger.error('There was an error while handling the request')
            raise ConnectorError('There was an error while handling the request')
        except Exception as e:
            logger.error('{0}'.format(e))
            raise ConnectorError('{0}'.format(e))


def build_params(params):
    return {k: v for k, v in params.items() if v is not None and v != ''}


def parse_comparison(value):
    match = re.match(r'^\s*(<=|>=|<|>)\s*(\d+)', value)
    if match:
        op, num = match.groups()
        return op_map[op], int(num)


def build_filter_expression(params, strict_match):
    filter_expression = []
    for key, value in params.items():
        if key in ["type", "platform"]:
            map_dict = property_to_map.get(key)
            value = map_dict.get(value)
        if isinstance(value, str) and "," in value:
            filter_expression.append(
                {
                    "type": "PredicateExpression",
                    "operation": "in",
                    "property": key,
                    "value": value
                })
        elif isinstance(value, str) and any(op in value for op in ['<=', '>=', '<', '>']):
            opr, val = parse_comparison(value.strip())
            filter_expression.append(
                {
                    "type": "PredicateExpression",
                    "operation": opr,
                    "property": key,
                    "value": val
                })
        else:
            filter_expression.append(
                {
                    "type": "PredicateExpression",
                    "operation": "equals" if strict_match or isinstance(value, int) else "contains",
                    "property": key,
                    "value": value
                })
    return {
        "filter": {
            "type": "GroupExpression",
            "operation": "and",
            "items": filter_expression
        }
    }


def build_sort_expression(params):
    return {
        "sorting": {
            "property": property_.get(params.pop('property', '') or 'Name'),
            "direction": direction.get(params.pop('direction', '') or 'Ascending')
        }
    }


def build_pagination_filter(params):
    return {
        "pagination": {
            "skip": params.pop('skip', '') or 0,
            "limit": params.pop('limit', '') or 50
        }
    }


def remove_microseconds(iso_str):
    iso_str = iso_str.replace('Z', '+00:00')
    dt = datetime.fromisoformat(iso_str)
    return dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def get_server_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    payload = {}
    payload.update(build_pagination_filter(params))
    if params.get('sort_by', '') == 'Property':
        params.pop('sort_by', '')
        payload.update(build_sort_expression(params))
    if params.get('filter_mode', '') == 'Simple':
        params.pop('filter_mode', '')
        if params:
            payload.update(build_filter_expression(params, params.pop('strict_match', False)))
    if params.get('filter_mode', '') == 'Advanced':
        payload.update({"filter": params.get('filter', {})})
    return vdp.make_rest_call(config, endpoint='inventory', json_body=payload, method='POST')


def get_unstructured_data_server_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    if not params.get('orderColumn', ''):
        params.pop('orderAsc', '')
    return vdp.make_rest_call(config, endpoint='inventory/unstructuredDataServers', params=params)


def get_microsoft_entra_id_tenant_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    if not params.get('orderColumn', ''):
        params.pop('orderAsc', '')
    return vdp.make_rest_call(config, endpoint='inventory/entraId/tenants', params=params)


def create_malware_event(config, params):
    vdp = VeeamDataPlatform(config)
    return vdp.make_rest_call(config, endpoint='malwareDetection/events', json_body=params, method='POST')


def get_malware_event_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    if params.get('detectedAfterTimeUtcFilter'):
        params['detectedAfterTimeUtcFilter'] = remove_microseconds(params.get('detectedAfterTimeUtcFilter'))
    if params.get('detectedBeforeTimeUtcFilter'):
        params['detectedBeforeTimeUtcFilter'] = remove_microseconds(params.get('detectedBeforeTimeUtcFilter'))
    if params.get('typeFilter'):
        params['typeFilter'] = event_type.get(params.get('typeFilter'))
    if params.get('stateFilter'):
        params['stateFilter'] = event_state.get(params.get('stateFilter'))
    if params.get('sourceFilter'):
        params['sourceFilter'] = event_source.get(params.get('sourceFilter'))
    if params.get('orderColumn'):
        params['orderColumn'] = sort_by.get(params.get('orderColumn'))
    if not params.get('orderColumn', ''):
        params.pop('orderAsc', '')
    return vdp.make_rest_call(config, endpoint='malwareDetection/events', params=params)


def scan_backup(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    scan_engine = params.pop('scanEngine', '')
    payload = {
        "backupObjectPair": [
            {
                "backupId": params.pop('backupId', ''),
                "backupObjectId": params.pop('backupObjectId', '')
            }
        ],
        "scanMode": scan_mode.get(params.pop('scanMode')),
        "scanEngine": {
            "useAntivirusEngine": "Antivirus Engine" in scan_engine,
            "useYaraRule": "YARA Rule" in scan_engine
        }
    }
    # Conditionally add yaraRule if needed
    if "YARA Rule" in scan_engine:
        payload["scanEngine"]["yaraRule"] = {
            "fileName": params.pop('fileName')
        }
    if params.pop('scanRange', ''):
        payload['scanRange'] = {"from": params.pop('from'), "to": params.pop('to')}
    payload.update(params)
    return vdp.make_rest_call(config, endpoint='malwareDetection/scanBackup', json_body=payload, method='POST')


def start_security_compliance_analyzer(config, params):
    vdp = VeeamDataPlatform(config)
    return vdp.make_rest_call(config, endpoint='securityAnalyzer/start', method='POST')


def get_security_compliance_analyzer_results(config, params):
    vdp = VeeamDataPlatform(config)
    return vdp.make_rest_call(config, endpoint='securityAnalyzer/bestPractices', method='GET')


def start_configuration_backup(config, params):
    vdp = VeeamDataPlatform(config)
    return vdp.make_rest_call(config, endpoint='configBackup/backup', method='POST')


def get_managed_server_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    if params.get('typeFilter', ''):
        params['typeFilter'] = server_type.get(params.get('typeFilter'))
    if not params.get('orderColumn', ''):
        params.pop('orderAsc', '')
    return vdp.make_rest_call(config, endpoint='backupInfrastructure/managedServers', params=params)


def start_instant_recovery(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    restore_type = restore_mode.get(params.pop('type', ''))
    enable_av = params.pop('antivirusScanEnabled', True)
    payload = {
        "restorePointId": params.pop('restorePointId', ''),
        "type": restore_type,
        "vmTagsRestoreEnabled": params.pop('vmTagsRestoreEnabled', True),
        "secureRestore": {
            "antivirusScanEnabled": enable_av
        },
        "nicsEnabled": params.pop('nicsEnabled', True),
        "powerUp": params.pop('powerUp', True),
        "reason": params.pop('reason', '')
    }
    # Conditionally extend secureRestore
    if enable_av:
        payload["secureRestore"].update({
            "virusDetectionAction": virus_detection_action.get(params.pop('virusDetectionAction')),
            "entireVolumeScanEnabled": params.pop('entireVolumeScanEnabled', True)
        })
    # Conditionally extend top-level payload
    if restore_type == 'Customized':
        payload.update({
            "datastore": params.pop('datastore'),
            "destination": params.pop('destination', {}),
            "overwrite": params.pop('overwrite', False)
        })
    return vdp.make_rest_call(config, endpoint='restore/instantRecovery/vSphere/vm', json_body=payload, method='POST')


def start_quick_backup(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    params['platform'] = platform.get(params.get('platform'))
    params['type'] = type_.get(params.get('type'))
    return vdp.make_rest_call(config, endpoint='jobs/quickBackup/vSphere', json_body=params, method='POST')


def get_backup_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    if params.get('createdAfterFilter'):
        params['createdAfterFilter'] = remove_microseconds(params.get('createdAfterFilter'))
    if params.get('createdBeforeFilter'):
        params['createdBeforeFilter'] = remove_microseconds(params.get('createdBeforeFilter'))
    sort_ = params.get('orderColumn', '')
    if sort_:
        params['orderColumn'] = sort_by.get(sort_)
    else:
        params.pop('orderAsc', '')
    return vdp.make_rest_call(config, endpoint='backups', params=params)


def get_repository_state_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    if params.get('typeFilter', ''):
        params['typeFilter'] = repo_type.get(params.get('typeFilter'))
    sort_ = params.get('orderColumn', '')
    if sort_:
        params['orderColumn'] = sort_by.get(sort_)
    else:
        params.pop('orderAsc', '')
    return vdp.make_rest_call(config, endpoint='backupInfrastructure/repositories/states', params=params)


def get_restore_point_list(config, params):
    vdp = VeeamDataPlatform(config)
    params = build_params(params)
    if params.get('createdAfterFilter'):
        params['createdAfterFilter'] = remove_microseconds(params.get('createdAfterFilter'))
    if params.get('createdBeforeFilter'):
        params['createdBeforeFilter'] = remove_microseconds(params.get('createdBeforeFilter'))
    if params.get('platformNameFilter', ''):
        params['platformNameFilter'] = platform_name.get(params.get('platformNameFilter'))
    sort_ = params.get('orderColumn', '')
    if sort_:
        params['orderColumn'] = sort_by.get(sort_)
    else:
        params.pop('orderAsc', '')
    return vdp.make_rest_call(config, endpoint='restorePoints', params=params)


def execute_an_api_request(config, params):
    try:
        vdp = VeeamDataPlatform(config)
        endpoint = params.get("endpoint")
        http_method = params.get("method")
        query_params = params.get("query_params") or None
        payload = params.get("payload") or None
        return vdp.make_rest_call(config, endpoint=endpoint, params=query_params, json_body=payload, method=http_method)
    except Exception as err:
        logger.exception("{0}".format(str(err)))
        raise ConnectorError("{0}".format(str(err)))


def check_health_ex(config, connector_info):
    try:
        return check(config, connector_info)
    except Exception as err:
        raise ConnectorError(str(err))


operations = {
    'get_server_list': get_server_list,
    'get_unstructured_data_server_list': get_unstructured_data_server_list,
    'get_microsoft_entra_id_tenant_list': get_microsoft_entra_id_tenant_list,
    'create_malware_event': create_malware_event,
    'get_malware_event_list': get_malware_event_list,
    'scan_backup': scan_backup,
    'start_security_compliance_analyzer': start_security_compliance_analyzer,
    'get_security_compliance_analyzer_results': get_security_compliance_analyzer_results,
    'start_configuration_backup': start_configuration_backup,
    'get_managed_server_list': get_managed_server_list,
    'start_instant_recovery': start_instant_recovery,
    'start_quick_backup': start_quick_backup,
    'get_backup_list': get_backup_list,
    'get_repository_state_list': get_repository_state_list,
    'get_restore_point_list': get_restore_point_list,
    'execute_an_api_request': execute_an_api_request,
    'check_health': check_health_ex
}
