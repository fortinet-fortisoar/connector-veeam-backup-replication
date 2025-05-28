"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

op_map = {
    '<': 'lessThan',
    '<=': 'lessThanOrEqual',
    '>': 'greaterThan',
    '>=': 'greaterThanOrEqual'
}

property_ = {
    "Platform": "platform",
    "Size": "size",
    "Host Name": "hostName",
    "Name": "name",
    "Type": "type",
    "Object ID": "objectId",
    "Uniform Resource Name": "urn"
}

direction = {
    "Ascending": "ascending",
    "Descending": "descending"
}

platform = {
    "VMware": "VMware",
    "Cloud Director": "CloudDirector"
}

type_ = {
    "Cloud Director Server": "CloudDirectorServer",
    "Organization": "Organization",
    "Organization VDC": "OrganizationVDC",
    "vApp": "vApp",
    "vCenter": "vCenter",
    "VM Template": "VmTemplate",
    "Unknown": "Unknown",
    "Virtual Machine": "VirtualMachine",
    "vCenter Server": "vCenterServer",
    "Data Center": "Datacenter",
    "Cluster": "Cluster",
    "Host": "Host",
    "Resource Pool": "ResourcePool",
    "Folder": "Folder",
    "Datastore": "Datastore",
    "Datastore Cluster": "DatastoreCluster",
    "Storage Policy": "StoragePolicy",
    "Template": "Template",
    "Compute Resource": "ComputeResource",
    "Virtual App": "VirtualApp",
    "Tag": "Tag",
    "Category": "Category",
    "Multi Tag": "Multitag",
    "Network": "Network",
    "DVS Network": "DVSNetwork"
}

property_to_map = {
    "type": type_,
    "platform": platform
}

event_type = {
    "Unknown": "Unknown",
    "Deleted Useful Files": "DeletedUsefulFiles",
    "Ransomware Notes": "RansomwareNotes",
    "Malware Extensions": "MalwareExtensions",
    "Encrypted Data": "EncryptedData",
    "YARA Scan": "YaraScan",
    "Antivirus Scan": "AntivirusScan",
    "Renamed Files": "RenamedFiles",
    "Indicator of Compromise": "IndicatorOfCompromise"
}

event_state = {
    "Created": "Created",
    "False Positive": "FalsePositive"
}

event_source = {
    "Manual": "Manual",
    "Internal Veeam Detector": "InternalVeeamDetector",
    "External": "External",
    "Mark as Clean Event": "MarkAsCleanEvent"
}

sort_by = {
    "Type": "Type",
    "Detection Time": "DetectionTimeUtc",
    "Backup Object ID": "BackupObjectId",
    "State": "State",
    "Source": "Source",
    "Severity": "Severity",
    "Created By": "CreatedBy",
    "Engine": "Engine",
    "Name": "Name",
    "Creation Time": "CreationTime",
    "Platform ID": "PlatformId",
    "Job ID": "JobId",
    "Policy Tag": "PolicyTag",
    "Host": "Host",
    "Path": "Path",
    "Capacity": "CapacityGB",
    "Free": "FreeGB",
    "Used Space": "UsedSpaceGB",
    "Description": "Description",
    "Backup ID": "BackupId"
}

scan_mode = {
    "Most Recent": "MostRecent",
    "All In Interval": "AllInInterval",
    "First In Interval": "FirstInInterval"
}

server_type = {
    "Windows Host": "WindowsHost",
    "Linux Host": "LinuxHost",
    "Vi Host": "ViHost",
    "Cloud Director Host": "CloudDirectorHost"
}

restore_mode = {
    "Original Location": "OriginalLocation",
    "Customized": "Customized"
}

virus_detection_action = {
    "Disable Network": "DisableNetwork",
    "Abort Recovery": "AbortRecovery",
    "Ignore": "Ignore"
}

repo_type = {
    "Win Local": "WinLocal",
    "Linux Local": "WinLocal",
    "Smb": "Smb",
    "Nfs": "Nfs",
    "Azure Blob": "AzureBlob",
    "Azure Data Box": "AzureDataBox",
    "Azure Archive": "AzureArchive",
    "Amazon S3": "AmazonS3",
    "Amazon Snowball Edge": "AmazonSnowballEdge",
    "Amazon S3 Glacier": "AmazonS3Glacier",
    "S3 Compatible": "S3Compatible",
    "Google Cloud": "GoogleCloud",
    "IBM Cloud": "IBMCloud",
    "Extendable Repository": "ExtendableRepository",
    "DD Boost": "DDBoost",
    "ExaGrid": "ExaGrid",
    "HP Store Once Integration": "HPStoreOnceIntegration",
    "Quantum": "Quantum",
    "Wasabi Cloud": "WasabiCloud",
    "Linux Hardened": "LinuxHardened",
    "Infinidat": "Infinidat",
    "Fujitsu": "Fujitsu"
}

platform_name = {
    "VMware": "VMware",
    "HyperV": "HyperV",
    "Cloud Director": "CloudDirector",
    "Windows Physical": "WindowsPhysical",
    "Linux Physical": "LinuxPhysical",
    "Tape": "Tape",
    "Custom Platform": "CustomPlatform",
    "Entra ID": "EntraID",
    "Unstructured Data": "UnstructuredData",
    "Test": "Test"
}
