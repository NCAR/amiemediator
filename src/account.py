from amieparms import (AMIEParmDescAware, process_parms)

class CreateAccount(AMIEParmDescAware,dict):

    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'site_grant_key',
            'ProjectID',
            'PersonID',
            'Resource',
        ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            ['ProjectID', 'site_grant_key'],
            'PersonID',
            'Resource',
            ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``create_account()``"""
        dict.__init__(self, **kwargs)

class InactivateAccount(AMIEParmDescAware,dict):

    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'Comment',
            'PersonID',
            'ProjectID',
            'Resource',
        ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'PersonID',
            'ProjectID',
            'Resource',
            ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``inactivate_account()``"""
        dict.__init__(self, **kwargs)


class ReactivateAccount(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'Comment',
            'PersonID',
            'ProjectID',
            'Resource',
        ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'PersonID',
            'ProjectID',
            'Resource',
            ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``reactivate_account()``"""
        dict.__init__(self, **kwargs)


class NotifyUser(AMIEParmDescAware,dict):

    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'BusinessPhoneNumber',
            'Email',
            'Email',
            'PersonID',
            'ProjectID',
            'RemoteSiteLogin',
            'Resource',
            'Username',
        ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'ProjectID',
            'PersonID',
            'RemoteSiteLogin',
            'Resource',
            ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``notify_user()``"""
        dict.__init__(self, **kwargs)
