import logging
from packethandler import PacketHandler
from misctypes import DateTime
from taskstatus import TaskStatus
from miscfuncs import truthy
import handler.subtasks as sub

class RequestProjectCreate(PacketHandler, packet_type="request_project_create"):

    def work(self, apacket):
        """Handle a "request_project_create" packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """

        spa = self.sp_adapter

        #
        # The lower-case parameters we collect initially (e.g. "person_id",
        # "org_code", etc) represent the dynamic state of this request. The
        # first time work() is called, none of these "dynamic state" parameters
        # will be defined. On re-entry to work(), it is possible that some or
        # all or them will be defined.
        #

        # We want to check up front for RecordID
        recordID = apacket.get('RecordID',None)
        if recordID is not None:
            ts = sub.lookup_project_task(spa, apacket)
            if ts:
                npc = build_reply(apacket)
                return npc
        
        org_code = apacket.get('org_code',None)
        if org_code is None:
            ts = sub.define_org_code(spa, apacket, 'Pi')
            if ts:
                return ts
        org_code = apacket['org_code']
        
        person_id = apacket.get('person_id',None)
        if person_id is None:
            ts = sub.define_person(spa, apacket,"Pi")
            if ts:
                return ts
        person_id = apacket['person_id']
        site_org = apacket['site_org']
        person_active = apacket.get('person_active',False)
        apacket['PersonID'] = person_id
        apacket['pi_person_id'] = person_id

        if not person_active:
            ts = sub.activate_person(spa, apacket, "Pi")
            if ts:
                return ts
        person_active = apacket['person_active']

        site_grant_key = apacket.get('site_grant_key',None)
        if site_grant_key is None:
            ts = sub.define_site_grant_key(spa, apacket)
            if ts:
                return ts
        site_grant_key = apacket['site_grant_key']

        allocation_type = apacket['AllocationType']
#        if allocation_type == "new" or allocation_type == "renewal":
#            local_fos = apacket.get('local_fos',None)
#            if local_fos is None:
#                ts = sub.define_local_fos(spa, apacket)
#                if ts:
#                    return ts
#            local_fos = apacket['local_fos']
#
#        if allocation_type == "new":
#            project_name_base = apacket.get('project_name_base',None)
#            if project_name_base is None:
#                ts = sub.define_project_name_base(spa, apacket)
#                if ts:
#                    return ts
#            project_name_base = apacket['project_name_base']
#                
#            project_id = apacket.get('project_id',None)
#            if project_id is None:
#                ts = sub.define_project(spa, apacket)
#                if ts:
#                    return ts
#            project_id = apacket['project_id']
#            service_units_allocated = apacket.get('service_units_allocated',None)
#            start_date = apacket['start_date']
#            end_date = apacket['end_date']
#            remote_site_login = apacket['remote_site_login']
#
#        else:
#            project_id = apacket.get('ProjectID',apacket['project_id'])
#            service_units_allocated = apacket.get('service_units_allocated',None)
#            if service_units_allocated is None:
#                ts = sub.define_allocation(spa, apacket)
#                if ts:
#                    return ts
#            service_units_allocated = apacket['service_units_allocated']
#            start_date = apacket['start_date']
#            end_date = apacket['end_date']

        local_fos = apacket.get('local_fos',None)
        if local_fos is None:
            ts = sub.define_local_fos(spa, apacket)
            if ts:
                return ts
        local_fos = apacket['local_fos']
        project_name_base = apacket.get('project_name_base',None)
        if project_name_base is None:
            ts = sub.define_project_name_base(spa, apacket)
            if ts:
                return ts
        project_name_base = apacket['project_name_base']
            
        project_id = apacket.get('project_id',None)
        if project_id is None:
            ts = sub.define_project(spa, apacket)
            if ts:
                return ts
        service_units_allocated = apacket.get('service_units_allocated',None)
        start_date = apacket['start_date']
        end_date = apacket['end_date']
        remote_site_login = apacket['remote_site_login']

        user_notified = apacket.get('user_notified',None)
        if not truthy(user_notified):
            ts = sub.notify_user(spa, apacket)
            if ts:
                return ts
        
        npc = build_reply(apacket)
        return npc

    def build_reply(self,apacket):
        npc = apacket.create_reply_packet()
        npc.GrantNumber = apacket['GrantNumber']
        npc.PfosNumber = apacket['PfosNumber']
        npc.PiOrgCode = apacket['PiOrgCode']
        npc.ProjectTitle = apacket['ProjectTitle']
        npc.ResourceList = apacket['ResourceList']

        npc.PiPersonID = apacket['PiPersonID']
        npc.PiRemoteSiteLogin = apacket['PiRemoteSiteLogin']
        npc.ProjectID = apacket['ProjectID']
        npc.ServiceUnitsAllocated = float(apacket['ServiceUnitsAllocated'])
        npc.StartDate = DateTime(apacket['StartDate']).datetime()
        npc.EndDate = DateTime(apacket['EndDate']).datetime()

        return npc
