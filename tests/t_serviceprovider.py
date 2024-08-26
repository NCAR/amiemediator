#!/usr/bin/env python
import unittest
from amieparms import (transform_value,AMIEParmDescAware)
from fixtures.request_account_create import RAC_PKT_1
from fixtures.request_project_create import RPC_PKT_1
from misctypes import DateTime
from amieparms import strip_key_prefix
from taskstatus import TaskStatus
from organization import AMIEOrg
from person import AMIEPerson
from project import Project
import serviceproviderspy
from serviceprovider import (ServiceProviderIF, ServiceProvider)

    
class TestServiceProvider(unittest.TestCase):
    def setUp(self):
        self.config = {
            'package': '',
            'module': 'serviceproviderspy',
            }
        
    def test_constructor(self):
        sp = ServiceProvider()

        self.assertTrue(isinstance(sp,ServiceProvider),
                        msg='constructor failed')
        self.assertTrue(hasattr(sp,'implem'),
                                msg='implem attr not created')
        self.assertEqual(sp.implem,None,
                                msg='implem attr not None')

    def test_apply_config(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        
        self.assertTrue(isinstance(sp.implem,
                                   serviceproviderspy.ServiceProvider),
                        msg='config did not set implem')
        

    def test_get_tasks(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        l = sp.get_tasks()
        args = spi.args['get_tasks']
        self.assertTrue(isinstance(l,list),
                        msg='get_tasks did not return list')
        self.assertTrue('active' in args,
                        msg='active arg not passed')
        self.assertEqual(args['active'],True,
                        msg='active arg default not True')
        self.assertTrue('wait' in args,
                        msg='wait arg not passed')
        self.assertEqual(args['wait'],None,
                        msg='wait arg default not None')
        self.assertTrue('since' in args,
                        msg='since arg not passed')
        self.assertEqual(args['since'],None,
                        msg='since arg default not None')

        l = sp.get_tasks(active=False)
        args = spi.args['get_tasks']
        self.assertTrue('active' in args,
                        msg='active arg not passed')
        self.assertEqual(args['active'],False,
                        msg='wait arg not set')

        l = sp.get_tasks(wait=10)
        args = spi.args['get_tasks']
        self.assertTrue('wait' in args,
                        msg='wait arg not passed')
        self.assertEqual(args['wait'],10,
                        msg='wait arg not set')

        l = sp.get_tasks(since='2023-01-01T00:00:00Z')
        args = spi.args['get_tasks']
        self.assertTrue('since' in args,
                        msg='since arg not passed')
        self.assertEqual(args['since'],'2023-01-01T00:00:00Z',
                        msg='since arg not set')

    def test_lookup_org(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        org = strip_key_prefix('User',RAC_PKT_1['body'])
        o = sp.lookup_org(**org)
        args = spi.args['lookup_org']
        self.assertEqual(args['OrgCode'],org['OrgCode'],
                         msg='unprefixed OrgCode not passed on')

    def test_choose_or_add_org(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        org = strip_key_prefix('User',RAC_PKT_1['body'])
        self._add_task_info(org)
        ts = sp.choose_or_add_org(org)
        args = spi.args['choose_or_add_org']
        self.assertEqual(args['OrgCode'],org['OrgCode'],
                         msg='unprefixed OrgCode not passed on')

    def test_lookup_person(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        account_person = strip_key_prefix('User',RAC_PKT_1['body'])
        ap = sp.lookup_person(**account_person)
        args = spi.args['lookup_person']
        self.assertEqual(args['PersonID'],account_person['PersonID'],
                         msg='unprefixed PersonID not passed on')

    def test_choose_or_add_person(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        account_person = strip_key_prefix('User',RAC_PKT_1['body'])
        self._add_task_info(account_person)
        ts = sp.choose_or_add_person(**account_person)
        args = spi.args['choose_or_add_person']
        self.assertEqual(args['FirstName'],account_person['FirstName'],
                         msg='unprefixed FirstName not passed on')

    def test_activate_person(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        account_person = strip_key_prefix('User',RAC_PKT_1['body'])
        self._add_task_info(account_person)
        ts = sp.activate_person(**account_person)
        args = spi.args['activate_person']
        self.assertEqual(args['PersonID'],account_person['PersonID'],
                         msg='unprefixed PersonID not passed on')


    def test_lookup_grant(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        req = RPC_PKT_1['body']
        ap = sp.lookup_grant(**req)
        args = spi.args['lookup_grant']
        self.assertEqual(args['GrantNumber'],req['GrantNumber'],
                         msg='GrantNumber not passed on')

    def test_choose_or_add_grant(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        req = RPC_PKT_1['body'].copy()
        req['PiPersonID'] = 'vraunak'
        self._add_task_info(req)
        ts = sp.choose_or_add_grant(**req)
        args = spi.args['choose_or_add_grant']
        self.assertEqual(args['GrantNumber'],req['GrantNumber'],
                         msg='GrantNumber not passed on')

    def test_lookup_local_fos(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        req = RPC_PKT_1['body']
        ap = sp.lookup_local_fos(**req)
        args = spi.args['lookup_local_fos']
        self.assertEqual(args['local_fos'],req['local_fos'],
                         msg='local_fos not passed on')

    def test_choose_local_fos(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        req = RPC_PKT_1['body'].copy()
        self._add_task_info(req)
        ts = sp.choose_local_fos(**req)
        args = spi.args['choose_local_fos']
        self.assertEqual(args['local_fos'],req['local_fos'],
                         msg='local_fos not passed on')

    def test_lookup_project_name_base(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        req = RPC_PKT_1['body']
        ap = sp.lookup_local_fos(**req)
        args = spi.args['lookup_project_name_base']
        self.assertEqual(args['project_name_base'],req['project_name_base'],
                         msg='project_name_base not passed on')

    def test_choose_or_project_name_base(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        req = RPC_PKT_1['body'].copy()
        self._add_task_info(req)
        ts = sp.choose_or_add_project_name_base(**req)
        args = spi.args['choose_or_add_project_name_base']
        self.assertEqual(args['project_name_base'],req['project_name_base'],
                         msg='project_name_base not passed on')

    def test_create_project(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        pi_person_id = RAC_PKT_1['body']['UserPersonID']
        proj = RPC_PKT_1['body'].copy()
        proj['PiPersonID'] = pi_person_id
        proj['site_grant_key'] = "IRI120015"
        self._add_task_info(proj)
        ap = sp.create_project(proj)
        args = spi.args['create_project']
        self.assertEqual(args['PiPersonID'],proj['PiPersonID'],
                         msg='PiPersonID not passed in')
        self.assertEqual(args['site_grant_key'],proj['site_grant_key'],
                         msg='site_grant_key not passed in')


    def test_inactivate_project(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        proj = RPC_PKT_1['body'].copy()
        proj['ProjectID'] = 'UFOO00100';
        proj['site_grant_key'] = "IRI120015"
        self._add_task_info(proj)
        ap = sp.inactivate_project(proj)
        args = spi.args['inactivate_project']
        self.assertEqual(args['ProjectID'],proj['ProjectID'],
                         msg='ProjectID not passed in')
        self.assertEqual(args['ServiceUnitsAllocated'],
                         proj['ServiceUnitsAllocated'],
                         msg='ServiceUnitsAllocated not passed in')

    def test_reactivate_project(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        proj = RPC_PKT_1['body'].copy()
        proj['ProjectID'] = 'UFOO00100'
        proj['site_grant_key'] = "IRI120015"
        self._add_task_info(proj)
        ap = sp.activate_project(proj)
        args = spi.args['reactivate_project']
        self.assertEqual(args['ProjectID'],proj['ProjectID'],
                         msg='ProjectID not passed in')
        self.assertEqual(args['ServiceUnitsAllocated'],
                         proj['ServiceUnitsAllocated'],
                         msg='ServiceUnitsAllocated not passed in')

    def test_create_account(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        account_person = strip_key_prefix('User',RAC_PKT_1['body'])
        self._add_task_info(account_person)
        ts = sp.create_account(account_person)
        args = spi.args['create_account']
        
        self.assertEqual(args['ProjectID'], account_person['ProjectID'],
                         msg='ProjectID not passed in')
        self.assertEqual(args['PersonID'], account_person['PersonID'],
                         msg='PersonID not passed in')
        self.assertEqual(args['ResourceList'], account_person['ResourceList'],
                         msg='ResourceList not passed in')


    def test_inactivate_account(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        account_person = strip_key_prefix('User',RAC_PKT_1['body'])
        account_person['ProjectID'] = 'UFOO00100'
        self._add_task_info(account_person)
        ts = sp.inactivate_account(account_person)
        args = spi.args['inactivate_account']
        self.assertEqual(args['PersonID'], account_person['PersonID'],
                         msg='PersonID not passed in')
        self.assertEqual(args['ProjectID'], account_person['ProjectID'],
                         msg='ProjectID not passed in')

    def test_reactivate_account(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        account_person = strip_key_prefix('User',RAC_PKT_1['body'])
        account_person['ProjectID'] = 'UFOO00100'
        self._add_task_info(account_person)
        ts = sp.reactivate_account(account_person)
        args = spi.args['reactivate_account']
        self.assertEqual(args['PersonID'], account_person['PersonID'],
                         msg='PersonID not passed in')
        self.assertEqual(args['ProjectID'], account_person['ProjectID'],
                         msg='ProjectID not passed in')


    def test_update_allocation(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        proj = RPC_PKT_1['body'].copy()
        proj['ProjectID'] = 'UFOO00100';
        self._add_task_info(proj)
        ap = sp.update_allocation(proj)
        args = spi.args['update_allocation']
        self.assertEqual(args['ProjectID'],proj['ProjectID'],
                         msg='ProjectID not passed in')
        self.assertEqual(args['ServiceUnitsAllocated'],
                         proj['ServiceUnitsAllocated'],
                         msg='ServiceUnitsAllocated not passed in')

    def test_modify_user(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        rec = RPC_PKT_1['body'].copy()
        self._add_task_info(rec)
        ap = sp.modify_user(rec)
        args = spi.args['modify_user']
        self.assertEqual(args['PersonID'],rec['PersonID'],
                         msg='PersonID not passed in')

    def test_merge_person(self):
        sp = ServiceProvider()
        sp.apply_config(self.config)
        spi = sp.implem
        rec = {
            'KeepGlobalID': "12345",
            'KeepPersonID': "gooduser",
            'DeleteGlobalID': "23456",
            'DeletePerson': "baduser",
            }
        self._add_task_info(rec)
        ap = sp.modify_user(rec)
        args = spi.args['merge_person']
        self.assertEqual(args['KeepGlobalID'],rec['KeepGlobalID'],
                         msg='KeepGlobalID not passed in')
        self.assertEqual(args['KeepPersonID'],rec['KeepPersonID'],
                         msg='KeepPersonID not passed in')
        self.assertEqual(args['DeleteGlobalID'],rec['DeleteGlobalID'],
                         msg='DeleteGlobalID not passed in')
        self.assertEqual(args['DeletePersonID'],rec['DeletePersonID'],
                         msg='DeletePersonID not passed in')

    def _add_task_info(self, parms):
        parms['job_id'] = 'atid:pid'
        parms['amie_transaction_id'] = 'atid'
        parms['amie_packet_id'] = 'pid'
        parms['task_name'] =  'mytask'

        
if __name__ == '__main__':
    unittest.main()
