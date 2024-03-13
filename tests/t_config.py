#!/usr/bin/env python
import unittest
import os
import tempfile
from config import ConfigLoader

class TestConfig(unittest.TestCase):
    def test_config(self):
        with tempfile.TemporaryDirectory() as tempdir:
            os.environ['SECRETS_DIR'] = tempdir
            configfile = tempdir + "/config.ini"
            with open(configfile,"w") as cf:
                cf.write("""
[DEFAULT]
configclass = ConfigLoader

[amieclient]
site_name = %(amieclient_site_name)s
amie_url = https://a3mdev.xsede.org/amie-api-test
api_key = %(amieclient_api_key)s

[localsite]
package = amiemod
module = .test
""")
                cf.close()
            secretfile = tempdir + "/amieclient_api_key"
            with open(secretfile,"w") as tf:
                tf.write("mysecretkey")
            tf.close

            os.environ['AMIECLIENT_SITE_NAME'] = "TEST"

            config = ConfigLoader.loadConfig(configfile)

            self.assertTrue(isinstance(config,dict),
                            msg="dict construction failed")
            self.assertTrue('amieclient' in config,
                            msg="amieclient section not in config")
            amieclient = config['amieclient']
            self.assertEqual(amieclient['site_name'],"TEST",
                             msg="value not injected from environment")
            self.assertEqual(amieclient['amie_url'],"https://a3mdev.xsede.org/amie-api-test",
                             msg="literal value assigned")
            self.assertEqual(amieclient['api_key'],"mysecretkey",
                             msg="value not injected from file")
            self.assertEqual(amieclient['configclass'],"ConfigLoader",
                             msg="value not inherited from [DEFAULT]")
            self.assertEqual(len(amieclient),4,
                             msg="extra variables not filtered out")


if __name__ == '__main__':
    unittest.main()
