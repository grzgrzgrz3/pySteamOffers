import unittest
import mock
from schema import Schema  # , SchemaInterface
from steamapi.steamapi.core import APIConnection, APIResponse
from steamapi.steamapi import errors

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
APIConnection(API_KEY, 10)


'''
@unittest.skip('')
class schema_test(unittest.TestCase):

    def test_argsSingleton(self):
        self.assertEqual(id(Schema(570)),id(Schema(570)))
        self.assertNotEqual(id(Schema(570)),id(Schema(470)))
        
    def test_load_from_file(self):
        schema = Schema(570)._load_from_file(Schema(570)._schema_file)
        self.assertIsInstance(schema,APIResponse)
        
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

@unittest.skip('')
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
'''


class SchemaFlyweightTest(unittest.TestCase):

    def test_schema_flyweight_same_game(self):
        schema_570_1 = Schema(570)
        schema_570_2 = Schema(570)
        self.assertEqual(id(schema_570_2), id(schema_570_1))

    def test_schema_flyweight_different_game(self):
        schema_570 = Schema(570)
        schema_470 = Schema(470)
        self.assertNotEqual(id(schema_470), id(schema_570))

    def test_schema_call_init_once(self):
        with mock.patch('schema.Schema._load', spec=True,
                        return_value=True) as load_mock:
            schema_570 = Schema(570)
            assert schema_570.schema
            schema_570 = Schema(570)
            assert schema_570.schema
            self.assertEquals(load_mock.call_count, 1)

    def test_schema_caching_same_game(self):
        with mock.patch('schema.Schema._load', spec=True,
                        return_value=True) as load_mock:
            schema_570 = Schema(570)
            assert schema_570.schema
            assert schema_570.schema
            self.assertEquals(load_mock.call_count, 1)

    def test_schema_not_caching_different_games(self):
        with mock.patch('schema.Schema._load', spec=True,
                        return_value=True) as load_mock:
            schema_570 = Schema(570)
            schema_470 = Schema(470)
            assert schema_570.schema
            assert schema_470.schema
            self.assertEquals(load_mock.call_count, 2)

    def test_not_loading_without_call(self):
        with mock.patch('schema.Schema._load', spec=True,
                        return_value=True) as load_mock:
            Schema(570)
            self.assertFalse(load_mock.called)


class SchemaLoadTest(unittest.TestCase):

    @mock.patch('schema.requests',
                **{'request.side_effect': errors.APINotModified})
    def test_load_schema_from_file_not_modified(self, r):
        with mock.patch('schema.load_from_file',
                        spec=True) as from_file:
            schema_570 = Schema(570)
            assert schema_570.schema
            self.assertTrue(from_file.called)

    @mock.patch('schema.requests',
                **{'request.side_effect': errors.APINotModified})
    def test_load_game_schema_from_file_not_modified(self, r):
        test_dict = {'items_game_url': 'http://foo.pl'}
        with mock.patch('schema.load_from_file', spec=True,
                        return_value=APIResponse(test_dict)) as from_file:
            schema_570 = Schema(570)
            assert schema_570.game_schema
            self.assertEqual(from_file.call_count, 2)

    @mock.patch('schema.requests',
                **{'request.side_effect': errors.APIError})
    def test_load_schema_from_file_api_error(self, r):
        with mock.patch('schema.load_from_file',
                        spec=True) as from_file:
            schema_570 = Schema(570)
            assert schema_570.schema
            self.assertTrue(from_file.called)



if __name__ == '__main__':
    unittest.main()
