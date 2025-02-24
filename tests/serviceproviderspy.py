from serviceprovider import ServiceProviderIF
from fixtures.request_account_create import RAC_PKT_1
from fixtures.request_project_create import RPC_PKT_1
from misctypes import DateTime
from taskstatus import TaskStatus
from organization import AMIEOrg
from person import AMIEPerson
from project import Project

class ServiceProvider(ServiceProviderIF):
    def __init__(self):
        self.args = {}
        self.test_data = {
        }
        self.default_data = {
            'lookup_org_result': {
                'City': "Pittsbugh",
                'Country': "9US",
                'OrgCode': "0032425",
                'Organization': "Carnegie Mellon University",
                'State': "PA",
            },
            'lookup_person_result': {
                'PersonID': '12345',
                'GlobalID': '71691',
                'FirstName': 'Vikas',
                'LastName': 'Raunak',
                'MiddleName': '',
            },
            'lookup_grant_result': "IRI120015",
            ],
        }

    def create_task_status(self, task_name=None, task_state='queued',
                           products=[], **kwargs):
        if task_name is None:
            task_name = kwargs['task_name']
        ts_parms = {
            'amie_packet_type': kwargs['amie_packet_type'],
            'amie_transaction_id': kwargs['amie_transaction_id'],
            'amie_packet_id': kwargs['amie_packet_id'],
            'job_id': kwargs['job_id'],
            'task_name': task_name,
            'task_state': task_state,
            'timestamp': DateTime.now(),
            'products': products,
            }
        return TaskStatus(ts_parms)

    def set_test_data(self, name, data):
        self.test_data[name] = data

    def clear_test_data(self, name):
        self.test_data[name] = {}
    
    def apply_config(self, config):
        self.args['apply_config'] = config

    def get_tasks(self, active=True, wait=None, since=None) -> list:
        self.args['get_tasks'] = {
            'active': active,
            'wait': wait,
            'since': since
        }
        return []

    def clear_transaction(self, amie_transaction_id):
        self.args['clear_transaction'] = amie_transaction_id

    def lookup_org(self, *args, **kwargs) -> AMIEOrg:
        self.args['lookup_org'] = kwargs
        if 'lookup_org_result' in self.test_data:
            parms = self.test_data['lookup_org_result']
        else:
            parms = self.default_data['lookup_org_result']
        if parms is not None:
            return AMIEOrg(**parms)
        return None

    def choose_or_add_org(self, *args, **kwargs) -> TaskStatus:
        self.args['choose_or_add_org'] = kwargs
        if 'choose_or_add_org_result' in self.test_data:
            parms = kwargs | self.test_data['choose_or_add_org_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def lookup_person(self, *args, **kwargs) -> AMIEPerson:
        self.args['lookup_person'] = kwargs
        if 'lookup_person_result' in self.test_data:
            parms = self.test_data['lookup_person_result']
        else:
            parms = self.default_data['lookup_person_result']
        if parms is not None:
            return AMIEPerson(**parms)
        return None

    def choose_or_add_person(self, *args, **kwargs) -> TaskStatus:
        self.args['choose_or_add_person'] = kwargs
        if 'choose_or_add_person_result' in self.test_data:
            parms = kwargs | self.test_data['choose_or_add_person_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def activate_person(self, *args, **kwargs) -> TaskStatus:
        self.args['activate_person'] = kwargs
        if 'activate_person_result' in self.test_data:
            parms = kwargs | self.test_data['activate_person_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def lookup_grant(self, *args, **kwargs) -> str:
        self.args['lookup_grant'] = kwargs
        if 'lookup_grant_result' in self.test_data:
            val = self.test_data['lookup_grant_result']
        else:
            val = self.default_data['lookup_grant_result']
        return val
    
    def choose_or_add_grant(self, *args, **kwargs) -> TaskStatus:
        self.args['choose_or_add_grant'] = kwargs
        if 'choose_or_add_grant_result' in self.test_data:
            parms = kwargs | self.test_data['choose_or_add_grant_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def lookup_local_fos(self, *args, **kwargs) -> str:
        self.args['lookup_local_fos'] = kwargs
        if 'lookup_local_fos_result' in self.test_data:
            val = self.test_data['lookup_local_fos_result']
        else:
            val = self.default_data['lookup_local_fos_result']
        return val
    
    def choose_or_add_local_fos(self, *args, **kwargs) -> TaskStatus:
        self.args['choose_or_add_local_fos'] = kwargs
        if 'choose_or_add_local_fos' in self.test_data:
            parms = kwargs | self.test_data['choose_or_add_local_fos']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def lookup_project_name_base(self, *args, **kwargs) -> str:
        self.args['lookup_project_name_base'] = kwargs
        if 'lookup_project_name_base_result' in self.test_data:
            val = self.test_data['lookup_project_name_base_result']
        else:
            val = self.default_data['lookup_project_name_base_result']
        return val
    
    def choose_or_add_project_name_base(self, *args, **kwargs) -> TaskStatus:
        self.args['choose_or_add_project_name_base'] = kwargs
        if 'choose_or_add_project_name_base_result' in self.test_data:
            parms = kwargs | self.test_data['choose_or_add_project_name_base']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def create_project(self, *args, **kwargs) -> TaskStatus:
        self.args['create_project'] = kwargs
        if 'create_project_result' in self.test_data:
            parms = kwargs | self.test_data['create_project_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def inactivate_project(self, *args, **kwargs) -> TaskStatus:
        self.args['inactivate_project'] = kwargs
        if 'inactivate_project_result' in self.test_data:
            parms = kwargs | self.test_data['inactivate_project_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def reactivate_project(self, *args, **kwargs) -> TaskStatus:
        self.args['reactivate_project'] = kwargs
        if 'reactivate_project_result' in self.test_data:
            parms = kwargs | self.test_data['reactivate_project_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def create_account(self, *args, **kwargs) -> TaskStatus:
        self.args['create_account'] = kwargs
        if 'create_account_result' in self.test_data:
            parms = kwargs | self.test_data['create_account_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def inactivate_account(self, *args, **kwargs) -> TaskStatus:
        self.args['inactivate_account'] = kwargs
        if 'inactivate_account_result' in self.test_data:
            parms = kwargs | self.test_data['inactivate_account_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def reactivate_account(self, *args, **kwargs) -> TaskStatus:
        self.args['reactivate_account'] = kwargs
        if 'reactivate_account_result' in self.test_data:
            parms = kwargs | self.test_data['reactivate_account_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def update_allocation(self, **kwargs) -> TaskStatus:
        self.args['update_allocation'] = kwargs
        if 'update_allocation_result' in self.test_data:
            parms = kwargs | self.test_data['update_allocation_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def modify_user(self, **kwargs) -> TaskStatus:
        self.args['modify_user'] = kwargs
        if 'modify_user' in self.test_data:
            parms = kwargs | self.test_data['modify_user_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def merge_person(self, **kwargs) -> TaskStatus:
        self.args['merge_person'] = kwargs
        if 'merge_person' in self.test_data:
            parms = kwargs | self.test_data['merge_person_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)

    def notify_user(self, **kwargs) -> TaskStatus:
        self.args['notify_user'] = kwargs
        if 'notify_user' in self.test_data:
            parms = kwargs | self.test_data['notify_user_result']
        else:
            parms = kwargs
        return self.create_task_status(**parms)


