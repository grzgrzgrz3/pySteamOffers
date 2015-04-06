import unittest
from html_to_obj import HtmlToObejct, SingleAggregation
from lxml import html

class HtmlAggregate(object):
    def __init__(self,cls):
        self.cls = cls
        
class AvatarImg(HtmlToObejct):
    PATTERN = './/div[contains(@class,"playerAvatar ")]'
    __html_builder__ = dict(image_url='//img/@src')
    def __init__(self,image_url=None,html=None):
        self.image_url = image_url
        super(AvatarImg,self).__init__(html)
        
class Friend(HtmlToObejct):
    PATTERN = './/div[contains(@class,"friendBlock ")]'
    __html_builder__ = dict(steamid='.//input[@class="friendCheckbox"]/@data-steamid',
                    avatar_multi = AvatarImg, 
                    avatar=SingleAggregation(AvatarImg))
    def __init__(self,steamid=None,avatar=None,html=None):
        self.steamid = steamid
        self.avatar = avatar
        super(Friend,self).__init__(html)

class steam_weblogin_test(unittest.TestCase):
    def setUp(self):
        test_html = open("test.htm").read()
        self._html = html.document_fromstring(test_html)
        self.friend = Friend(html=self._html.xpath(Friend.PATTERN)[0])
        self.avatar_url = "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/avatars/aa/aac40ad29acfefb78348bccf1c9a0a7ce23bb13a.jpg"
 
    def test_aggregation(self):
        friends = HtmlToObejct.proces_aggregate(self._html,Friend)
        self.assertTrue(len(friends) == 49)
    
    def test_initiation_object(self):
        self.assertEqual(self.friend.steamid,'76561197997039363')
    
    def test_single_inside_aggregation(self):
        self.assertEqual(self.friend.avatar.image_url,self.avatar_url)
    
    def test_multi_inside_aggregation(self):
        self.assertEqual(self.friend.avatar_multi[0].image_url,self.avatar_url)
        
    def test_normal_init(self):
        avatar = AvatarImg(image_url=self.avatar_url)
        steamid = '76561197997039363'
        friend = Friend(steamid,avatar)
        self.assertEqual(friend.steamid,steamid)
        self.assertEqual(friend.avatar.image_url,self.avatar_url)
if __name__ == '__main__':
    unittest.main()
