from packethandler import PacketHandler
from misctypes import DateTime
from taskstatus import TaskStatus
from miscfuncs import truthy
import handler.subtasks as sub

class RequestAccountCreate(PacketHandler, packet_type="request_account_create"):

    def work(self, apacket):
        """Handle a "request_account_create" packet

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
        org_code = apacket.get('org_code',None)
        if org_code is None:
            ts = sub.define_org_code(spa, apacket,'User')
            if ts:
                return ts
        org_code = apacket['org_code']
        
        person_id = apacket.get('person_id',None)
        if person_id is None:
            ts = sub.define_person(spa, apacket,'User')
            if ts:
                return ts
        person_id = apacket['person_id']
        site_org = apacket['site_org']
        apacket['PersonID'] = person_id

        person_active = apacket.get('person_active',False)
        if not person_active:
            ts = sub.activate_person(spa, apacket,'User')
            if ts:
                return ts
        person_active = apacket['person_active']

        remote_site_login = apacket.get('remote_site_login',False)
        if not remote_site_login:
            ts = sub.define_account(spa, apacket,'User')
            if ts:
                return ts
        remote_site_login = apacket['remote_site_login']
        account_activity_time = apacket['account_activity_time']
        project_id = apacket['project_id']

        user_notified = apacket.get('user_notified', None)
        if user_notified is None:
            ts = sub.notify_user(spa, apacket)
            if ts:
                return ts
        
        nac = apacket.create_reply_packet()
        ad = apacket.get('AcademicDegree',None)
        if ad:
            nac.AcademicDegree = ad
        nac.ResourceList = apacket['ResourceList']
        nac.UserFirstName = apacket['UserFirstName']
        nac.UserLastName = apacket['UserLastName']
        nac.UserOrganization = apacket['UserOrganization']
        nac.UserOrgCode = apacket['UserOrgCode']
        
        nac.AccountActivityTime = account_activity_time
        nac.ProjectID = project_id
        nac.UserPersonID = person_id
        nac.UserRemoteSiteLogin = remote_site_login

        return nac
