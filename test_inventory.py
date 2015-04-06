import unittest
from .schema import Schema, SchemaInterface, modification_date
from .steamapi.core import APIResponse, APIConnection

"""
  {
      "name": "Wex Ambience",
      "defindex": 10109,
      "item_class": "dota_item_wearable",
      "item_type_name": "Courier Effect",
      "item_name": "Wex Ambience",
      "item_quality": 4,
      "item_rarity"		"common"
"""

DEFINDEX = 4948
ITEM_NAME = "Ogre's Caustic Steel Choppers"
ITEM_RARITY = "uncommon"
API_KEY = '4B9F3F0BB554EFD9C6A52899DB695AA8'
APIConnection(API_KEY, 5)


class schema_test(unittest.TestCase):

    def test_argsSingleton(self):
        self.assertEqual(id(Schema(570)), id(Schema(570)))
        self.assertNotEqual(id(Schema(570)), id(Schema(470)))
        
    def test_load_from_file(self):
        schema = Schema(570)._load_from_file(Schema(570)._schema_file)
        self.assertIsInstance(schema, APIResponse)
        
    def test_load_from_file_when_http_fail(self):
        """
        api with schema for dota2(570) currently not working,
        so we can test loading from file when api fail
        """
        Schema(570)._load()
        self.assertIsInstance(Schema(570)._schema,APIResponse)
        
    def test_load_from_net(self):
        schema = Schema(440)._load()
        self.assertIsInstance(schema,APIResponse)

    def test_getattribute(self):
        Schema(570).items


class schema_interface_test(unittest.TestCase):
    def test_item_by_defindex(self):
        item = SchemaInterface._info_by_defindex(DEFINDEX,570)
        self.assertEqual(item.defindex,DEFINDEX)
        self.assertEqual(item.name,ITEM_NAME)
        self.assertEqual(item.item_rarity,ITEM_RARITY)
        
    def test_quality_name(self):
        item = SchemaInterface._info_by_defindex(5048,440)
        q_numer = item.item_quality
        self.assertEqual(SchemaInterface._quality_name(q_numer,440), 
                        "Unique")

if __name__ == '__main__':
    unittest.main()
