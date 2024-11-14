import importlib
from abc import (ABC, abstractmethod)
import logging
from requests.exceptions import (ConnectionError, Timeout)
from spexception import *
from amieclient.packet.base import Packet as AMIEPacket
from retryingproxy import RetryingServiceProxy
from amieparms import (AMIEParmDescAware, process_parms)
from miscfuncs import to_expanded_string
from misctypes import (DateTime, TimeUtil)
from taskstatus import TaskStatus
from organization import (AMIEOrg, LookupOrg, ChooseOrAddOrg)
from person import (AMIEPerson, LookupPerson, ChooseOrAddPerson, ActivatePerson,
                    MergePerson, UpdatePersonDNs)
from grant import (LookupGrant, ChooseOrAddGrant)
from project import (LookupLocalFos, ChooseOrAddLocalFos,
                     LookupProjectNameBase, ChooseOrAddProjectNameBase,
                     CreateProject, InactivateProject, ReactivateProject)
from account import (CreateAccount, InactivateAccount, ReactivateAccount)
from allocation import UpdateAllocation
from user import ModifyUser


class ServiceProviderIF(ABC):
    """
    Site Service Provider Interface - the Abstract Base Class for the
    local site's allocation/accounting service.

    A working AMIEMediator implementation will always have at least two
    concrete implementations of this base class.

    A "facade" implementation is what the top-level code interacts with.
    See ``serviceprovider.ServiceProvider``. The facade class
    handles parameter filtering and validation, and delegates the real work
    to the *other* ServiceProviderIF concrete subclass.

    The other ServiveProviderIF subclass is specified in the application
    configuration. It handles the details specific to the local site.

    Note that the amiemediator code proper does not itself maintain persistent
    state; it relies on the remote AMIE service to maintain persistent state
    for AMIE packets, and on the local ServiceProvider implementation to
    maintain persistent state for any tasks submitted to it. At run time,
    the mediator code (see :class:`~mediator.AMIEMediator`) queries the
    ServiceProvider for its task data using the get_tasks() method, and this
    task data is expected to carry sufficient state for all other
    ServiceProvider methods. (But see description of "snapshots" in
    ``packetmanager.PacketManager``.)
    """

    @abstractmethod
    def apply_config(self, config):
        """Apply "localsite" configuration
        """
        
        pass

    @abstractmethod
    def get_local_task_name(self, method_name, *args, **kwargs) -> str:
        """Return the local task name for the given request

        :param method_name: The name of a ServiceProvider method that
            requires a task
        :type method_name: str
        :param args: See ServiceProvider method
        :type args: list
        :param kwargs: See ServiceProvider method
        :type kwargs: dict
        
        :raises ServiceProviderError: if no implementation is configured
        :return: The task name, or None if the operation is not supported
        """

        pass
        
    @abstractmethod
    def get_tasks(self, active=True, wait=None, since=None) -> list:
        """Get all TaskStatus objects
        
        Note that this is the only Service Provider operation that might
        wait for data before returning. See the ``wait`` parameter.

        :param active: If False, "cleared" tasks are included. Default is true.
            "Active" implies that the task has not yet been "cleared".
        :type active: bool, optional
        :param wait: If given, the maximum number of seconds to wait for
            updates. If None or not given, the method should return immediately
            if there is no new data.
        :type wait: int, optional
        :param since: If given, only return information for tasks that have
            been updated since the indicated time
        :param since: DateTime, optional
        :raises ServiceProviderTimeout: if a request times out
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A list of TaskStatus objects
        """

        pass

    @abstractmethod
    def clear_transaction(self, amie_transaction_id):
        """Clean up task data associated with a packet

        :param amie_transaction_id: A string that uniquely identifies an AMIE
            transaction
        :type amie_transaction_id: str
        """
        
        pass

    @abstractmethod
    def lookup_org(self, *args, **kwargs) -> AMIEOrg:
        """Lookup a single established "AMIE" organization

        This is useful for sites that have their own database of organizations
        that must be reconciled with the AMIE OrgCode. If a site does not need
        to do this, the service provider can simply returned the input
        parameters in the form of an AMIEOrg object.
        
        Refer to :class:`~organization.LookupOrg` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A AMIEOrg object describing a single organization or None if
                 no organization is found
        """
        
        pass

    @abstractmethod
    def choose_or_add_org(self, *args, **kwargs) -> TaskStatus:
        """Choose an existing organization person or create a new one

        Given an organization description, either choose a known organization
        or create a new one. This is useful for sites that have their own
        database of organizations that must be reconciled with the AMIE OrgCode.

        Refer to :class:`~organization.ChooseOrAddOrg` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include a "org_code" product
        """

        pass

    @abstractmethod
    def lookup_person(self, *args, **kwargs) -> AMIEPerson:
        """Lookup a single established "AMIE" person

        Refer to :class:`~person.LookupPerson` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A AMIEPerson object describing a single person
        """

        pass

    @abstractmethod
    def choose_or_add_person(self, *args, **kwargs) -> TaskStatus:
        """Choose an existing local person or create a new person

        Given a person description, either choose an existing local persons or
        create one. Ensure that person has a PersonID that will be made known
        to AMIE, and that the person is active.

        Refer to :class:`~person.ChooseOrAddPerson` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include a "PersonID" product
        """

        pass

    @abstractmethod
    def update_person_DNs(self, *args, **kwargs) -> TaskStatus:
        """Activate an existing local person

        Given the description, including a PersonID, of an existing but
        inactive person, ensure the person is active.

        Refer to :class:`~person.UpdatePersonDNs` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object
        """

        pass

    @abstractmethod
    def activate_person(self, *args, **kwargs) -> TaskStatus:
        """Activate an existing local person

        Given the description, including a PersonID, of an existing but
        inactive person, ensure the person is active.

        Refer to :class:`~person.ActivatePerson` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include "PersonID" and
            "active" products
        """

        pass

    @abstractmethod
    def lookup_local_fos(self, *args, **kwargs) -> str:
        """Look up the locally-defined "field of science"

        Refer to :class:`~project.LookupLocalFos` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A ``local_fos`` string
        """

        pass
    
    @abstractmethod
    def choose_or_add_local_fos(self, *args, **kwargs) -> TaskStatus:
        """Choose a locally-defined "field of science"

        Refer to :class:`~project.ChooseOrAddLocalFos` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include a "local_fos"
        product.
        """

        pass

    @abstractmethod
    def lookup_grant(self, *args, **kwargs) -> str:
        """Lookup a single established "Grant" or equivalent object

        Refer to :class:`~grant.LookupGrant` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A ``site_grant_key`` string
        """
        
        pass
    
    @abstractmethod
    def choose_or_add_grant(self, *args, **kwargs) -> TaskStatus:
        """Choose an existing grant/contract or create a new one

        Given a GrantNumber, select a local grant/contact object or create
        a new one.

        Refer to :class:`~grant.ChooseOrAddGrant` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include a "site_grant_key"
            product
        """

        pass
 
    @abstractmethod
    def lookup_project_name_base(self, *args, **kwargs) -> str:
        """Look up the base name for a new project

        Refer to :class:`~project.LookupProjectNameBase` for parameter
        info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A "project_name_base" string.
        """

        pass
   
    @abstractmethod
    def choose_or_add_project_name_base(self, *args, **kwargs) -> TaskStatus:
        """Choose a base name for a new project, or create a new one

        If the local site implements project identifiers as "smart keys" (i.e.
        names/keys with project metadata embedded in the value), this method
        provides a means to finalize the definition of relevant metadata
        objects used by the project name. For example, at NCAR, project codes
        include short keys that identifies the facility and organization
        of the project's PI; NCAR's implementation of this method ensures that
        these short codes are defined properly.
        
        Refer to :class:`~project.ChooseOrAddProjectNameBase` for parameter
        info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include a
            "project_name_base" product.
        """

        pass
    
    @abstractmethod
    def create_project(self, *args, **kwargs) -> TaskStatus:
        """Create a new project and allocation and activate the PI

        If the project or allocation already exist, just ensure that everything
        is active.
        
        Refer to :class:`~project.CreateProject` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include "ProjectId",
            "PiPersonID", "resource_name", "ServiceUnitsAllocated",
            "StartDate", "EndDate", and "PiRemoteSiteLogin" products.
        """

        pass

    @abstractmethod
    def inactivate_project(self, *args, **kwargs) -> TaskStatus:
        """Inactivate a project
        
        Refer to :class:`~project.InactivateProject` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include "ProductId" product
        """

        pass

    @abstractmethod
    def reactivate_project(self, *args, **kwargs) -> TaskStatus:
        """Reactivate a project
        
        Refer to :class:`~project.ReactivateProject` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include "ProjectId" product
        """

        pass

    @abstractmethod
    def create_account(self, *args, **kwargs) -> TaskStatus:
        """Create new association between a Person and a Project
        
        Refer to :class:`~account.CreateAccount` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include AccountActivityTime,
            ProjectID, PersonID, "resource_name", and RemoteSiteLogin products
        """

        pass

    @abstractmethod
    def inactivate_account(self, *args, **kwargs) -> TaskStatus:
        """Inactivate association between a Person and a Project
        
        Refer to :class:`~account.InactivateAccount` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include PersonID,
            ProjectID, and "resource_name" products
        """

        pass

    @abstractmethod
    def reactivate_account(self, *args, **kwargs) -> TaskStatus:
        """Reactivate association between a Person and a Project
        
        Refer to :class:`~account.ReactivateAccount` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include PersonID and
            ProjectID products
        """

        pass

    @abstractmethod
    def update_allocation(self, *args, **kwargs) -> TaskStatus:
        """Update an allocation
        
        Refer to :class:`~allocation.UpdateAllocation` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object, which should include "ProjectId",
            "ServiceUnitsAllocated", "StartDate", and "EndDate" products.
        """

        pass

    @abstractmethod
    def modify_user(self, *args, **kwargs) -> TaskStatus:
        """Modify a User
        
        Refer to :class:`~user.ModifyUser` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object.
        """

        pass

    @abstractmethod
    def merge_person(self, *args, **kwargs) -> TaskStatus:
        """Merge two PersonRecords
        
        Refer to :class:`~person.MergePerson` for parameter info.
        
        :raises ServiceProviderError: if no implementation is configured
        :raises ServiceProviderTemporaryError: if a temporary error occurs
        :return: A TaskStatus object
        """

        pass
    
class ServiceProvider(AMIEParmDescAware, ServiceProviderIF):
    """Site Service Provider Facade

    The high-level AMIEMod code interacts with this class. This class delegates
    work to the local site implementation of a ServiceProviderIF subclass.
    """

    def __init__(self):
        self.implem = None
        self.logger = logging.getLogger("sp")

    def apply_config(self, config):
        """Apply "localsite" configuration

        The facade class' implementation retrieves the local implementation's
        package and module name from the localsite configuration, and uses
        that information to instantiate the local "real" implementation of
        the :class:``ServiceProviderIF`` interface. It then passes the
        configuration on to that implementation, and remembers the object so
        that the rest of the methods in the class can delegate to it.
        """

        localsite_package = config['package']
        localsite_module = config['module']

        localsite = importlib.import_module(localsite_module,localsite_package)
        self.implem = localsite.ServiceProvider()
        self.logger.debug("ServiceProvider="+str(self.implem.__class__))
        self.implem.apply_config(config)

    def _check_implem(self):
        if self.implem is None:
            msg = "No real ServiceProvider implementation has been configured!"
            raise ServiceProviderError(msg)

    def get_local_task_name(self, method_name, *args, **kwargs) -> str:
        self._check_implem()
        return self.implem.get_local_task_name(method_name, *args, **kwargs)

    def get_tasks(self, active=True, wait=None, since=None) -> list:
        self._check_implem()
        try:
            local_packets = self.implem.get_tasks(active=active,
                                                  wait=wait, since=since)
        except Timeout as to:
            raise ServiceProviderTimeout() from to
        return local_packets
        

    def clear_transaction(self, amie_transaction_id):
        self._check_implem()
        self.implem.clear_transaction(amie_transaction_id)


    def lookup_org(self, *args, **kwargs) -> AMIEOrg:
        self._check_implem()
        valid_kwargs = LookupOrg(*args,**kwargs)
        return self.implem.lookup_org(*args, **valid_kwargs);

    def choose_or_add_org(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ChooseOrAddOrg(*args,**kwargs)
        return self.implem.choose_or_add_org(*args,**valid_kwargs)

    def lookup_person(self, *args, **kwargs) -> AMIEPerson:
        self._check_implem()
        valid_kwargs = LookupPerson(*args,**kwargs)
        return self.implem.lookup_person(*args, **valid_kwargs);

    def choose_or_add_person(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ChooseOrAddPerson(*args,**kwargs)
        return self.implem.choose_or_add_person(*args,**valid_kwargs)

    def update_person_DNs(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = UpdatePersonDNs(*args,**kwargs)
        return self.implem.update_person_DNs(*args,**valid_kwargs)

    def activate_person(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ActivatePerson(*args,**kwargs)
        return self.implem.activate_person(*args,**valid_kwargs)

    def lookup_grant(self, *args, **kwargs) -> str:
        self._check_implem()
        valid_kwargs = LookupGrant(*args,**kwargs)
        return self.implem.lookup_grant(*args, **valid_kwargs);
        
    
    def choose_or_add_grant(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ChooseOrAddGrant(*args,**kwargs)
        return self.implem.choose_or_add_grant(*args,**valid_kwargs)

    def lookup_local_fos(self, *args, **kwargs) -> str:
        self._check_implem()
        valid_kwargs = LookupLocalFos(*args,**kwargs)
        return self.implem.lookup_local_fos(**valid_kwargs)
    
    def choose_or_add_local_fos(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ChooseOrAddLocalFos(*args,**kwargs)
        return self.implem.choose_or_add_local_fos(**valid_kwargs)

 
    def lookup_project_name_base(self, *args, **kwargs) -> str:
        self._check_implem()
        valid_kwargs = LookupProjectNameBase(*args,**kwargs)
        return self.implem.lookup_project_name_base(**valid_kwargs)

    
    def choose_or_add_project_name_base(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ChooseOrAddProjectNameBase(*args,**kwargs)
        return self.implem.choose_or_add_project_name_base(**valid_kwargs)

    def create_project(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = CreateProject(*args,**kwargs)
        return self.implem.create_project(**valid_kwargs)

    def inactivate_project(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = InactivateProject(*args, **kwargs)
        return self.implem.inactivate_project(**valid_kwargs)

    def reactivate_project(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ReactivateProject(*args, **kwargs)
        return self.implem.reactivate_project(**valid_kwargs)

    def create_account(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = CreateAccount(*args, **kwargs)
        return self.implem.create_account(**valid_kwargs)

    def inactivate_account(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = InactivateAccount(*args, **kwargs)
        return self.implem.inactivate_account(**valid_kwargs)

    def reactivate_account(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ReactivateAccount(*args, **kwargs)
        return self.implem.reactivate_account(**valid_kwargs)

    def update_allocation(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = UpdateAllocation(*args, **kwargs)
        return self.implem.update_allocation(**valid_kwargs)

    def modify_user(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = ModifyUser(*args, **kwargs)
        return self.implem.modify_user(**valid_kwargs)

    def merge_person(self, *args, **kwargs) -> TaskStatus:
        self._check_implem()
        valid_kwargs = MergePerson(*args, **kwargs)
        return self.implem.merge_person(**valid_kwargs)


class SPSession(RetryingServiceProxy):
    """Context Manager class for calling the ServiceProvider methods"""

    @classmethod
    def configure(cls, sp,
                  min_retry_delay, max_retry_delay, retry_time_max,
                  time_util=None):
        """Configure the class

        :param sp: the ServiceProvider class
        :type sp: ServiceProvider subclass
        :param min_retry_delay: the minimum number of seconds to wait before
            retrying
        :type min_retry_delay: int
        :param max_retry_delay: the maximum number of seconds to wait before
            retrying; the actual retry starts at ``min_retry_delay`` and
            doubles with every temporary error until the ``max_retry_delay``
            is reached
        :type max_retry_delay: int
        :param retry_time_max: the maximum number of seconds to retry
            before raising a timeout error
        :type retry_time_max: int
        :param time_util: the TimeUtil class to use for returning the current
            time and for sleeping. Default is :class:`misctypes.TimeUtil`
        :type time_util: class, optional
        """
        
        cls.svc = sp
        cls.min_retry_delay = int(min_retry_delay)
        cls.max_retry_delay = int(max_retry_delay)
        cls.retry_time_max = int(retry_time_max)
        cls.time_util = TimeUtil() if time_util is None else time_util
        cls.max_retry_exception = ServiceProviderTimeout
        cls.retry_delay = None
        cls.retry_deadline = None
        cls.temp_exception_classes = [
            ServiceProviderTemporaryError,
            ConnectionError
        ]
        cls.canonical_temp_exception_class = ServiceProviderTemporaryError

    @classmethod
    def get_service_provider(cls):
        return cls.svc

