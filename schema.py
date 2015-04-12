import os
import json
import datetime
import requests
from requests.exceptions import ReadTimeout
from steamapi.steamapi import errors
from steamapi.steamapi.core import APIConnection, APIResponse
import vdf
import weakref


def modification_date(file_):
    """checking when specify file was modified,
    returning datetime object"""
    t = os.path.getmtime(file_)
    return datetime.datetime.fromtimestamp(t)


def http_date_format(date):
    """ converting datetime object to http If-Modified-Since header format
    date returning as string
    Example format:
    Sat, 29 Oct 1994 19:43:31 GMT
    """
    return date.strftime('%a, %d %b %Y %H:%M:%S GMT')


def http_last_modified_file(file_):
    """function checking when last time we modified file and building
    http headers with If-Modified-Since key.

    :param file_: path to file we want get last modified headers
    :return: dictionary object with If-Modified-Since date
    :rtype: dict
    """
    if os.path.isfile(file_):
        last_modified = modification_date(file_)
        last_modified_http = http_date_format(last_modified)
        return {'If-Modified-Since': last_modified_http}


def save_to_file(name, schema):
    """saving object to file as string"""
    with open(name, 'w') as f:
        f.write(str(schema))


def load_from_file(file_):
    """loading json object from file, returning as APIResponse object"""
    if os.path.isfile(file_):
        schema_str = open(file_).read()
        schema = json.loads(schema_str)
        return APIResponse(schema)
    raise ItemSchemaLoadFail()


class ItemSchemaLoadFail(Exception):
    pass


class Schema(object):
    _schemas = weakref.WeakValueDictionary()

    def __new__(cls, *args, **kwargs):
        key = "".join(map(str, args) + kwargs.values())
        schema = cls._schemas.get(key)
        if not schema:
            schema = super(Schema, cls).__new__(cls)
            cls._schemas[key] = schema
            schema._inited = False
        return schema

    def __init__(self, app_id, language='en'):
        if not self._inited:
            self._app_id = app_id
            self._language = language
            self._schema = None
            self._game_schema = None
            self._schema_file = 'schema_{app_id}.json'.format(app_id=app_id)
            self._game_schema_file = 'game_schema_{app_id}.json'.format(
                app_id=app_id)
            self._inited = True

    def _load(self, game=False):
        """loading items schema or game items schema"""
        file_name = self._game_schema_file if game else self._schema_file
        headers = http_last_modified_file(file_name)
        try:
            if game:
                response_obj = self._get_game_schema(headers)
            else:
                response_obj = self._get_schema(headers)
            # storing pretty printed json schema string in file
            save_to_file(file_name, json.dumps(response_obj, indent=4))
            return APIResponse(response_obj)
        except (errors.APINotModified, ReadTimeout,
                errors.APIError):
            # fetching from net failed, loading schema from file
            return load_from_file(file_name)

    def _get_game_schema(self, headers):
        response = requests.request('GET', self.schema.items_game_url, timeout=5, headers=headers)
        if 304 == response.status_code:
            raise errors.APINotModified()
        # converting vdf (steam format) to normal json
        return vdf.convert(response.text)

    def _get_schema(self, headers):
        response = APIConnection().call("IEconItems_%s" % self._app_id,
                                        "GetSchema", "v1", format='json',
                                        language=self._language,
                                        headers=headers)
        return response.json()['result']

    """
    def __getattribute__(self, attr):
        if attr.startswith('_'):
            return object.__getattribute__(self, attr)
        if not self._schema:
            self._schema = self._load()
        elif attr == 'items_game':
            if not self._game_schema:
                self._game_schema = self._load(self.items_game_url)
            return getattr(self._game_schema, attr)
        return getattr(self._schema, attr)
    """

    @property
    def schema(self):
        if not self._schema:
            self._schema = self._load()
        return self._schema

    @property
    def game_schema(self):
        if not self._game_schema:
            self._game_schema = self._load(True)
        return self._game_schema


class SchemaInterface(Schema):
    def info_by_defindex(self, defindex):
        """
        collecting all info about item from items_game_url and IEconItems,
        returning as APIResponse object
        """
        item = self._item_schema
        game_item = self.game_schema.items[str(defindex)]
        """
        # removing duplicates
        for key in item:
            if key in game_item:
                del game_item[key]
        """
        item.update_(game_item)
        return item

    def _item_schema(self, defindex):
        for item in self.schema.items:
            if item.defindex == defindex:
                return item
        raise AttributeError("Item with {0} defindex not found".format(defindex))

if __name__ == "__main__":
    # schema1 = Schema(570)
    # schema2 = Schema(570)
    # schema3 = Schema(470)
    # print schema1, schema2, schema3
    pass