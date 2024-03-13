RAC_PKT_1 = {
    'DATA_TYPE': 'Packet',
    'type_id': 16,
    'type': 'request_account_create',
    'header': {
        'expected_reply_list': [
            {'type': 'notify_account_create', 'timeout': 30240}
        ],
        'packet_id': 1,
        'trans_rec_id': 87139097,
        'transaction_id': 244206,
        'packet_rec_id': 174709745,
        'local_site_name': 'PSC',
        'remote_site_name': 'SDSC',
        'originating_site_name': 'SDSC',
        'outgoing_flag': False,
        'transaction_state': 'in-progress',
        'packet_state': None,
        'packet_timestamp': '2021-08-24T14:47:51.507Z',
    },
    'body': {
        'AcademicDegree': [
            {'Field': 'Computer and Computation Research', 'Degree': 'MS'}
        ],
        'SitePersonId': [
            {'PersonID': 'vraunak', 'Site': 'X-PORTAL'},
            {'PersonID': 'vraunak', 'Site': 'XD-ALLOCATIONS'},
            {'PersonID': 'RAUNAK12P', 'Site': 'PSC'},
            {'PersonID': '112157', 'Site': 'SDSC'}
        ],
        'RoleList': ['allocation_manager'],
        'UserDnList': [
            '/C=US/O=Pittsburgh Supercomputing Center/CN=Vikas Raunak',
            '/C=US/O=National Center for Supercomputing Applications/CN=Vikas Raunak'
        ],
        'UserPersonID': '112157',
        'NsfStatusCode': 'GS',
        'UserOrgCode': '0032425',
        'UserOrganization': 'Carnegie Mellon University',
        'UserTitle': '',
        'UserDepartment': 'SCS',
        'UserLastName': 'Raunak',
        'UserMiddleName': '',
        'UserFirstName': 'Vikas',
        'UserCountry': '9US',
        'UserState': 'PA',
        'UserZip': '15213',
        'UserStreetAddress': 'Craig Street, Carnegie Mellon University, Pittsburgh 15213',
        'UserCity': 'Pittsburgh',
        'UserEmail': 'vraunak@andrew.cmu.edu',
        'UserBusinessPhoneNumber': '4124781149',
        'UserGlobalID': '71691',
        'UserFavoriteColor': 'blue',
        'AllocatedResource': 'comet-gpu.sdsc.xsede',
        'UserRequestedLoginList': [''],
        'ResourceList': ['comet-gpu.sdsc.xsede'],
        'UserPasswordAccessEnable': '1',
        'GrantNumber': 'IRI120015',
        'ProjectID': 'CMU139'
        }
    }
