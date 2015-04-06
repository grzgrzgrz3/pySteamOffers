import unittest
from http import Browser
import os
import time
def delete_file_if_exist(filename):
    if os.path.isfile(os.path.abspath(filename)):
        os.remove(filename)
        
def creat_file_with_content(filename,content):
    with open(filename, "w") as f:
        f.write(content)
        
class test_browser(unittest.TestCase):
    def setUp(self):
        self.filename = 'test_file.cookie'
        delete_file_if_exist(self.filename)
        self.http = Browser(cookie_file_name=self.filename)
        
    def test_fetching_url(self):
        html_response = self.http.open('http://google.pl')
        self.assertIn('<html',html_response)
        
    def test_cookies_processing(self):
        self.http.open('http://google.pl')
        self.assertTrue(len(self.http.cj) > 0 )
        
    def test_cookies_from_file(self):
        creat_file_with_content(self.filename,"""#LWP-Cookies-2.0""")
        html_response = self.http.open('http://dota2bid.com')
        self.assertIn('youtube',html_response,
                      msg='content should have youtube video attached')
        
        file_data = """#LWP-Cookies-2.0
Set-Cookie3: first_visit=1; path="/"; domain="dota2bid.com"; path_spec; expires="2015-02-21 16:52:37Z"; version=0
        """
        creat_file_with_content(self.filename,file_data)
        html_response = self.http.open('http://dota2bid.com')
        self.assertNotIn('youtube',html_response,
                         msg='content should have youtube video attached')

    def tearDown(self):
        delete_file_if_exist(self.filename)
if __name__ == "__main__":
    unittest.main()