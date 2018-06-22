from optopsy.enums import FilterType


class Filter(object):

    def __init__(self, filter_type, ideal, lower=None, upper=None):
        self.filter_type = filter_type
        self.ideal = ideal
        self.lower = lower
        self.upper = upper

    @property
    def name(self):
        """
        Filter name.
        """
        return self.__class__.__name__

    def __call__(self, target, quotes):
        raise NotImplementedError("%s not implemented!" % self.name)


class FilterStack(object):
    """
    A FilterStack runs multiple Filters until a failure is encountered.

    The purpose of an FilterStack is to group a logic set of Filters together. Each
    Filter in the stack is run. Execution stops if one Filter returns False.

    Args:
        * filters (list): List of filters.

    """

    def __init__(self, target, *filters):
        super(FilterStack, self).__init__()
        self.filters = filters
        self.target = target
        self.check_run_always = any(hasattr(x, 'run_always')
                                    for x in self.filters)

        # check if our data source has columns needed for certain filters
        for f in self.filters:
            if hasattr(f, 'required_fields'):
                if not all(fld in self.target.spread_data.columns for fld in f.required_fields):
                    raise ValueError("Required fields not in data source: ".join(f.required_fields))

    def execute(self, quotes):
        # normal running mode
        if not self.check_run_always:
            for f in self.filters:
                if not f(self.target, quotes):
                    return False
            return True
        # run mode when at least one filter has a run_always attribute
        else:
            # store result in res
            # allows continuation to check for and run
            # filters that have run_always set to True
            res = True
            for f in self.filters:
                if res:
                    res = f(self.target, quotes)
                elif hasattr(f, 'run_always'):
                    if f.run_always:
                        f(self.target, quotes)
            return res


class EntryAbsDelta(Filter):

    def __init__(self, ideal, lower, upper):
        super(EntryAbsDelta, self).__init__(FilterType.ENTRY, ideal, lower, upper)
        self.required_fields = ['delta']

    def __call__(self, target, quotes):
        return quotes.nearest('delta', self.ideal).between('delta', self.lower, self.upper)


class EntrySpreadPrice(Filter):

    def __init__(self, ideal, lower, upper):
        super(EntrySpreadPrice, self).__init__(FilterType.ENTRY, ideal, lower, upper)

    def __call__(self, target, quotes):
        return quotes.nearest('mark', self.ideal).between('mark', self.lower, self.upper)


class EntryDaysToExpiration(Filter):

    def __init__(self, ideal, lower, upper):
        super(EntryDaysToExpiration, self).__init__(FilterType.ENTRY, ideal, lower, upper)

    def __call__(self, target, quotes):
        return quotes.nearest('dte', self.ideal).between('dte', self.lower, self.upper)


class EntryDayOfWeek(Filter):

    def __init__(self, ideal):
        super(EntryDayOfWeek, self).__init__(FilterType.ENTRY, ideal)

    def __call__(self, target, quotes):
        print(target.now)


class ExitDaysToExpiration(Filter):

    def __init__(self, ideal):
        super(ExitDaysToExpiration, self).__init__(FilterType.ENTRY, ideal)
        self.type = FilterType.EXIT
        self.ideal = ideal

    def __call__(self, target, quotes):
        pass
