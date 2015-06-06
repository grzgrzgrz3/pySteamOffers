from weblogin.weblogin import WebLogin, WebModule, WebControl
import time
from rsa import encode
import json

# defined like that to let eval json bool 'true'
true = True
false = False


class SteamGuard(object):
    def get(self, acc):
        code = raw_input('Type stam guard code for username %s: \n' % (acc.name))
        return code


class SteamAccount(object):
    _steam_guard = SteamGuard

    def __init__(self, username, password, email=None, email_pwd=None, guard=None):
        # possible to specify own guard code handler
        if guard:
            _steam_guard = guard
        self.username = username
        self.password = password
        self.email = email
        self.email_pwd = email_pwd
        self._id = None
        self._login = SteamWebLogin(self)
        self.cookies_file_name = self.username + ".cookies"

    def set_steam_id(self, id):
        self._id = id

    def get_encrypted_password(self, rsa_values):
        return encode(self.password, rsa_values['publickey_mod'],
                      rsa_values['publickey_exp'])

    @property
    def name(self):
        return self.username

    @property
    def guard_code(self):
        return self._steam_guard().get(self)

    def login(self):
        self._login.login()

    def get_page(self, url):
        # fetching page and returning html response
        return self._login.get_page(url)

    @property
    def offerts(self):
        page = self.get_page(Offerts.URL)
        self._offerts = HtmlToObejct.proces_aggregate(page, Offert))
        return self._offerts


class SteamWebLoginUnhandledException(Exception):

    def __init__(self, msg, par):
        s = 'Unhandled steam answer parameter: %s, \ndata:\n%s ' % (par, json.dumps(msg, indent=4))
        super(SteamWebLoginUnhandledException, self).__init__(s)


class SteamWebLogin(WebLogin):
    LOGIN_CHECK_PATTERN = 'href="javascript:Logout();">'
    LOGIN_CHECK_URL = "url = 'https://steamcommunity.com'"

    def _do_login(self, msg='{}'):
        """
        all steamcommunity logining is handling here
        """
        # if msg =='{}':
        # if 'UpdateCaptcha' in self.http.open('http://store.steampowered.com/login/'):
        # raise Exception("captcha not implemented")
        url = "https://steamcommunity.com/login/dologin/"
        msg = eval(msg)
        if msg.get('captcha_gid', '-1') != '-1':
            # self.http.open('https://steamcommunity.com/public/captcha.php?gid='+str(msg['captcha_gid']))
            # self.http.save_html_response('captcha.png')
            # captcha = raw_input('podaj captche:\n')
            """
            Captcha is needed when we sent wrong post data few times. 
            In this case we can change ip or set up .cookie file by our own.
            """
            raise NotImplementedError("captcha in steam webform")
        rsa_values = self._get_rsa_key()
        login_data = {"password": self.account.get_encrypted_password(rsa_values),
                      "username": self.account.username,
                      'emailauth': '',
                      'captchagid': msg.get('captcha_gid', '-1'),
                      'donotcache': int(time.time()),
                      'captcha_text': '',
                      'emailsteamid': msg.get('emailsteamid', ''),
                      'rsatimestamp': rsa_values['timestamp'],
                      'remember_login': 'true',
                      'twofactorcode': '',
                      'loginfriendlyname': ''}
        # success: False
        if not msg.get('success', False) and msg != {}:
            if msg.get('message', '') == "SteamGuard":
                # steam guard code needed
                print 'need steamgueard code'
                login_data['emailauth'] = self.account.guard_code
            elif msg.get('message', '') == "Error verifying humanity":
                """
                this message occures when we do not pass or pass wrong captcha code.
                """
                raise NotImplementedError("captcha in steam webform")
            else:
                raise SteamWebLoginUnhandledAnswerException(msg, "message:{Unknow}")
        msg = eval(self.http.open(url, login_data))
        print msg
        raw_input("dalej?\n")
        # success: False
        if not msg.get('success', False):
            print 'message not success'
            self._do_login(str(msg))
            return
            # success: True
            # login_complete: True
        if msg.get('login_complete', False):
            print 'logged in'
            self._transfer(msg['transfer_url'], msg['transfer_parameters'])
            if not self.is_logged:
                self._do_login()
            print 'logged in'
            # login_complete: False
        else:
            raise SteamWebLoginUnhandledException(msg, "login_compled:False")

    def _transfer(self, url, params):
        url = url.replace('\\', '')
        self.account.set_steam_id(params['steamid'])
        self.http.open(url, params)

    def _get_rsa_key(self):
        url = "https://steamcommunity.com/login/getrsakey/"
        post_data = {"username": self.account.username,
                     'donotcache': int(time.time())}
        return eval(self.http.open(url, post_data))

    @property
    def is_logged(self):
        if not self.http.html_response:
            self.http.open(self.LOGIN_CHECK_URL)
        if self.LOGIN_CHECK_PATTERN in self.http.html_response:
            return True
        return False


class OffersPage(WebModule):
    call_backs = ('new_offert', 'not_implemented')

    def __call__(self):
        self.controler.new_offer('nowa_oferta')
        self.controler.not_implemented('nowa_oferta')


WebControl.register_module(OffersPage)


class Bot(WebControl):
    def __init__(self, username, password):
        self.account = SteamAccount(username, password)
        super(Bot, self).__init__(self.bot_account)
        self.loop()

    def new_offert(self, offert):
        print 'nowa oferta'


class Offer(object):
    pass


class IncomingOffers(Offer):
    pass


class SentOffer(Offer):
    pass


if __name__ == "__main__":
    Bot('grzgrzgrz3', '')
