from .schema import SchemaInterface
from .steamapi.core import SteamObject


class ItemInfo(object):
    def __init__(self, defindex, app_id):
        self._defindex = defindex
        self._app_id = app_id
        self._schema = None

        self._info = None

    @property
    def info(self):
        """
        getting all item info from schema and game_schema
        """
        if not self._info:
            self._info = SchemaInterface._info_by_defindex(self._defindex,
                                                           self._app_id)
        return self._info

    @property
    def name(self):
        return self.info.name

    @property
    def rarity(self):
        try:
            return self.info.item_rarity
        except AttributeError:
            return 'common'

    @property
    def quality(self):
        return SchemaInterface._quality_name(self._quailty)


class Item(ItemInfo, SteamObject):
    def __init__(self, id, original_id, defindex, level, quality,
                 quantity, inventory, app_id, attributes=None):
        self._id = id
        self._level = level
        self._quality = quality
        self._quantity = quantity
        self._inventory = inventory
        self._attributes = attributes
        super(Item, self).__init__(defindex, app_id)
