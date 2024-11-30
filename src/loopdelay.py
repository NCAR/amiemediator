from misctypes import (DateTime, TimeUtil)
from miscfuncs import to_expanded_string

class WaitParms(object):
    def __init__(self, auto_update_delay, human_action_delay, idle_delay,
                 timeutil=None):
        # Keep a timeutil object so that it can be easily mocked
        if timeutil is None:
            timeutil = TimeUtil()
        self.auto_update_delay = auto_update_delay
        self.human_action_delay = human_action_delay
        self.idle_delay = idle_delay
        self.timeutil = timeutil

    def get_timeutil(self):
        return self.timeutil

class LoopDelay(object):
    def __init__(self, wait_parms, target_time=None):
        if target_time:
            target_time = self.now()
        # Keep a timeutil object so that it can be easily mocked
        self.timeutil = wait_parms.get_timeutil()
        self.wait_parms = wait_parms
        self.target_time = target_time

    def now(self):
        return self.timeutil.now()
    
    def calculate_target_time(self,
                              base_time=None,
                              immediate=False,
                              expect_auto_response=False,
                              expect_human_action=False):
        if base_time == None:
            base_time = self.now()
        self.base_time = base_time
        if immediate:
            self.target_time = base_time
            return
        elif expect_auto_response:
            delay = self.wait_parms.auto_update_delay
        elif expect_human_action:
            delay = self.wait_parms.human_action_delay
        else:
            delay = self.wait_parms.idle_delay
        self.target_time = self.timeutil.future_time(delay, base_time)

    def get_base_time(self):
        return self.base_time
    
    def set_target_time(self, target_time):
        self.target_time = target_time

    def get_target_time(self):
        return self.target_time

    def wait_secs(self):
        """Return positive seconds to wait until target_time, or None"""
        
        if self.target_time is None:
            return None
        currtime = self.timeutil.now()
        wait = int((self.target_time - currtime).total_seconds())
        return wait if wait > 0 else None
