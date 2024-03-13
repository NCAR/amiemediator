from abc import (ABC, abstractmethod)
import stat
import signal, os, sys, errno
import time

class FileWaiterFileType(Exception):
    """Exception raised when wait file exists and is wrong type"""
    pass


class FileWaiter(object):
    implem = None
    
    def __init__(self, path):
        """Use a file to wait for another process to release us

        :param path: the path of the file to use for synchronization
        :type path: str
        """
        if not FileWaiter.implem:
            if os.name == "posix":
                FileWaiter.implem = FIFOFileWaiter(path)
            else:
                FileWaiter.implem = PollingFileWaiter(path)
        
    def wait(self, max_secs=600):
        """Wait for another process to release us

        :param max_secs: Maximum time to wait, in seconds
        :type max_secs: int
        :return: True if we were released, False if we timed out
        """
        FileWaiter.implem.wait(max_secs)

    def release(self):
        """Release another process that might be waiting"""
        FileWaiter.implem.release()

class FileWaiterImplABC(ABC):

    @abstractmethod
    def wait(self, max_secs):
        pass

    @abstractmethod
    def release(self):
        pass

class FIFOFileWaiter(FileWaiterImplABC):

    def __init__(self, path):
        self.path = path
        if os.path.exists(self.path):
            if stat.S_ISFIFO(os.stat(self.path).st_mode):
                return
            self.implem = PollingFileWaiter()
        else:
            os.mkfifo(self.path)

    def wait(self, max_secs):
        pid = os.fork()
        if pid == 0:
            signal.alarm(max_secs)
            fd = os.open(self.path, os.O_RDONLY)
            os._exit(0)
        (wpid, status) = os.waitpid(pid, 0)
        signo = status & 255
        if signo:
            return False

        return True

    def release(self):
        try:
            fd = os.open(self.path, os.O_RDWR | os.O_NONBLOCK)
            os.close(fd)
        except OSError as e:
            if e.errno != errno.ENXIO:
                raise e

class PollingFileWaiter(FileWaiterImplABC):

    def __init__(self, path):
        self.path = path
        if os.path.exists(self.path):
            if stat.S_ISREG(os.stat(self.path).st_mode):
                return
            raise FileWaiterFileType()
        with open(self.path, 'w') as fp:
            # truncate file; zero size implies no process is waiting
            pass

    def _get_file_size(self):
        statinfo = os.stat(self.path)
        return statinfo.ST_SIZE

    def wait(self, max_secs):
        with open(self.path, 'a') as fp:
            print('', file=fp)
            # add a char; non-zero size implies process is waiting
        initial_size = self._get_file_size()
        size = initial_size
        while True:
            if size < initial_size:
                return True
            if max_secs <= 0:
                return False
            time.sleep(1)
            size = self._get_file_size()
            max_secs = max_secs - 1

    def release(self):
        size = self._get_file_size()
        if size == 0:
            return
        with open(self.path, 'w') as fp:
            # truncate file
            pass

    
