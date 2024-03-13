from amieparms import (AMIEParmDescAware, process_parms)

class ModifyUser(AMIEParmDescAware,dict):
    """
    A class used when modifying a user
    """

    @process_parms(
        allowed=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'ActionType',
            'AcademicDegree',
            'BusinessPhoneComment',
            'BusinessPhoneExtension',
            'BusinessPhoneNumber',
            'CitizenshipList',
            'City',
            'Country',
            'Department',
            'DnList',
            'Email',
            'FirstName',
            'HomePhoneComment',
            'HomePhoneExtension',
            'HomePhoneNumber',
            'LastName',
            'MiddleName',
            'NsfStatusCode',
            'Organization',
            'OrgCode',
            'PersonID',
            'State',
            'StreetAddress',
            'StreetAddress2',
            'Title',
            'Zip',
            ],
        required=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'timestamp',
            
            'ActionType',
            'PersonID',
            ])
    def __init__(self, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``modify_user()``"""
        dict.__init__(self, **kwargs)
