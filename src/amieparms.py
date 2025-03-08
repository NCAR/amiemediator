from misctypes import DateTime
from amieclient.packet.base import Packet as AMIEPacket
from parmdesc import transform_value
from parmdesc import process_parms as real_process_parms
from parmdesc import ParmDescAware

def get_packet_keys(packet) -> dict:
    """Return a packet's job_id, amie_transaction_id, and packet_id

    An amie_transaction_id contains a combination of all the AMIE fields that
    uniquely identify an AMIE transaction (transaction_id, originating site,
    remote site, and local site).

    The packet_id uniquely identifies an AMIE Packet within a transaction, so
    the combination of amie_transaction_id and packet_id uniquely identify a
    packet.

    The job_id also uniquely identifies a packet; it is the globally-unique
    packet id for AMIE - the Packet.packet_rec_id (not to be confused with
    Packet.packet_id). Since the packet is associated with a set of tasks in
    the ServiceProvider and therefore acts a the "job" that ties multiple tasks
    together, we call this job_id rather that packet_rec_id in that context to
    avoid confusion with the packet_id.

    While both the job_id and amie_transaction_id+packet_id uniquely identify
    a packet, the amie_transaction_id+packet_id is the preferred identifier
    for the ServiceProvider because it can be used to distinguish AMIE jobs
    from jobs that might come from other sources. However, the job_id is used
    internally by the mediator because AMIE reply packets refer to
    packet_rec_ids in the "in_reply_to" attribute.

    :param packet: Input packet data
    :param type: dict or AMIE Packet
    :raises TypeError: if invalid packet data is provided
    :return: tuple
    """

    atrid = None
    if isinstance(packet,AMIEPacket):
        job_id = str(packet.packet_rec_id)
        tid = str(packet.transaction_id)
        os = str(packet.originating_site_name)
        rs = str(packet.remote_site_name)
        ls = str(packet.local_site_name)
        pid = str(packet.packet_id)
    elif isinstance(packet,dict):
        job_id = packet.get('job_id',None)
        atrid = packet.get('amie_transaction_id',None)
        pid = packet.get('amie_packet_id',None)
        if atrid is None or job_id is None:
            header = packet.get('header',None)
            if header is None:
                raise TypeError("get_packet_keys() given unknown dict format")
            tid = str(header['transaction_id'])
            os = str(header['originating_site_name'])
            rs = str(header['remote_site_name'])
            ls = str(header['local_site_name'])
            pid = str(header['packet_id'])
            job_id = str(header['packet_rec_id'])
    else:
        raise TypeError("get_packet_keys() requires AMIE Packet or dict")

    if atrid is None:
        atrid = f"{os}:{rs}:{ls}:{tid}"

    return (job_id, atrid, pid)

def parse_atrid(atrid) -> (str, str, str, str):
    """Return components of amie_transaction_id string

    The components are (in order) originating_site_name, remote_site_name,
    local_site_name, and transaction_id

    :param atrid: AMIE transaciton ID string
    :type atrid: str
    :returns: Tuple with os, rs, ls, tid
    """
    
    comps = atrid.split(":")
    return (comps[0],comps[1],comps[2],comps[3])

def strip_key_prefix(prefix, parm_dict):
    """Copy a dictionary but remove the given prefix from keys

    This is meant to be used to remove the "Pi" or "User" prefix from packet
    data. It will *not* recursively process embedded dictionaries. In addition,
    it assumes that if the first character following the prefix is lower case,
    the prefix should not be removed; for example, if the prefix is "User",
    the "UserFirstName" key would be affected, by the "Username" key would not
    be. Finally, it will also remove a matching lower-case prefix followed by "_"
    (e.g. if prefix is "Pi" it would replace "pi_name" with "name")
    
    :param prefix: The prefix; this is expected to be "Pi" or "User"
    :type prefix: str
    :param parm_dict: The prefix; this is expected to be "Pi" or "User"
    :type parm_dict: dict
    """
    if prefix is None:
        return parm_dict.copy()

    lcprefix = prefix.lower() + "_"
    newdict = {}
    for key in parm_dict:
        if key == 'prefix':
            continue
        elif key.startswith(prefix):
            newkey = key.removeprefix(prefix)
            if newkey[0:1].islower():
                newdict[key] = parm_dict[key]
            else:
                newdict[newkey] = parm_dict[key]
        elif key.startswith(lcprefix):
            newkey = key.removeprefix(lcprefix)
            newdict[newkey] = parm_dict[key]
        else:
            newdict[key] = parm_dict[key]
    return newdict

def process_parms(allowed,required=[]):
    return real_process_parms(allowed,required)

class AMIEParmDescAware(ParmDescAware):
    """A ParmDescAware subclass that defines default parameter info"""

    def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)

    #: Default values for ParmDescAware.parm2type
    # Note that all parameters defined by AMIE start with an upper case letter.
    # Parameters that start with lower case are defined by amiemediator.
    # One exception is 'Resource', which is the first element of the
    # ResourceList list. The AMIE spec says ResourceList is a list, but it
    # only contains one element; to make things easier on the service provider
    # implementation, Resource is set when an AMIE Packet is converted to an
    # ActionablePacket
    default_parm2type = {
        'active': bool,
        'amie_packet_type': str,
        'amie_packet_timestamp': DateTime,
        'amie_packet_id': str,
        'amie_transaction_id': str,
        'contingent_resources': str,
        'job_id': str,
        'person_active': bool,
        'person_role': str,
        'site_grant_key': str,
        'site_org': str,
        'local_fos': str,
        'local_user_id': str,
        'project_id': str,
        'project_name_base': str,
        'requested_amount': str,
        'requested_resource': str,
        'Resource': str,
        'resource_name': str,
        'task_name': str,
        'timestamp': int,
        'user_notified': bool,
        
        'Abstract': str,
        'AcademicDegree': [dict],
        'AccountActivityTime': DateTime,
        'ActionType': str,
        'AllocatedResource': str,
        'AllocationType': str,
        'BoardType': str,
        'BusinessPhoneComment': str,
        'BusinessPhoneExtension': str,
        'BusinessPhoneNumber': str,
        'ChargeNumber': str,
        'CitizenshipList': str,
        'City': str,
        'Comment': str,
        'Country': str,
        'DeleteGlobalID': str,
        'DeletePersonID': str,
        'DeletePortalLogin': str,
        'Department': str,
        'DnList': [str],
        'Email': str,
        'EndDate': DateTime,
        'Fax': str,
        'FirstName': str,
        'GlobalID': str,
        'GrantNumber': str,
        'GrantType': str,
        'HomePhoneComment': str,
        'HomePhoneExtension': str,
        'HomePhoneNumber': str,
        'KeepGlobalID': str,
        'KeepPersonID': str,
        'KeepPortalLogin': str,
        'LastName': str,
        'MiddleName': str,
        'NsfStatusCode': str,
        'Organization': str,
        'OrgCode': str,
        'PasswordAccessEnable': str,
        'PersonID': str,
        'PfosNumber': str,
        'PiCity': str,
        'PiCountry': str,
        'PiDepartment': str,
        'PiFirstName': str,
        'PiLastName': str,
        'PiMiddleName': str,
        'PiPersonID': str,
        'PiOrganization': str,
        'PiOrgCode': str,
        'PiRemoteSiteLogin': str,
        'PiState': str,
        'Position': str,
        'ProjectID': str,
        'ProjectTitle': str,
        'RecordID': str,
        'RemoteSiteLogin': str,
        'RequestedLoginList': str,
        'Resource': str,
        'ResourceList': [str],
        'RoleList': list,
        'ServiceUnitsAllocated': float,
        'ServiceUnitsRemaining': float,
        'Sfos': [dict],
        'SitePersonID': [dict],
        'StartDate': DateTime,
        'State': str,
        'StreetAddress': str,
        'StreetAddress2': str,
        'Title': str,
        'UID': str,
        'UserFirstName': str,
        'UserLastName': str,
        'UserOrganization': str,
        'UserOrgCode': str,
        'Username': str,
        'RequestedLoginList': [str],
        'Zip': str,
    }

    #: Default values for ParmDescAware.parm2doc
    default_parm2doc = {
        'active': "Is object currently 'active' at the local site",
        'amie_packet_type': "packet_type from an AMIE packet",
        'amie_packet_timestamp': "timestamp from an AMIE packet header",
        'amie_packet_id': "string that uniquely identifies a packet " + \
                          "within an AMIE transaction",
        'amie_transaction_id': "string that uniquely identifies an AMIE " + \
                               "transaction",
        'contingent_resources': "additional resources assigned by local site",
        'job_id': "string that uniquely identifies related set of tasks",
        'person_active': "Is person currently 'active' at the local site",
        'person_role': 'person role ("Pi" or "User")',
        'site_grant_key': 'local key used to identify "Grants"',
        'site_org': 'Internal org code for site',
        'local_fos': 'locally-defined "field of science"',
        'local_user_id': 'locally-defined immutable user ID',
        'project_name_base': 'string used in building new project names',
        'Resource': 'First element from ResourceList',
        'resource_name': 'Single site resource name (from Resource)',
        'task_name': 'Task name, unique within a packet',
        'timestamp': 'Packet update time',
        'user_notified': 'site-specific notification of user complete',
    }
    
    #: Default value for ParmDescAware.default_parm_doc
    default_parm_doc = '(See AMIE Model)'

