class Parser(object):
    regex = None
    position = None
    linenumber = None
    separator = None

    def __init__(self, regex=None, position=None, linenumber=None, separator=None):
        self.regex = regex
        self.position = position
        self.separator = separator
        self.linenumber = linenumber

    def get_value(self, data):
        if self.regex is not None:
            return self._get_regex_value(data)

        if self.linenumber is not None and self.position is not None:
            return self._get_position_value(self._get_linenumber_value(data))
        if self.position is not None:
            return self._get_position_value(data)
        if self.linenumber is not None:
            return self._get_linenumber_value(data)

        return data

    def _get_regex_value(self, data):
        import re

        match = re.search(self.regex, data)
        if match is None:
            return None

        if len(match.groups()) > 0:
            return match.group(1)

        return match.group()

    def _get_position_value(self, data):
        if self.separator is None:
            raise ValueError("Separator not set")

        return data.split(self.separator)[self.position].strip()

    def _get_linenumber_value(self, data):
        return data.split("\n")[self.linenumber].strip()
