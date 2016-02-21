class LogFilter:
    def __init__(self, pidFilters, levelFilters, tagFilters):
        self._pidFilters = pidFilters
        self._levelFilters = levelFilters
        self._tagFilters = tagFilters
        self._result = []

    def parserFnc(self, entry):
        # PID filter
        if self._pidFilters:
            if not entry.pid in self._pidFilters:
                return True

        # Level filter
        if self._levelFilters:
            if not entry.level in self._levelFilters:
                return True

        # Tag filter
        if self._tagFilters:
            if not entry.tag in self._tagFilters:
                return True

        self._result.append(entry)

        return True

    def reset(self):
        self._result = []

    @property
    def result(self):
        return self._result
