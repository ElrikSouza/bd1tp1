class Subscriptable:
    def __getitem__(self, key):
        return self.__getattribute__(key)


class ReviewEntries(Subscriptable):
    __slots__ = ('date', 'customerId', 'rating', 'votes', 'helpful', 'asin')

    def __init__(self, date, customerId, rating, votes, helpful, asin) -> None:
        self.date = date
        self.customerId = customerId
        self.rating = rating
        self.votes = votes
        self.helpful = helpful
        self.asin = asin


class Product(Subscriptable):
    __slots__ = ("asin", "title", "group", "salesrank",
                 "similar", "review_entries", "categories")

    def __init__(self) -> None:
        self.asin = None
        self.title = None
        self.group = None
        self.salesrank = None
        self.similar = None
        self.categories = None
        self.review_entries = []

    def get_asin_leaf_category_tuples(self):
        '''Returns a generator of tuples containing the product asin and the id of one leaf category'''
        return ((self.asin, category_id) for category_id in self.categories)


class Category(Subscriptable):
    __slots__ = ("id", "parent_category_id", "name")

    def __init__(self, id, parent_category_id, name):
        self.id = int(id)
        self.parent_category_id = parent_category_id

        if parent_category_id == 0:
            self.parent_category_id = None

        self.name = name
