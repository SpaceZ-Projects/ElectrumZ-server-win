

'''An enum-like type with reverse lookup.'''


class EnumError(Exception):
    pass


class Enumeration:

    def __init__(self, name, enumList):
        self.__doc__ = name

        lookup = {}
        reverseLookup = {}
        i = 0
        uniqueNames = set()
        uniqueValues = set()
        for x in enumList:
            if isinstance(x, tuple):
                x, i = x
            if not isinstance(x, str):
                raise EnumError("enum name {} not a string".format(x))
            if not isinstance(i, int):
                raise EnumError("enum value {} not an integer".format(i))
            if x in uniqueNames:
                raise EnumError("enum name {} not unique".format(x))
            if i in uniqueValues:
                raise EnumError("enum value {} not unique".format(x))
            uniqueNames.add(x)
            uniqueValues.add(i)
            lookup[x] = i
            reverseLookup[i] = x
            i = i + 1
        self.lookup = lookup
        self.reverseLookup = reverseLookup

    def __getattr__(self, attr):
        result = self.lookup.get(attr)
        if result is None:
            raise AttributeError('enumeration has no member {}'.format(attr))
        return result

    def whatis(self, value):
        return self.reverseLookup[value]
