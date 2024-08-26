from amieparms import (AMIEParmDescAware, strip_key_prefix, process_parms)


class AMIEOrg(AMIEParmDescAware,dict):
    """
    A class used to describe operations on AMIE's concept of an
    'organization'.
    """

    @process_parms(
        allowed=[
            'OrgCode',
            'Organization',
            'StreetAddress',
            'StreetAddress2',
            'City',
            'State',
            'Country',
            'Zip',
            ],
        required=[
            'OrgCode',
            'Organization',
            ])
    def __init__(self, *args, **kwargs):
        """lookup_org() result object

        The site client implementation should use this to create the result of
        lookup_org().
        """

        dict.__init__(self,**kwargs)

class LookupOrg(AMIEParmDescAware,dict):
        
    @process_parms(
        allowed=[
            'OrgCode',
        ],
        required=[
            'OrgCode',
        ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``lookup_org()``"""
        return dict.__init__(self,**kwargs)

class ChooseOrAddOrg(AMIEParmDescAware,dict):
    """
    A class used when specifying an organization that will be known to AMIE
    """

    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',
            
            'City',
            'Country',
            'Organization',
            'OrgCode',
            'State',
            ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            ['OrgCode','Organization'],
            ])
    def __init__(self, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``choose_or_add_org()``"""
        dict.__init__(self, **kwargs)

