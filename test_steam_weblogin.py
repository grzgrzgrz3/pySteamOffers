import unittest
from steam_weblogin import SteamAccount, SteamWebLogin

# username = 'grzgrzgrz3'
# password = ''
if not username:
    username = raw_input('to test define username:\n') 
if not password:
    password = raw_input('to test define password:\n') 
class steam_weblogin_test(unittest.TestCase):
    def setUp(self):
        self.a = SteamAccount(username,password)
        self.s = SteamWebLogin(self.a)
    def test_get_rsa(self):
        values = ['publickey_mod', 'publickey_exp', 'timestamp']
        res = self.s._get_rsa_key()
        for v in values:
            self.assertIn(v,res,msg='Missing values %s in rsa response'%v)
    def test_login(self):
        self.s.login()
if __name__ == '__main__':
    unittest.main()
