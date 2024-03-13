from pathlib import Path
import os
import json
from stat import *
import time
from filewait import FileWaiter

class Snapshots(object):
    def __init__(self, dir, mode='r', purge_writeable=True):
        """Set up a directory as a "snapshot" directory

        A "snapshot" is a JSON-serialized image of an object at an instant
        in time. A Snapshots instance is created as either a "writer" or a
        "reader".

        Each snapshot has a key unique to the object. The key should be a
        readable string that does not start with '.' or contain '/'. The key
        is used as the name of the snapshot file.

        :param dir: The directory containing snapshot files.
        :type dir: str
        :param mode: The mode: either 'r' or 'w'
        :type mode: str
        """
        if (mode != 'r') and (mode != 'w'):
            raise ValueError("mode must be 'r' or 'w'")
        
        Path(dir).mkdir(parents=True, exist_ok=True)
        self.dir = dir
        waitfile = str(Path(dir,".WAITFILE"))
        self.filewaiter = FileWaiter(waitfile)
        if mode == 'r':
            self.images = None
        else:
            self.images = dict()
            entry_gen = os.scandir(self.dir)
            for dir_entry in entry_gen:
                if not dir_entry.name.startswith('.') and dir_entry.is_file():
                    if purge_writeable:
                        Path(dir_entry.path).unlink(missing_ok=True)
                    else:
                        with open(dir_entry.path,'r') as f:
                            jdata = f.read()
                            self.images[dir_entry.name] = jdata

    def mode(self):
        """Return the mode ('r' or 'w')"""
        
        return 'r' if self.images is None else 'w'
        
    def update(self, key, data):
        """Update the data associated with the given key

        The Snapshot object must be in 'w' mode.
        
        :param key: The key
        :type key: str
        :param data: The object data
        :type data: Any JSON-serializeable value or object
        """
        
        if self.mode() == 'r':
            raise TypeError("Snapshots.update() not supported in 'r' mode")
        jdata = json.dumps(data)
        image = self.images.get(key, None)
        if jdata != image:
            fpath = Path(self.dir,key)
            with open(fpath,'w') as f:
                f.write(jdata)
                self.images[key] = jdata
                self.filewaiter.release()
        
    def release(self):
        """Release any process waiting on the snapshots

        The Snapshot object must be in 'w' mode.
        """
        
        if self.mode() == 'r':
            raise TypeError("Snapshots.update() not supported in 'r' mode")

        self.filewaiter.release()

    def delete(self, key):
        """Delete the data associated with the given key

        The Snapshot object must be in 'w' mode.

        :param key: The key
        :type key: str
        :param data: The object data
        :type data: Any JSON-serializeable value or object
        """
        
        if self.mode() == 'r':
            raise TypeError("Snapshots.delete() not supported in 'r' mode")
        fpath = Path(self.dir, key)
        if os.path.exists(fpath):
            Path(fpath).unlink(missing_ok=True)
            self.filewaiter.release()
        self.images.pop(key, None)
    
    def list(self):
        """Return all snapshots

        The Snapshot object can be in either 'r' or 'w' mode.

        :return: A list of unserialized data objects
        """
        
        if self.mode() == 'r':
            images = dict()
            entry_gen = os.scandir(self.dir)
            for dir_entry in entry_gen:
                if not dir_entry.name.startswith('.') and dir_entry.is_file():
                    key = dir_entry.name
                    with open(dir_entry.path,'r') as f:
                        jdata = f.read()
                        images[key] = jdata
        else:
            images = self.images

        keys = list(images.keys())
        keys.sort()
        objs = list()
        for key in keys:
            jdata = images[key]
            objs.append(json.loads(jdata))
        return objs
    
    def list_when_updated(self, max_wait=0):
        """Return all snapshots when something is updated or after max_wait sec

        The Snapshot object must be in 'r' mode.

        :param key: The target key
        :type key: str
        :param max_wait: The maximum seconds to wait; if nothing is updated in
            this number of seconds, all snapshots are returned (default=0)
        :type max_wait: int
        :return: A list of unserialized data objects
        """
        
        if self.mode() == 'w':
            raise TypeError("Snapshots.list_when_updated() " +\
                            "not supported in 'w' mode")
        if max_wait > 0:
            self.filewaiter.wait(max_wait)
            
        return self.list()

    def get(self, key):
        """Get the snapshot data for the given key

        The Snapshot object can be in either 'r' or 'w' mode.
        
        :param key: The target key
        :type key: str
        :return: The unserialized data object from the snapshot
        """

        if self.mode() == 'r':
            (jdata, token) = self._get_from_file(key)
        else:
            jdata = self.images.get(key,None)
            if jdata is None:
                return None
        return json.loads(jdata)

    def get_when_updated(self, key, max_wait=0, token=None):
        """Get the snapshot data for the given key when it is updated

        The Snapshot object must be in 'r' mode.

        :param key: The target key
        :type key: str
        :param max_wait: The maximum seconds to wait
        :type max_wait: int
        :param token: A token used to track when the file has changed; if None,
            the function returns immediately
        :type token: list
        :return: A (data, token) pair; the token is None if the key does not
            exist, and data is None if the operation times out
        """
        if self.mode() == 'w':
            raise TypeError("Snapshots.get_when_updated() " +\
                            "not supported in 'w' mode")
        (jdata, curr_token) = self._get_from_file(key)
        if (token is None) or (token != curr_token):
            return (jdata, curr_token)
        
        curr_time = int(time.time())
        expire_time = curr_time + max_wait
        if curr_time < expire_time:
            remaining_time = expire_time - curr_time
            self.filewaiter.wait(remaining_time)
        (jdata, curr_token) = self._get_from_file(key)
        if (token is None) or (token != curr_token):
            return (jdata, curr_token)
        return (None, curr_token)
            

    def _get_from_file(self, key):
        fpath = Path(self.dir, key)
        if not os.path.exists(fpath):
            return (None, None)
        with open(fpath,'r') as f:
            jdata = f.read()
            fd = f.fileno()
            statinfo = os.fstat(fd)
            token = (statinfo.st_mtime, statinfo.st_size)
            data = json.loads(jdata)
        return (data, token);
