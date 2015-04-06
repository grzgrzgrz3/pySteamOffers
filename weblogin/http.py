import  urllib2 
import urllib
from cookielib import LWPCookieJar,FileCookieJar
import os.path
 

class LWPSaveLoadCookieJar(LWPCookieJar,FileCookieJar):
    def __init__(self,filename):
        if not  os.path.isfile(os.path.abspath(filename)):
            self.create_empty_LWP_file(filename)
        FileCookieJar.__init__(self,filename)
        
    def create_empty_LWP_file(self,filename):
        f = open(filename, "w")
        f.write("#LWP-Cookies-2.0\n")
        f.close()

HTTPCookieProcessor = urllib2.HTTPCookieProcessor
class HTTPAutoCookieProcessor(HTTPCookieProcessor):
    """
        HTTPAutoCookieProcessor every response/request calls save/load method on cookie instance. 
        It makes sure your request cookies all always up to date with file_cookie.
    """
    def __init__(self,cookie=None):
        HTTPCookieProcessor.__init__(self, cookie)
    def http_request(self, request):
        self.cookiejar.load()
        return HTTPCookieProcessor.http_request(self,request)

    def http_response(self, request, response):
        response = HTTPCookieProcessor.http_response(self,request,response)
        self.cookiejar.save()
        return response
        
    https_request = http_request
    https_response = http_response
_DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'
class Browser(object):
    """
    **WARNING**
    If u do not pass cookie_file_name argument it will use 'default_cookies_file.cookie', every 
    instance of class will use same file. It may cause override/share cookies problems.
    """
    def __init__(self, user_agent = _DEFAULT_USER_AGENT,
                    cookie_file_name='default_cookies_file.cookie',
                    cookie_handler=LWPSaveLoadCookieJar):
        self.html_reponse = None
        self.user_agent = user_agent
        self.cookie_file_name = cookie_file_name
        self._build_opener(cookie_handler)
    
    def _build_opener(self,cookie_handler):
        self.cj = cookie_handler(self.cookie_file_name)
        self.opener = urllib2.build_opener(HTTPAutoCookieProcessor(self.cj),urllib2.HTTPSHandler(debuglevel=0))

    def open(self,url,data=None):
        req = self._build_request(url,data)
        self.last_request = self.opener.open(req)
        self.html_reponse =  self.last_request.read()
        return self.html_reponse
        
    def _build_request(self,url,data=None):
        if data:
            data = urllib.urlencode(data)
        req = urllib2.Request(url, data, {"User-Agent":self.user_agent})
        req.add_header('Connection', 'keep-alive')
        req.add_header('Accept-Encoding', 'deflate')
        req.add_header('Accept-Language', 'en-us;q=0.7,en;q=0.3')
        return req
    
    def save_html_response(self,filename):
        with open(filename,'wb') as f:
            f.write(self.html_reponse)
        
if  __name__ == "__main__":
    http=Browser(cookie_file_name='test_file.cookie')
    http.open('http://dota2bid.com')
    # http.cj in Cookie('','')