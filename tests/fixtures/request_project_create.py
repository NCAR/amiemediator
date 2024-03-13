RPC_PKT_1 = {
    'DATA_TYPE': 'Packet',
    'type_id': 7,
    'type': 'request_project_create',
    'header': {
        'expected_reply_list': [
            {'type': 'data_project_create', 'timeout': 30240}
        ],
        'packet_id': 2,
        'trans_rec_id': 87139098,
        'transaction_id': 244207,
        'packet_rec_id': 174709746,
        'local_site_name': 'PSC',
        'remote_site_name': 'SDSC',
        'originating_site_name': 'SDSC',
        'outgoing_flag': False,
        'transaction_state': 'in-progress',
        'packet_state': 'in-progress',
        'packet_timestamp': '2021-08-24T14:47:52.600Z',
    },
    'body': {
        'Abstract': 'Investigate something',
        'AcademicDegree': [
            {'Field': 'Computer and Computation Research', 'Degree': 'MS'}
        ],
        'AllocatedResource': 'comet-gpu.sdsc.xsede',
        'AllocationType': 'new',
        'EndDate': '2022-09-30T23:59:59Z',
        'GrantNumber': 'IRI120015',
        'NsfStatusCode': 'GS',
        'PfosNumber': 21,
        'PiCity': 'Pittsburgh',
        'PiCountry': '9US',
        'PiDepartment': 'SCS',
        'PiEmail': 'vraunak@andrew.cmu.edu',
        'PiFirstName': 'Vikas',
        'PiGlobalID': '71691',
        'PiLastName': 'Raunak',
        'PiMiddleName': '',
        'PiOrgCode': '0032425',
        'PiOrganization': 'Carnegie Mellon University',
        'PiState': 'PA',
        'PiStreetAddress': 'Craig Street, Carnegie Mellon University, Pittsburgh 15213',
        'PiTitle': '',
        'PiZip': '15213',
        'PiBusinessPhoneNumber': '4124781149',
        'PiRequestedLoginList': [''],
        'RecordID': 12345,
        'ResourceList': ['comet-gpu.sdsc.xsede'],
        'ServiceUnitsAllocated': 20000,
        'StartDate': '2021-10-01T00:00:00Z',
        }
    }

RPC_PKT_2 = {
    'DATA_TYPE': 'Packet',
    'type_id': 7,
    'type': 'request_project_create',
    'header': {
        'expected_reply_list': [
            {'type': 'data_project_create', 'timeout': 30240}
        ],
        'packet_id': 3,
        'trans_rec_id': 87139099,
        'transaction_id': 244208,
        'packet_rec_id': 174709747,
        'local_site_name': 'PSC',
        'remote_site_name': 'SDSC',
        'originating_site_name': 'SDSC',
        'outgoing_flag': False,
        'transaction_state': 'in-progress',
        'packet_state': 'in-progress',
        'packet_timestamp': '2021-08-24T15:47:52.600Z',
    },
    'body': {
        'Abstract': 'Investigate something interesting',
        'AcademicDegree': [
            {'Field': 'Computer and Computation Research', 'Degree': 'MS'}
        ],
        'AllocatedResource': 'comet-gpu.sdsc.xsede',
        'AllocationType': 'new',
        'EndDate': '2022-09-30T23:59:59Z',
        'GrantNumber': 'IRI120015',
        'NsfStatusCode': 'GS',
        'PfosNumber': 21,
        'PiCity': 'Pittsburgh',
        'PiCountry': '9US',
        'PiDepartment': 'SCS',
        'PiEmail': 'vraunak@andrew.cmu.edu',
        'PiFirstName': 'Vikas',
        'PiGlobalID': '71691',
        'PiLastName': 'Raunak',
        'PiMiddleName': '',
        'PiOrgCode': '0032425',
        'PiOrganization': 'Carnegie Mellon University',
        'PiState': 'PA',
        'PiStreetAddress': 'Craig Street, Carnegie Mellon University, Pittsburgh 15213',
        'PiTitle': '',
        'PiZip': '15213',
        'PiBusinessPhoneNumber': '4124781149',
        'PiRequestedLoginList': [''],
        'RecordID': 12345,
        'ResourceList': ['comet-gpu.sdsc.xsede'],
        'ServiceUnitsAllocated': 20000,
        'StartDate': '2021-10-01T00:00:00Z',
        }
    }

RPC_PKT_SCENARIO_RPR = {
    "DATA_TYPE": "Packet",
    "type": "request_project_create",
    "header": {
        "expected_reply_list": [
            {
                "type": "notify_project_create",
                "timeout": 30240
            }
        ],
        "packet_id": 1,
        "trans_rec_id": 116811798,
        "transaction_id": 20897,
        "remote_site_name": "NCAR",
        "local_site_name": "TGCDB",
        "originating_site_name": "TGCDB",
        "outgoing_flag": 1,
        "packet_rec_id": 233441576,
        "packet_timestamp": "2023-08-03T20:34:45.920Z",
        "client_state": None,
        "packet_state": "in-progress",
        "client_json": None,
        "transaction_state": "in-progress"
    },
    "body": {
        "AllocationType": "new",
        "BoardType": "Startup",
        "RequestType": "new",
        "Abstract": "Lorem ipsum dolor est...",
        "ChargeNumber": "TG-NNT237423",
        "GrantNumber": "NNT237423",
        "ProposalNumber": "NNT237423",
        "PfosNumber": "21000",
        "PiGlobalID": "32657",
        "PiBusinessPhoneNumber": "7202352981",
        "PiEmail": "jll1062+xsede@phys.psu.edu",
        "PiCity": "University Park",
        "PiStreetAddress": "Department of Physics",
        "PiStreetAddress2": "104 Davey Lab, Box 166",
        "PiZip": "16802",
        "PiState": "PA",
        "PiCountry": "9US",
        "PiFirstName": "Justin",
        "PiMiddleName": "",
        "PiLastName": "Lanfranchi",
        "PiDepartment": "Physics",
        "PiTitle": "",
        "PiOrganization": "Pennsylvania State University",
        "PiOrgCode": "0088138",
        "NsfStatusCode": "GS",
        "PiDnList": [
            "/C=US/O=National Center for Supercomputing Applications/CN=Justin Lanfranchi",
            "/C=US/O=Pittsburgh Supercomputing Center/CN=Justin Lanfranchi"
        ],
        "SitePersonId": [
            {
                "Site": "XD-ALLOCATIONS",
                "PersonID": "lanfranj"
            },
            {
                "Site": "X-PORTAL",
                "PersonID": "lanfranj"
            }
        ],
        "AcademicDegree": [
            {
                "Degree": "BS",
                "Field": "Engineering"
            }
        ],
        "ProjectTitle": "Lorem Ipsum",
        "RecordID": "XRAS-110809-test-resource1.ncar.xsede",
        "Sfos": [
            {
                "Number": "0"
            }
        ],
        "StartDate": "2023-08-03",
        "EndDate": "2024-08-03",
        "ServiceUnitsAllocated": "1",
        "ResourceList": [
            "test-resource1.ncar.xsede"
        ],
        "PiRequestedLoginList": [
            "lanfranj"
        ],
        "AllocatedResource": "test-resource1.ncar.xsede"
    }
}
