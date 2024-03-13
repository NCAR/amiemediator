#!/usr/bin/env python
import os, sys
import time
from filewait import FileWaiter

waitfile = sys.argv.pop(0)
# fork
pid = os.fork()
if pid == 0:
    subpid = os.fork()
        if subpid == 0:
            fw = FileWaiter(waitfile)
            fw.release()
            sys.exit(0)
    else:
        return
class TestFileWaiter(unittest.TestCase):

    def xtest_wait_timeout(self):
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
        print("test_wait_release starttime="+str(starttime))
        waitfile = str(Path(tempdir.name,"relwaitfile"))
        fw = FileWaiter(waitfile)
        spawn_release(waitfile)
        released = fw.wait(3)
        endtime = time.time()
        print("test_wait_release endtime="+str(endtime))
        elapsed = endtime - starttime
        self.assertFalse(released,
                         msg="wait() did not return True")
        self.assertTrue((elapsed > 0.0) and (elapsed < 2.5),
                        msg=str(elapsed) +" seconds elapsed on release")

        
if __name__ == '__main__':
    unittest.main()
    tempdir.cleanup()
