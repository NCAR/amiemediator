ITC_CANCEL_RPC_PKT_1 = {
    'DATA_TYPE': 'Packet',
    'type': 'inform_transaction_complete',
    'header': {
        'packet_rec_id': 174709748,
        'packet_id': 2,
        'transaction_id': 244207,
        'trans_rec_id': 87139098,
        'expected_reply_list': [
            {
                'type': 'data_project_create',
                'timeout': 30240
            }
        ],
        'local_site_name': 'PSC',
        'remote_site_name': 'SDSC',
        'originating_site_name': 'SDSC',
        'outgoing_flag': False,
        'transaction_state': 'in-progress',
        'packet_state': 'in-progress',
        'packet_timestamp': '2021-08-24T14:47:55.600Z',
        'in_reply_to': 174709746
    },
    'body': {
        'DetailCode': 99,
        'Message': 'Cancelled',
        'StatusCode': 99,
    },
}

ITC_CANCEL_RPC_PKT_2 = {
    'DATA_TYPE': 'Packet',
    'type': 'inform_transaction_complete',
    'header': {
        'packet_rec_id': 174709749,
        'packet_id': 2,
        'transaction_id': 244208,
        'trans_rec_id': 87139099,
        'expected_reply_list': [
            {
                'type': 'data_project_create',
                'timeout': 30240
            }
        ],
        'local_site_name': 'PSC',
        'remote_site_name': 'SDSC',
        'originating_site_name': 'SDSC',
        'outgoing_flag': False,
        'transaction_state': 'in-progress',
        'packet_state': 'in-progress',
        'packet_timestamp': '2021-08-24T14:47:56.600Z',
        'in_reply_to': 174709747
    },
    'body': {
        'DetailCode': 99,
        'Message': 'Cancelled',
        'StatusCode': 99,
    },
}
