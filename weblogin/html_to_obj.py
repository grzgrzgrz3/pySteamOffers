from lxml import html

class HtmlToObejct(object):
    def __init__(self,html):
        if html is not None:
            self._html = HtmlToObejct._load_html(html)
            self._proces()

    def _proces(self):
        """setting all attributes from __html_builder__"""
        for attr, value in self.__html_builder__.items():
            if callable(value):
                setattr(self,attr,
                        HtmlToObejct.proces_aggregate(self._html,value))
            else:
                nodes = self._html.xpath(value)
                if not nodes:
                    raise AttributeError("can't find %s attribute for class %s"%
                                            (attr,self.__class__.__name__))
                elif len(nodes) == 1:
                    nodes = nodes[0]
                setattr(self,attr,nodes)
                
    @classmethod            
    def _load_html(cls,_html):
        """checking if :param _html: is an string then converting it to html object and returning"""
        if isinstance(_html,str):
            _html = html.document_fromstring(_html)
        return _html
        
    @classmethod
    def proces_aggregate(cls,_html,aggregate):
        """
        finding all elements matching pattern returning list of instances
        :param _html: html code, this code is searched for object 
        :param aggregate:  class that we want instantized
        
        :return: list of object instatnized from :param aggregate:
        """
        _html = cls._load_html(_html)
        nodes = _html.xpath(aggregate.PATTERN)
        if isinstance(aggregate,SingleAggregation):
            return aggregate.cls(html=html.tostring(nodes[0]))
        else:
            return [aggregate(html=html.tostring(node)) for node in nodes]


class SingleAggregation(object):
    def __init__(self,cls):
        self.cls = cls
        self.PATTERN = cls.PATTERN
    def __call__(self):
        """ we need this magic method to get True from callable test """
        pass