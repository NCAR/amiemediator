from abc import (ABC, abstractmethod)
import importlib
import logging
from amieclient.packet.base import Packet as AMIEPacket
from logdumper import LogDumper
from misctypes import DateTime
from miscfuncs import to_expanded_string
from amieparms import (get_packet_keys, strip_key_prefix)
from spexception import (ServiceProviderRequestFailed, ServiceProviderError)
from serviceprovider import (ServiceProvider, SPSession)
from organization import AMIEOrg
from person import AMIEPerson
from taskstatus import (TaskStatus, TaskStatusList)
from actionablepacket import ActionablePacket
import handler

    
class PacketHandlerError(Exception):
    pass

class ServiceProviderAdapter(object):
    def __init__(self):
        self.logger = logging.getLogger("handler")
        self.logdumper = LogDumper(self.logger)

    def _get_task_by_method_name(self, method_name, apacket):
        sp = SPSession.get_service_provider()
        task_name = sp.get_local_task_name(method_name, apacket)
        if task_name is None:
            task = dict(packet_dict)
            task['client'] = 'AMIE'
            task['task_name'] = method_name
            task['task_state'] = 'nascent'
            task['timestamp'] = int(DateTime.now().timestamp()*1000)
            ts = TaskStatus(task)
            ts.fail("Unsupported operation")
            task['products'] = ts['products']
            return ts
        task_list = apacket['tasks']
        ts = task_list.get(task_name)
        if ts is None:
            ts = self._create_new_task(task_name, apacket)

        return ts

    def _create_new_task(self, task_name, apacket) -> TaskStatus:
            
        jid, atrid, pid = get_packet_keys(apacket)
        ts_parms = {
            'amie_packet_type': apacket['amie_packet_type'],
            'job_id': jid,
            'amie_transaction_id': apacket['amie_transaction_id'],
            'amie_packet_id': apacket['amie_packet_id'],
            'task_name': task_name,
            'timestamp': int(DateTime.now().timestamp()*1000),
            'task_state': 'nascent',
            }
        ts = TaskStatus(**ts_parms)
        apacket.add_or_update_task(ts)
        return ts

    def _init_task_data(self, ts, apacket, prefix=None) -> dict:
        if prefix is not None:
            apdata = strip_key_prefix(prefix, apacket)
        else:
            apdata = apacket.copy()
        apdata['task_name'] = ts['task_name']
        return apdata

    def clear_transaction(self, apacket):
        """Clean up task data associated with a packet
        
        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: An AMIEOrg object or None
        """

        transaction_id = apacket.get('amie_transaction_id',None)

        with SPSession() as sp:
            sp.clear_transaction(transaction_id)
        return

    def lookup_org(self, apacket, prefix) -> AMIEOrg:
        """Get the AMIEOrg object for the packet
        
        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: The prefix string to strip from keys ("User" or "Pi").
        :type prefix: str
        :return: An AMIEOrg object or None
        """

        request_data = strip_key_prefix(prefix,apacket)

        amie_org = None
        with SPSession() as sp:
            amie_org = sp.lookup_org(request_data)
        return amie_org
        
    def choose_or_add_org(self, apacket, prefix) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.choose_or_add_org()

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: The prefix string to strip from keys ("User" or "Pi").
        :type prefix: str
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include OrgCode
        """

        ts = self._get_task_by_method_name("choose_or_add_org",apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket, prefix)

            with SPSession() as sp:
                ts = sp.choose_or_add_org(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def lookup_person(self, apacket, prefix) -> AMIEPerson:
        """Get the AMIEPerson object for the packet
        
        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: The prefix string to strip from keys ("User" or "Pi").
        :type prefix: str
        :return: An AMIEPerson object or None
        """

        request_data = strip_key_prefix(prefix,apacket)
        amie_person = None
        with SPSession() as sp:
            amie_person = sp.lookup_person(request_data)
        return amie_person

    def choose_or_add_person(self, apacket, prefix) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.choose_or_add_person()

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: The prefix string to strip from keys ("User" or "Pi").
        :type prefix: str
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include PersonID
        """

        ts = self._get_task_by_method_name("choose_or_add_person", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket, prefix)
            request_data['person_role'] = prefix

            with SPSession() as sp:
                ts = sp.choose_or_add_person(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        state = ts['task_state']
        if state == "successful":
            person_id = ts.get_product_value('PersonID')
            lcprefix = prefix.lower()
            person_key = lcprefix + "_person_id"
            apacket[person_key] = person_id
        return ts

    def update_person_DNs(self, apacket, prefix) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.update_person_DNs()

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: The prefix string to strip from keys ("User" or "Pi").
        :type prefix: str
        :return: A TaskStatus object from the ServiceProvider task.
        """

        ts = self._get_task_by_method_name("update_person_DNs", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket, prefix)

            with SPSession() as sp:
                ts = sp.update_person_DNs(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def activate_person(self, apacket, prefix) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.activate_person()

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: The prefix string to strip from keys ("User" or "Pi").
        :type prefix: str
        :return: A TaskStatus object from the ServiceProvider task. Final
            Products on success must include PersonID and active
        """

        ts = self._get_task_by_method_name("activate_person", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket, prefix)
            request_data['person_role'] = prefix

            with SPSession() as sp:
                ts = sp.activate_person(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        state = ts['task_state']
        if state == "successful":
            active = ts.get_product_value('active')
            apacket['person_active'] = active
        return ts

    def lookup_grant(self, apacket) -> str:
        """Get the site_grant_key for the packet
        
        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: site_grant_key string
        """

        site_grant_key = None
        with SPSession() as sp:
            site_grant_key = sp.lookup_grant(apacket)
        return site_grant_key
        
    def choose_or_add_grant(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.choose_or_add_grant()

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include site_grant_key
        """

        ts = self._get_task_by_method_name("choose_or_add_grant", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)
            request_data['PiPersonID'] = apacket['pi_person_id']

            with SPSession() as sp:
                ts = sp.choose_or_add_grant(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def lookup_local_fos(self, apacket) -> str:
        """Get the locally-defined FoS equivalent for the given FosNumber

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: local_fos string
        """

        local_fos = None
        with SPSession() as sp:
            local_fos = sp.lookup_local_fos(apacket)
        return local_fos

    def choose_or_add_local_fos(self, apacket) -> str:
        """Get the TaskStatus object from SP.choose_or_add_local_fos

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include local_fos
        """

        ts = self._get_task_by_method_name("choose_or_add_local_fos", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)

            with SPSession() as sp:
                ts = sp.choose_or_add_local_fos(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def lookup_project_name_base(self, apacket) -> str:
        """Get the base name for a new project

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: local_fos string
        """

        project_name_base = None
        with SPSession() as sp:
            project_name_base = sp.lookup_project_name_base(apacket)
        return project_name_base

    def choose_or_add_project_name_base(self, apacket) -> str:
        """Get the TaskStatus object from SP.choose_or_add_project_name_base

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task Final
        Products on success must include project_name_base
        """

        ts = self._get_task_by_method_name("choose_or_add_project_name_base",
                                           apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)

            with SPSession() as sp:
                ts = sp.choose_or_add_project_name_base(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

        
    def create_project(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.create_project()

        Create a Project with the given PiPersonID, and optionally create
        an allocation for the associated resource.

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include ProjectID
        """

        ts = self._get_task_by_method_name("create_project", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)
            request_data['PiPersonID'] = apacket['pi_person_id']

            with SPSession() as sp:
                ts = sp.create_project(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def inactivate_project(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.inactivate_project()

        Inactivate a Project

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include ProjectID
        """

        ts = self._get_task_by_method_name("inactivate_project", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)

            with SPSession() as sp:
                ts = sp.inactivate_project(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def reactivate_project(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.reactivate_project()

        (Re)activate a Project

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
            Products on success must include ProjectID
        """

        ts = self._get_task_by_method_name("reactivate_project", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)

            with SPSession() as sp:
                ts = sp.reactivate_project(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def create_account(self, apacket, prefix=None) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.create_account()

        Create an account (a person-project association)

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: If given, a prefix string to strip from keys ("User" or
            "Pi").
        :type prefix: str, optional
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include RemoteSiteLogin
        """

        ts = self._get_task_by_method_name("create_account", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket, prefix)
            project_id = apacket.get('ProjectID',None)
            if project_id is None:
                request_data['ProjectID'] = apacket['project_id']

            with SPSession() as sp:
                ts = sp.create_account(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def inactivate_account(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.inactivate_account()

        Inactivate an account

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include RemoteSiteLogin
        """

        ts = self._get_task_by_method_name("inactivate_account", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)

            with SPSession() as sp:
                ts = sp.inactivate_account(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def reactivate_account(self, apacket, prefix=None) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.reactivate_account()

        Reactivate an account

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :param prefix: If given, a prefix string to strip from keys ("User" or
            "Pi").
        :type prefix: str, optional
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include RemoteSiteLogin
        """

        ts = self._get_task_by_method_name("reactivate_account", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket, prefix)
            request_data['task_name'] = task_name

            with SPSession() as sp:
                ts = sp.reactivate_account(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def update_allocation(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.update_allocation()

        Add or update an allocation

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include ServiceUnitsAllocations, StartDate,
        and EndDate
        """

        ts = self._get_task_by_method_name("update_allocation", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)
            request_data['ProjectID'] = apacket['project_id']

            with SPSession() as sp:
                ts = sp.update_allocation(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def modify_user(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.modify_user()

        Modify a User

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include modify_user_status
        """

        ts = self._get_task_by_method_name("modify_user", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)

            with SPSession() as sp:
                ts = sp.modify_user(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def merge_person(self, apacket) -> TaskStatus:
        """Get the TaskStatus object from ServiceProvider.merge_person()

        Merge two persons

        :param apacket: An "ActionablePacket"
        :type apacket: dict 
        :return: A TaskStatus object from the ServiceProvider task. Final
        Products on success must include PersonID and/or GlobalID
        """

        ts = self._get_task_by_method_name("merge_person", apacket)
        if ts['task_state'] == 'nascent':
            request_data = self._init_task_data(ts, apacket)

            with SPSession() as sp:
                ts = sp.merge_person(**request_data)
            apacket.add_or_update_task(ts)

        self._check_task_status_for_errors(ts)
        return ts

    def _check_task_status_for_errors(self, ts):
        state = ts['task_state']
        if state == "failed":
            message = ts.get_product_value('FAILED')
            raise ServiceProviderRequestFailed(message)
        elif state == "errored":
            message = ts.get_product_value('ERRORED')
            raise ServiceProviderError(message)
        return


_handler_map = {}

class PacketHandler(ABC):
    
    def __init_subclass__(cls, packet_type, **kwargs):
        super().__init_subclass__(**kwargs)
        handler = cls()
        cls.singleton = handler
        _handler_map[packet_type] = handler

    @classmethod
    def initialize_handlers(cls):
        for pkg in handler.__all__:
            mod = importlib.import_module('.'+pkg,'handler')
        DefaultHandler()

    @classmethod
    def get_handler(cls, packet_type):
        handler = _handler_map.get(packet_type,None)
        if handler is None:
            handler = DefaultHandler.singleton
        return handler

    def __init__(self):
        """Object that handles ServiceProvider interactions for an Packet"""

        super().__init__()
        self.logger = logging.getLogger("handler")
        self.logdumper = LogDumper(self.logger)
        self.sp_adapter = ServiceProviderAdapter()

    @abstractmethod
    def work(self, actionable_packet):
        """Do all that can be done with a packet without waiting

        Interact with the service provider to process a packet. Continue until
        there is a reply packet to send to the AMIE server, or until the
        service provider returns a :class:`~taskstatus.TaskStatus` object with
        a state of ``queued`` or ``in-progress``.

        All concrete ``PacketHandler`` subclasses must implement this method.

        All subclass implementations must use the
        :class:`~packethandler.ServiceProviderAdapter`
        class to interact with the Service Provider via the ``self.sp_adapter``
        attribute.

        :param actionable_packet: all data associated with the packet
        :type actionable_packet: ActionablePacket

        :return: A TaskStatus object in a non-end state, or a reply AMIE Packet
        """
        pass

class DefaultHandler(PacketHandler, packet_type="DEFAULT"):

    def initial_transaction_packet(self):
        return True

    def work(self, apacket):
        """Handle an unsupported packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: An InformationTransactionComplete Packet with a failure
        """

        packet = apacket['amie_packet']
        pt = packet.__class__._packet_type
        msg = f"{pt} not implemented"
        rp = ActionablePacket.create_failure_reply(packet, message=msg)
        return rp

