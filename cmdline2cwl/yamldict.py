from collections import OrderedDict


class UnsortableList(list):
    def sort(self, *args, **kwargs):
        pass


class YamlOrderedDict(OrderedDict):
    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))
