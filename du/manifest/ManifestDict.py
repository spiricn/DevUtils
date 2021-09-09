from du.manifest.Exceptions import *


class ManifestDict:
    """
    Manifest parser helper class. Used mainly for type checking
    """

    def __init__(self, dictionary):
        """
        Constructor

        @param dictionary Source raw dictionary
        """

        # Check type
        if type(dictionary) != dict:
            raise ManifestParseError(
                "Invalid type: expected: %s , got: %s" % (dict, type(dictionary))
            )

        self._dictionary = dictionary

    def get(self, name):
        """
        Get a value of any type

        @param name Key name string or a list of name aliases
        """

        if isinstance(name, str):
            # Single name
            if name in self._dictionary:
                return self._dictionary[name]

        elif isinstance(name, tuple):
            # List of names (aliases)
            for i in name:
                if i in self._dictionary:
                    return self._dictionary[i]

        raise ManifestFieldMissingError("Required variable %r not defined" % str(name))

    def getDict(self, name):
        """
        Get a dictionary value

        @param name Key name
        """

        return ManifestDict(self.getType(name, dict))

    def getList(self, name, elementType=None):
        """
        Get a list value

        @param name Key name
        @param elementType List element type to check
        """

        value = self.getType(name, list)

        if elementType:
            for i in value:
                if type(i) != elementType:
                    raise ManifestParseError(
                        "Invalid list %r element type, expected:%s, got: %s"
                        % (name, elementType, type(i))
                    )

        return value

    def getStr(self, name):
        """
        Get a string value

        @param name Key name
        """

        return self.getType(name, str)

    def getType(self, name, valueType):
        """
        Get a value by type

        @param name Key name
        @param valueType Value type to check
        """

        value = self.get(name)

        if type(value) != valueType:
            raise ManifestParseError(
                "Invalid field %r type, expected: %s, got: %s"
                % (name, valueType, type(value))
            )

        return value

    @property
    def raw(self):
        """
        Raw dictionary
        """
        return self._dictionary
