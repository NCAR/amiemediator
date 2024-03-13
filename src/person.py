from amieparms import (AMIEParmDescAware, process_parms)

class AMIEPerson(AMIEParmDescAware,dict):
    """
    A class used to describe operations on AMIE's concept of an
    'person'.
    """

    @process_parms(
        allowed=[
            'PersonID',
            'GlobalID',
            'active',
            'FirstName',
            'MiddleName',
            'LastName',
            'Email',
            'AcademicDegree',
            'BusinessPhoneComment',
            'BusinessPhoneExtension',
            'BusinessPhoneNumber',
            'CitizenshipList',
            'City',
            'Country',
            'Department',
            'Fax',
            'HomePhoneComment',
            'HomePhoneExtension',
            'HomePhoneNumber',
            'Organization',
            'OrgCode',
            'RemoteSiteLogin',
            'State',
            'StreetAddress',
            'StreetAddress2',
            'Title',
            'Username',
            'site_org',
            'Zip',
            ],
        required=[
            'PersonID',
            ['FirstName','LastName'],
            ])
    def __init__(self, *args, **kwargs):
        """lookup_person() result object

        The site client implementation should use this to create the result of
        lookup_person().
        """

        dict.__init__(self,**kwargs)

class LookupPerson(AMIEParmDescAware,dict):
        
    @process_parms(
        allowed=[
            'PersonID',
            'GlobalID',
        ],
        required=[
        ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``lookup_person()``"""
        return dict.__init__(self,**kwargs)

class ChooseOrAddPerson(AMIEParmDescAware,dict):
    """
    A class used when specifying a local person who will be known to AMIE
    """

    @process_parms(
        allowed=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'AcademicDegree',
            'BusinessPhoneComment',
            'BusinessPhoneExtension',
            'BusinessPhoneNumber',
            'CitizenshipList',
            'City',
            'Country',
            'Department',
            'Email',
            'FirstName',
            'GlobalID',
            'HomePhoneComment',
            'HomePhoneExtension',
            'HomePhoneNumber',
            'LastName',
            'MiddleName', 
            'Organization',
            'OrgCode',
            'SitePersonID',
            'State',
            'Title',
            'RemoteSiteLogin',
            'RequestedLoginList',
            ],
        required=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            ['FirstName', 'LastName'],
            'Organization',
            ])
    def __init__(self, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``choose_or_add_person()``"""
        dict.__init__(self, **kwargs)

class ActivatePerson(AMIEParmDescAware,dict):
    """
    A class used when specifying a local person to activate
    """

    @process_parms(
        allowed=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'Email',
            'FirstName',
            'GlobalID',
            'LastName',
            'MiddleName', 
            'PersonID',
            'SitePersonID',
            'RemoteSiteLogin',
            ],
        required=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'PersonID',
            ])
    def __init__(self, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``activate_person()``"""
        dict.__init__(self, **kwargs)

class MergePerson(AMIEParmDescAware,dict):
    """
    A class used when specifying person records to merge
    """

    @process_parms(
        allowed=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'KeepGlobalID',
            'DeleteGlobalID',
            'KeepPersonID',
            'DeletePersonID',
            'KeepPortalLogin',
            'DeletePortalLogin',
            ],
        required=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'KeepGlobalID',
            'DeleteGlobalID',
            'KeepPersonID',
            'DeletePersonID',
            ])
    def __init__(self, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``merge_person()``"""
        dict.__init__(self, **kwargs)

