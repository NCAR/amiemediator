#!/usr/bin/env python
import unittest
import tempfile
from pathlib import Path
import os, sys
import time
import subprocess
from filewait import FileWaiter

tempdir = tempfile.TemporaryDirectory()

class TestFileWaiter(unittest.TestCase):

    def test_wait_timeout(self):
        starttime = time.time()
        waitfile = str(Path(tempdir.name,"tmwaitfile"))
        fw = FileWaiter(waitfile)
        released = fw.wait(2)
        endtime = time.time()
        elapsed = endtime - starttime
        self.assertFalse(released,
                         msg="wait() did not return False")
        self.assertTrue((elapsed > 1.5) and (elapsed < 2.5),
                        msg=str(elapsed) +" seconds elapsed on timeout")

    def test_wait_release(self):
        starttime = time.time()
        waitfile = str(Path(tempdir.name,"relwaitfile"))
        fw = FileWaiter(waitfile)
        subprocess.run([__file__,"release",waitfile,"1"])
        released = fw.wait(3)
        endtime = time.time()
        elapsed = endtime - starttime
        self.assertFalse(released,
                         msg="wait() did not return True")
        self.assertTrue((elapsed > 0.0) and (elapsed < 2.5),
                        msg=str(elapsed) +" seconds elapsed on release")

        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "release":
            waitfile = sys.argv[2]
            delay = int(sys.argv[3])
            pid = os.fork()
            if pid == 0:
                subpid = os.fork()
                if subpid == 0:
                    time.sleep(delay)
                    fw = FileWaiter(waitfile)
                    fw.release()
            sys.exit(0)
        
    unittest.main()
    tempdir.cleanup()
