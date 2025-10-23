from packethandler import PacketHandler
from misctypes import DateTime
from taskstatus import TaskStatus
from miscfuncs import (truthy, to_expanded_string)

def define_org_code(spa, apacket, prefix):
    amie_org = spa.lookup_org(apacket,prefix)
    if amie_org is None:
        org_ts = spa.choose_or_add_org(apacket, prefix)
        if org_ts['task_state'] == "successful":
            org_code = org_ts.get_product_value('OrgCode')
        else:
            return org_ts
    else:
        org_code = amie_org['OrgCode']
    apacket['org_code'] = org_code
    return None

def define_person(spa, apacket, prefix):
    amie_person = spa.lookup_person(apacket,prefix)
    if amie_person is None:
        spa.logdumper.debug("define_person: apacket=",apacket)
        person_ts = spa.choose_or_add_person(apacket, prefix)
        if person_ts['task_state'] == "successful":
            person_id = person_ts.get_product_value('PersonID')
            site_org = person_ts.get_product_value('site_org')
            person_active = person_ts.get_product_value('active')
        else:
            return person_ts
    else:
        person_id = amie_person['PersonID']
        username = amie_person['RemoteSiteLogin']
        site_org = amie_person.get('site_org',None)
        person_active = amie_person['active']
            
    spa.logdumper.debug("define_person: amie_person=",amie_person)
    apacket['person_id'] = person_id
    apacket['RemoteSiteLogin'] = username
    apacket['PersonID'] = person_id
    apacket['site_org'] = site_org
    apacket['person_active'] = truthy(person_active)
    return None
    
def update_person_DNs(spa, apacket, prefix):
    spa.logdumper.debug("update_person_DNs: apacket=", apacket)
    updn_ts = spa.update_person_DNs(apacket, prefix)
    if updn_ts['task_state'] == "successful":
        return None
    else:
        return updn_ts

def activate_person(spa, apacket, prefix):
    person_active = truthy(apacket.get('person_active','0'))
    if not person_active:
        spa.logdumper.debug("activate_person: prefix="+prefix+" apacket=",
                            apacket)
        active_ts = spa.activate_person(apacket, prefix)
        if active_ts['task_state'] == "successful":
            person_active = active_ts.get_product_value('active')
        else:
            return active_ts

    spa.logger.debug("activate_person: person_active="+person_active)
    apacket['person_active'] = person_active
    return None
    
def merge_person(spa, apacket):
    spa.logdumper.debug("merge_person: apacket=", apacket)
    merge_ts = spa.merge_person(apacket)
    if merge_ts['task_state'] == "successful":
        return None
    else:
        return merge_ts

def define_contract_number(spa, apacket):
    contract_number = spa.lookup_contract_number(apacket)
    if contract_number is None:
        spa.logdumper.debug("define_contract_number: apacket=", apacket)
        cts = spa.choose_or_add_contract_number(apacket)
        if cts['task_state'] == "successful":
            contract_number = cts.get_product_value('contract_number')
        else:
            return cts
    spa.logger.debug("define_contract_number contract_number="+contract_number)
    apacket['contract_number'] = contract_number
    return None

def define_local_fos(spa, apacket):
    local_fos = spa.lookup_local_fos(apacket)
    if local_fos is None:
        spa.logdumper.debug("define_local_fos: apacket=", apacket)
        lf_ts = spa.choose_or_add_local_fos(apacket)
        if lf_ts['task_state'] == "successful":
            local_fos = lf_ts.get_product_value('areaOfInterest')
        else:
            return lf_ts
    spa.logger.debug("define_local_fos local_fos="+local_fos)
    apacket['local_fos'] = local_fos
    return None

def lookup_project_by_grant_number(spa, apacket):
    spa.logdumper.debug("lookup_project_by_grant_number: apacket=", apacket)
    project_id = spa.lookup_project_by_grant_number(apacket)
    if project_id:
        apacket['project_id'] = project_id
    return project_id

def define_project_name_base(spa, apacket):
    project_name_base = spa.lookup_project_name_base(apacket)
    if project_name_base is None:
        spa.logdumper.debug("define_project_name_base: apacket=", apacket)
        pnb_ts = spa.choose_or_add_project_name_base(apacket)
        if pnb_ts['task_state'] == "successful":
            project_name_base = pnb_ts.get_product_value('project_name_base')
        else:
            return pnb_ts
    spa.logger.debug("define_project_name_base project_name_base="+\
                     project_name_base)
    apacket['project_name_base'] = project_name_base
    return None

def define_project(spa, apacket):
    spa.logdumper.debug("define_project: apacket=", apacket)
    project_ts = spa.create_project(apacket)
    if project_ts['task_state'] == "successful":
        project_id = project_ts.get_product_value('ProjectID')
        service_units_allocated = project_ts.get_product_value('ServiceUnitsAllocated')
        start_date = project_ts.get_product_value('StartDate')
        end_date = project_ts.get_product_value('EndDate')
        remote_site_login = project_ts.get_product_value('PiRemoteSiteLogin')
    else:
        return project_ts
    apacket['project_id'] = project_id
    apacket['service_units_allocated'] = service_units_allocated
    apacket['start_date'] = start_date
    apacket['end_date'] = end_date
    apacket['remote_site_login'] = remote_site_login

def lookup_project_task(spa, apacket):
    spa.logdumper.debug("lookup_project_task: apacket=", apacket)
    ts = spa.lookup_project_task(apacket)
    if ts:
        apacket['PiPersonID'] = ts.get_product_value('PiPersonID')
        apacket['PiRemoteSiteLogin'] = ts.get_product_value('PiRemoteSiteLogin')
        apacket['ProjectID'] = ts.get_product_value('ProjectID')
        apacket['ServiceUnitsAllocated'] = \
                                   ts.get_product_value('ServiceUnitsAllocated')
        apacket['StartDate'] = ts.get_product_value('StartDate')
        apacket['EndDate'] = ts.get_product_value('EndDate')
    return ts
        

def define_account(spa, apacket, prefix):
    remote_site_login = apacket.get('remote_site_login',None)
    if not remote_site_login:
        spa.logdumper.debug("define_account: prefix="+prefix+" apacket=",
                            apacket)
        account_ts = spa.create_account(apacket,prefix)
        if account_ts['task_state'] == "successful":
            remote_site_login = \
                account_ts.get_product_value('RemoteSiteLogin')
            account_activity_time = \
                account_ts.get_product_value('AccountActivityTime')
            project_id = \
                account_ts.get_product_value('ProjectID')
        else:
            return account_ts
    spa.logger.debug("define_account remote_site_login="+remote_site_login)
    apacket['remote_site_login'] = remote_site_login
    apacket['account_activity_time'] = account_activity_time
    apacket['project_id'] = project_id

def define_allocation(spa, apacket):
    spa.logdumper.debug("define_allocation: apacket=", apacket)
    alloc_ts = spa.update_allocation(apacket)
    if alloc_ts['task_state'] == "successful":
        service_units_allocated = \
            alloc_ts.get_product_value('ServiceUnitsAllocated')
        start_date = \
            alloc_ts.get_product_value('StartDate')
        end_date = \
            alloc_ts.get_product_value('EndDate')
        resource_name = \
            alloc_ts.get_product_value('resource_name')
    else:
        return alloc_ts
    apacket['service_units_allocated'] = service_units_allocated
    apacket['start_date'] = start_date
    apacket['end_date'] = end_date
    apacket['resource_name'] = resource_name

def modify_user(spa, apacket):
    spa.logdumper.debug("modify_user: apacket=", apacket)
    user_ts = spa.modify_user(apacket)
    if user_ts['task_state'] == "successful":
        return None
    else:
        return user_ts

def notify_user(spa, apacket):
    spa.logdumper.debug("notify_user: apacket=", apacket)
    notify_ts = spa.notify_user(apacket)
    if notify_ts['task_state'] == "successful":
        return None
    else:
        return notify_ts
