from misctypes import (DateTime, TimeUtil)
from miscfuncs import to_expanded_string

class WaitParms(object):
    def __init__(self, auto_update_delay, human_action_delay, idle_delay,
                 timeutil=None):
        self.timeutil = TimeUtil() if timeutil is None else timeutil
        self.auto_update_delay = auto_update_delay
        self.human_action_delay = human_action_delay
        self.idle_delay = idle_delay

class LoopDelay(object):
    def __init__(self, wait_parms):
        self.wait_parms = wait_parms
        self.base_time = None
        self.target_time = None
        
    def set_base_time(self, datetime_val=None):
        if datetime_val is None:
            self.base_time = self.timeutil.now()
        else:
            self.base_time = datetime_val

    def calculate_target_time(self, base_time, expect_auto_response=False,
                        expect_human_action=False):
        if base_time == None:
            return self.timeutil.now()
        elif expect_auto_response:
            delay = self.wait_parms.auto_update_delay
        elif expect_human_action:
            delay = self.wait_parms.human_action_delay
        else:
            delay = self.wait_parms.idle_delay
        return self.timeutil.future_time(delay, base_time)

    def set_target_time(self, expect_auto_response=False,
                        expect_human_action=False):
        if self.base_time == None:
            return self.timeutil.now()
        elif expect_auto_response:
            delay = self.wait_parms.auto_update_delay
        elif expect_human_action:
            delay = self.wait_parms.human_action_delay
        else:
            delay = self.wait_parms.idle_delay
        self.target_time = self.timeutil.future_time(delay, self.base_time)
        return self.target_time

    def set(self, base_time=None, expect_auto_response=False,
            expect_human_action=False):
        self.base_time = base_time
        if self.base_time == None:
            delay = 0
        elif expect_auto_response:
            delay = self.wait_parms.auto_update_delay
        elif expect_human_action:
            delay = self.wait_parms.human_action_delay
        else:
            delay = self.idle_delay
        self.target_time = self.timeutil.future_time(delay, self.base_time)
        return self.target_time

    def target_time(self):
        return self.target_time
    
    def wait_secs(self, currtime=None):
        if self.target_time is None:
            return 0
        if currtime is None:
            currtime = self.timeutil.now()
        wait = (self.target_time - currtime).total_seconds()
        return wait if wait >= 0 else 0
