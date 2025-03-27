from amieparms import (AMIEParmDescAware, process_parms)

class LookupProjectTask(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'RecordID',
            ],
        required=[
            'RecordID',
            ])
    def __init__(self, *args, **kwargs):
        """Validate, filter, and transform arguments to ``lookup_project_task()``"""
        dict.__init__(self, **kwargs)

class LookupLocalFos(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'PfosNumber',
            ],
        required=[
            'PfosNumber',
            ])
    def __init__(self, *args, **kwargs):
        """Validate, filter, and transform arguments to ``lookup_local_fos()``"""
        dict.__init__(self, **kwargs)

class ChooseOrAddLocalFos(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'Abstract',
            'GrantNumber',
            'PfosNumber',
            'ProjectTitle',
            'PiDepartment',
            ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'PfosNumber',
            ])
    def __init__(self, *args, **kwargs):
        """Validate, filter, and transform arguments to ``choose_local_fos()``"""
        dict.__init__(self, **kwargs)

class LookupProjectNameBase(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'BoardType',
            'ChargeNumber',
            'GrantNumber',
            'GrantType',
            'NsfStatusCode',
            'PfosNumber',
            'PiCity',
            'PiCountry',
            'PiPersonID',
            'PiOrganization',
            'PiOrgCode',
            'PiState',
            'ProjectID',
            'ProjectTitle',
            'site_org',
            'site_grant_key',
            ],
        required=[
            'GrantNumber',
            'PfosNumber',
            'PiOrganization',
            ['PiOrgCode', 'site_org'],
            'site_grant_key',
            ])
    def __init__(self, *args, **kwargs):
        """Validate, filter, and transform arguments to ``lookup_project_name_base()``"""
        dict.__init__(self, **kwargs)

class ChooseOrAddProjectNameBase(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'BoardType',
            'ChargeNumber',
            'GrantNumber',
            'GrantType',
            'NsfStatusCode',
            'PiCity',
            'PiCountry',
            'PfosNumber',
            'PiPersonID',
            'PiOrganization',
            'PiOrgCode',
            'PiState',
            'ProjectID',
            'ProjectTitle',
            'site_grant_key',
            'site_org',
            ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'GrantNumber',
            'PfosNumber',
            'PiOrganization',
            'PiOrgCode',
            'site_grant_key',
            ])
    def __init__(self, *args, **kwargs):
        """Validate, filter, and transform arguments to ``choose_or_add_project_name_base()``"""
        dict.__init__(self, **kwargs)
    

class CreateProject(AMIEParmDescAware,dict):

    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'local_fos',
            'project_name_base',
            'site_grant_key',
            'site_org',
            'Abstract',
            'AllocatedResource',
            'BoardType',
            'ChargeNumber',
            'EndDate',
            'GrantNumber',
            'GrantType',
            'NsfStatusCode',
            'PfosNumber',
            'PiPersonID',
            'ProjectID',
            'ProjectTitle',
            'RecordID',
            'RemoteSiteLogin',
            'Resource',
            'RoleList',
            'ServiceUnitsAllocated',
            'Sfos',
            'StartDate',
            ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',
            
            'local_fos',
            'project_name_base',
            'site_grant_key',
            'EndDate',
            'GrantNumber',
            'PfosNumber',
            'PiPersonID',
            'RemoteSiteLogin',
            'Resource',
            'ServiceUnitsAllocated',
            'StartDate',
            ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``create_project()``"""
        dict.__init__(self, **kwargs)


class InactivateProject(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',
            
            'site_grant_key',
            'GrantNumber',
            'AllocatedResource',
            'Comment',
            'EndDate',
            'ProjectID',
            'Resource',
            'ServiceUnitsAllocated',
            'ServiceUnitsRemaining',
            'StartDate',
        ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'ProjectID',
            'Resource',
            ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``inactivate_project()``"""
        dict.__init__(self, **kwargs)

class ReactivateProject(AMIEParmDescAware,dict):
    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',
            
            'GrantNumber',
            'AllocatedResource',
            'Comment',
            'EndDate',
            'PiPersonID',
            'ProjectID',
            'Resource',
            'ServiceUnitsAllocated',
            'ServiceUnitsRemaining',
            'StartDate',
        ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'ProjectID',
            'Resource',
            ])
    def __init__(self, *args, **kwargs) -> dict:
        """Validate, filter, and transform arguments to ``reactivate_project()``"""
        dict.__init__(self, **kwargs)

