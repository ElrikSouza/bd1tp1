class Subscriptable:
    def __getitem__(self, key):

        return self.__getattribute__(key)


class ReviewEntries(Subscriptable):
    def __init__(self, date, customerId, rating, votes, helpful) -> None:
        self.date = date
        self.customerId = customerId
        self.rating = rating
        self.votes = votes
        self.helpful = helpful


class Review(Subscriptable):
    def __init__(self, total, downloaded, avgRating, entries: list[ReviewEntries]) -> None:
        self.total = total
        self.downloaded = downloaded
        self.avgRating = avgRating
        self.entries = entries
        self.asin = None

    def set_product_asin(self, asin):
        self.asin = asin


class Product(Subscriptable):

    def __init__(self, attribute_map: dict) -> None:
        self.asin = attribute_map.get('ASIN')
        self.title = attribute_map.get('title')
        self.group = attribute_map.get('group')
        self.salesrank = attribute_map.get('salesrank')
        self.similar = attribute_map.get('similar')
        self.review = attribute_map.get('review')
        self.categories = attribute_map.get('category_leaves')

        if self.review != None:
            self.review.set_product_asin(self.asin)

    def get_asin_leaf_category_tuples(self):
        return ((self.asin, category_id) for category_id in self.categories)


class Category(Subscriptable):
    def __init__(self, id, parent_category_id, name):
        self.id = int(id)
        self.parent_category_id = parent_category_id

        if parent_category_id == 0:
            self.parent_category_id = None

        self.name = name
