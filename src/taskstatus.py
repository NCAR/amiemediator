import json
from miscfuncs import (Prettifiable, to_expanded_string)
from datetime import datetime
from misctypes import DateTime
from amieparms import (AMIEParmDescAware, process_parms)

class State(str):
    """
    A string subtype used to validate and store valid Task state values
    """

    valid_values = ("nascent",            # New, not yet persisted
                    "queued",             # Newly persisted, not acknowledged
                    "in-progress",        # In progress
                    "delegated",          # Delegated, service provider waiting
                    "syncing",            # Delegated op syncing to sp
                    "successful",         # Complete, successful
                    "failed",             # Complete, unsuccessful
                    "errored",            # Aborted due to error
                    "cleared")            # completion/abort acknowledged;
                                          #  cleared tasks may or may not be
                                          #  retained in persistent storage

    def __new__(cls,val):
        sval = str(val)
        if sval.lower() in State.valid_values:
            sval = sval.lower()
        else:
            raise TypeError("not a valid state value")
        return str.__new__(cls,sval)

    def is_end_state(st):
        return st in ("successful","failed","errored","cleared");


class Product(AMIEParmDescAware,dict):
    
    # this will be supplemented with data from AMIEAttrDescAware
    parm2type = {
        'value': str,
        'name': str,
    }
    # this will be supplemented with data from AMIEAttrDescAware
    parm2doc = {
        'value': 'Task product identifier',
        'name': 'Task product name',
    }

    @process_parms(
        allowed=[
            'name',
            'value',
        ],
        required=[
            'name',
            ])
    def __init__(self, *args, **kwargs):
        """Create a product description for a TaskStatus product list

        When a task is created by a Service Provider, it makes TaskStatus
        objects available for the moderator to monitor the status of the
        task. The ultimate goal of a task is to produce an appropriate set
        of products and return their values.

        There are two predefined product names: "FAILED" and "ERRORED". These
        correspond to the "failed" and "error" State values. The values for
        these special products is an error message.
        """

        dict.__init__(self,**kwargs)


class TaskStatus(AMIEParmDescAware, dict):
    # this will be supplemented with data from AMIEAttrDescAware
    parm2type = {
        'message': str,
        'products': [Product],
        'task_state': State,
        'timestamp': int,
    }
    # this will be supplemented with data from AMIEAttrDescAware
    parm2doc = {
        'products': 'List of task Products',
        'task_state': 'task State',
        'timestamp': 'Task update time (msec since start of epoch)'
    }

    @process_parms(
        allowed=[
            'job_id',
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'task_state',
            'timestamp',
            'products',
            ],
        required=[
            'amie_transaction_id',
            'amie_packet_rec_id',
            'task_name',
            'task_state',
            'timestamp'
            ])
    def __init__(self, *args, **kwargs):
        """Create an AMIEMod Service Provider TaskStatus object

        When a request is submitted to a Service Provider for a
        potentially long-lived task, the Service Provider will
        assign a unique ID to the task. AMIEMod can use this task
        ID to poll the Service Provider for the status of the task,
        which is described by a TaskStatus object.

        A Service Provider should use this constructor to create
        a TaskStatus object.

        If the product list contains a "FAILED" or "ERRORED" product, the
        task_state will be set to "failed" or "errored" respectively. If a
        task_state of "failed" or "errored" is set explicitly and there is
        no corresponding "FAILED" or "ERRORED" product, a KeyError is raised
        """

        if 'products' not in kwargs:
            kwargs['products'] = []

        state = kwargs['task_state']
        if state == 'failed' or state == 'errored':
            kwargs['task_state'] = None
        for pr in kwargs['products']:
            if pr['name'] == 'FAILED':
                kwargs['task_state'] = "failed"
                break
            elif pr['name'] == 'ERRORED':
                kwargs['task_state'] = "errored"
                break
        if kwargs['task_state'] is None:
            # this can only happen if we cleared it earlier
            raise KeyError("No message Product when task_state is "+str(state))

        dict.__init__(self,**kwargs)

    def fail(self, message):
        """Mark the task "failed" by adding a "FAILED" product

        :param message: The associated message
        :type message: str
        """
        self._add_bad_product("FAILED",message)

    def error(self, message):
        """Mark the task "errored" by adding a "ERRORED" product

        :param message: The associated message
        :type message: str
        """
        self._add_bad_product("ERRORED",message)

    def _add_bad_product(self, type, message):
        if message is not None:
            message = message.strip()
            if len(message) == 0:
                message = None
        if message is None:
            raise ValueError("non-empty message is required")
        newprod = Product(name=type, value=message)
        products = self['products']
        products.append(newprod)
        self['task_state'] = type.lower()
                

    def get_product_value(self, name):
        """Return the value of the named Product

        :param name: The unique name of the product within the TaskStatus
            object
        :type name: str
        :return: str, or None if named product does not exist
        """

        for pr in self['products']:
            if pr['name'] == name:
                return pr['value']
        return None


class TaskStatusList(Prettifiable):
    def __init__(self, tasks=None):
        """Create a collection of TaskStatus objects

        A TaskStatusList is iterable; the iterator will return tasks in
        timestamp order. TaskStatus objects can be looked up by task_name.
        A TaskStatusList is assumed to represent the tasks for a single
        transaction: there should be at most one active task.

        :param tasks: TaskStatus objects or dicts
        :type tasks: list, optional
        """
        self.tasks_by_name = {}
        if tasks is not None:
            self.put(tasks)
    
    def pformat(self):
        return self._pformat()

    def vpformat(self):
        return self._pformat('products')

    def _pformat(self, *verbose_keys):
        proxy_list = []
        for task in self.get_list():
            name = "  " + task['task_name']
            state = task['task_state']
            timestamp = float(task['timestamp'])
            dt = datetime.fromtimestamp(timestamp)
            ftimestamp = dt.isoformat()
            task_dict = {
                'name': name,
                'state': state,
                'tstamp': ftimestamp
                }
            if verbose_keys:
                for vk in verbose_keys:
                    task_dict[vk] = task[vk]
            proxy_list.append(task_dict)
        return to_expanded_string(proxy_list)

        
    def __str__(self):
        return str(self.tasks_by_name)

    def __eq__(self, other):
        if not isinstance(other,TaskStatusList):
            return False
        return self.tasks_by_name == other.tasks_by_name
    
    def __iter__(self):
        return iter(self.get_list())

    def get_list(self):
        """Return all TaskStatus objects in a list ordered by timestamp

        Note that this is not normally needed because TaskStatusList is
        iterable.
        """
        tasks = list(self.tasks_by_name.values())
        tasks.sort(key=lambda ts: ts['timestamp'])
        return tasks

    def get_name_map(self):
        """Return all TaskStatus objects in a dict indexed by task_name"""
        return self.tasks_by_name

    def get(self, task_name):
        """Return the TaskStatus object with the given name, or None

        :param task_name: the task name
        :type task_name: str
        :return: TaskStatus or None
        """

        return self.tasks_by_name.get(task_name,None)

    def put(self, *task_status):
        """Add/update a TaskStatus object or list of objects

        :param task_status: the TaskStatus object or a list of them
        :type task_status: TaskStatus or dict or list or TaskStatus/dict
        """
        
        inlist = []
        for ts in task_status:
            if isinstance(ts,list):
                inlist.extend(ts)
            else:
                inlist.append(ts)
        ts_list = []
        for ts in inlist:
            if isinstance(ts, dict):
                ts = TaskStatus(**ts)
                ts_list.append(ts)
            elif isinstance(ts,TaskStatus):
                ts_list.append(ts)
            else:
                msg="TaskStatusList requires (list of) TaskStatus or dict"
                raise TypeError(msg)

        for ts in ts_list:
            task_name = ts['task_name']
            existing_ts = self.get(task_name)
            if existing_ts is None or \
               existing_ts['timestamp'] < ts['timestamp']:
                self.tasks_by_name[task_name] = ts

    def find_active_task(self):
        """Return the active TaskStatus object or None

        :return: TaskStatus or None
        """

        for ts in self.tasks_by_name.values():
            st = ts['task_state']
            if not State.is_end_state(st):
                return ts
        return None

    def get_amie_transaction_ids(self) -> list:
        """Return amie_transaction_ids from all tasks"""
        atridlist = [ts['amie_transaction_id'] \
                     for ts in self.tasks_by_name.values()]
        return set(atridlist)
            
