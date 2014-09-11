class SexQuerySetMixin(object):
    def male(self):
        return self.filter(sex='male')

    def female(self):
        return self.filter(sex='female')

    def unkwn_sex(self):
        """Filter QuerySet to records with unspecified or invalid sex values"""
        return self.exclude(sex__in=['male', 'female'])
