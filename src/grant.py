from amieparms import (AMIEParmDescAware, process_parms)

class LookupGrant(AMIEParmDescAware,dict):
        
    @process_parms(
        allowed=[
            'GrantNumber',
        ],
        required=[
            'GrantNumber',
        ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``lookup_grant()``"""
        return dict.__init__(self,**kwargs)

class ChooseOrAddGrant(AMIEParmDescAware,dict):
    """
    A class used when specifying a GrantNumber known to AMIE
    """

    @process_parms(
        allowed=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'GrantNumber',
            'GrantType',
            'PfosNumber',
            'local_fos',
            'PiPersonID',
            'PiFirstName',
            'PiLastName',
            'PiDepartment',
            'ProjectTitle',
            'StartDate',
            'EndDate',
            ],
        required=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'GrantNumber',
            'PfosNumber',
            'PiPersonID',
            'PiFirstName',
            'PiLastName',
            'StartDate',
            'EndDate',
            ])
    def __init__(self, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``choose_or_add_grant()``"""
        dict.__init__(self, **kwargs)

