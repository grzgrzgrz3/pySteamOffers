import os
import json
import datetime
import requests
from .steamapi import errors
from .steamapi.core import APIConnection, APIResponse
from .steamapi.decorators import ArgsSingleton
import vdf


class SchemaInterface:
    schema = {}

    def __init__(self):
        pass

    @classmethod
    def _info_by_defindex(cls, defindex, app_id):
        """
        collecting all info about item from items_game_url and IEconItems,
        returning as dict
        """
        info = None
        schema = cls.schema[app_id]  # Schema(app_id)
        for item in schema.items:
            if item.defindex == defindex:
                info = item
        if not info:
            raise AttributeError("")
        game_item = schema.items_game.items[str(defindex)]
        # removing duplicates
        for key in info:
            if key in game_item:
                del game_item[key]
        info._update(game_item)
        return info

    @staticmethod
    def _quality_name(value, app_id):
        s = Schema(app_id)
        for f_name in s.qualities:
            if s.qualities[f_name] == value:
                return s.qualityNames[f_name]


def modification_date(file_):
    """checking when specify file was modificated, 
    returning datetime object"""
    t = os.path.getmtime(file_)
    # return time.ctime(os.path.getmtime(file))
    return datetime.datetime.fromtimestamp(t)


def http_date_format(date):
    """ converting datetime object to http If-Modified-Since header format
    date returning as string
    Example format:
    Sat, 29 Oct 1994 19:43:31 GMT
    """
    return date.strftime('%a, %d %b %Y %H:%M:%S GMT')


class ItemSchemaLoadFail(Exception):
    pass


class Schema(object):
    def __init__(self, app_id, language='en'):
        self._app_id = app_id
        self._language = language
        self._schema = None
        self._game_schema = None
        self._schema_file = 'schema_{app_id}.json'.format(app_id=app_id)
        self._game_schema_file = 'game_schema_{app_id}.json'.format(
            app_id=app_id)

    def _load(self, url=None):
        """
             loading items schema or game items schema             
        """
        headers = None
        file_name = self._game_schema_file if url else self._schema_file
        if os.path.isfile(file_name):
            last_modified = modification_date(file_name)
            last_modified_http = http_date_format(last_modified)
            headers = {'If-Modified-Since': last_modified_http}
        try:
            if url:
                response = requests.get(url, timeout=5, headers=headers)
                if 304 == response.status_code:
                    raise errors.APINotModified()
                # converting vdf (steam format) to normal json
                response_obj = vdf.convert(response.text)
            else:
                #raise requests.exceptions.ReadTimeout()
                response = APIConnection().call("IEconItems_%s" % self._app_id,
                                                "GetSchema", "v1", format='json', 
												language=self._language, headers=headers)
                response_obj = response.json()
                #response_obj = response
            if 'result' in response_obj:
                response_obj = response_obj['result']
            # storing pretty printed json schema string in file
            self._save_schema_to_file(file_name,
                                      json.dumps(response_obj, indent=4))
            return APIResponse(response_obj)
        except (errors.APINotModified, requests.exceptions.ReadTimeout, errors.APIError):
            # fetching from net failed, loading schema from file
            return self._load_from_file(file_name)

    def _save_schema_to_file(self, name, schema):
        """saving json object to file as string"""
        with open(name, 'w') as f:
            f.write(str(schema))

    def _load_from_file(self, file_):
        """loading schema from file, returning as APIResponse object"""
        if os.path.isfile(file_):
            schema_str = open(file_).read()
            schema = json.loads(schema_str)
            return APIResponse(schema)
        else:
            raise ItemSchemaLoadFail()

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