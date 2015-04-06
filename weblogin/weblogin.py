import time
from http import Browser


class WebLogin(object):
    def __init__(self,account):
        self.account = account
        self.http = Browser(cookie_file_name = self.account.cookies_file_name)
    def login_check(self):
        while 1:
            if self.is_logged:
                print 'logged nie potrzeba logowania'
                break
            print 'not logged loguje'
            self.login()

    def get_page(self,url):
        while 1:
            self.http.open(url)
            if self.is_loggerd:
                return self.http.html_response
            else:
                self.login()

    def login(self):
        while 1:
            if self.is_logged:
                print 'logged nie potrzeba logowania'
                break
            print 'not logged loguje'
            self._do_login()

def dummy_callback(*args,**kwargs):
    pass

class WebControl(object):
    _modules = []
    def __init__(self,account,intervals=30):
        self.intervals = intervals
        self.account = account
        self._init_modules()
        
    def _init_modules(self):
        for module in self._modules:
            module(self.account,self)
            
    @classmethod
    def register_module(cls,module):
        cls._modules.append(module)    
        cls._register_callbacks(module)
        
    @classmethod
    def _register_callbacks(cls,module):
        for call_back in module.call_backs:
            setattr(cls,call_back,dummy_callback)
        
    # def __getattribute__(self,attr):
        # if attr.endswith('_callback'):
            # if attr not in self.__dict__:
                # return dummy_callback 
        # return super(SteamControll,self).__getattribute__(attr)
        
    def _proces_modules(self):
        for module in self._modules:
            module(self.account,self)()
            
    def loop(self):
        while 1:
            self._proces_modules()
            time.sleep(self.intervals)
            break

class WebModule(object):
    def __init__(self,account,controler):
        self.account = account
        self.controler = controler
        


if __name__ == "__main__":
    Bot('a','b')