from datetime import (datetime, timedelta)
from dateutil.parser import parse as dtparse
from time import sleep

class DateTime(str):
    """
    A subtype of str that only accepts parseable date+time string or a
    datetime value when created, and has a string value of an ISO datetime
    value.
    """

    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], str):
            dt = dtparse(args[0])
        elif len(args) == 1 and isinstance(args[0], datetime):
            dt = args[0]
        else:
            dt = datetime.__new__(cls,*args)

        s = str.__new__(cls,dt.isoformat())
        s._timestamp = dt.timestamp()
        return s

    def timestamp(self):
        return self._timestamp

    def datetime(self):
        return datetime.fromisoformat(self)

    def __int__(self):
        return int(self._timestamp)
    
    @classmethod
    def now(cl):
        return DateTime(datetime.now())

    
class TimeUtil(object):
    """
    Miscellaneous time-related functions
    """

    def sleep(self, secs):
        """sleep() proxy - reimplement in subclass for testing"""

        isecs = int(secs) if secs else 0
        if isecs > 0:
            sleep(isecs)

    def now(self):
        """datetime.now() proxy - reimplement in subclass for testing"""
        return datetime.now()

    def timestamp(self, date_time=None):
        if date_time is None:
            date_time = datetime.now()
        return date_time.timestamp()
        
    def future_time(self, seconds, basetime=None):
        """Return datetime value given number of seconds in the future"""
        if basetime is None:
            basetime = self.now()
        elif isinstance(basetime,float):
            basetime = datetime.fromtimestamp(basetime/1000)

        return basetime if seconds == 0 \
            else basetime + timedelta(seconds=int(seconds))

    def timestamp_to_isoformat(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return dt.isoformat()
