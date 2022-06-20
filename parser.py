from itertools import islice, chain
from treelib import Tree
from entities import *
import re

DATASET_PATH = 'amazon-meta.txt'

NEXT_PRODUCT_DELIMITER = '\n'

ATTRIBUTES = ["Id:", "categories:", "ASIN:", "title:",
              "group:", "salesrank:", "similar:", "categories:"]


def split_product_data_line(line: str):
    return [f for f in line.strip().split(' ') if f != '']


def parse_key_value_attribute(raw_attribute: str, raw_value):
    attribute = raw_attribute.strip()[:-1]
    value = raw_value.strip()

    match attribute:
        # attributes that have int values
        case "Id" | "categories" | "salesrank":
            return attribute, int(value)

        case "ASIN":
            return attribute, value

        case "title":
            return attribute, ''.join(value)

        case "similar":
            # remove the length, and return the rest of the similar ASINs
            return attribute, value.split(' ')[1:]

        case _:
            return attribute, value


class CategoryHierarchy:
    def __init__(self) -> None:
        self.category_tree = Tree()

        # auxiliary node that holds all the category branches together
        self.category_tree.create_node('sentinel_node', 0)

    def add_category(self, id, name, parent_id):
        if id not in self.category_tree:
            self.category_tree.create_node(
                name, id, parent=parent_id, data=parent_id)

    def _get_node_data(self, node_id) -> Category:
        node = self.category_tree[node_id]

        return Category(node.identifier, node.data, node.tag)

    def get_width_iterator(self):
        category_generator = (self._get_node_data(node)
                              for node in self.category_tree.expand_tree(0, Tree.WIDTH))
        # skip the sentinel node
        return islice(category_generator, 1, None)

    def show(self):
        self.category_tree.show()


class Dataset:
    def __init__(self) -> None:
        self.num_of_groups = 0
        self.products = list[Product]()
        self.category_hiearchy = CategoryHierarchy()
        self.unique_product_groups = set[str]()
        self.amazon_users = set[str]()
        self.product_group_dict = dict[str, str]()

    def _add_product_group(self, group):
        if group == None:
            return

        if group not in self.product_group_dict.keys():
            self.product_group_dict[group] = self.num_of_groups
            self.num_of_groups += 1

    def add_product(self, product: Product):
        self.products.append(product)
        self._add_product_group(product.group)

        if product.group != None:
            product.group = self.product_group_dict[product.group]

        if product.review != None:
            for review_entry in product.review.entries:
                self.amazon_users.add(review_entry.customerId)

    def add_category(self, id, name, parent_id):
        self.category_hiearchy.add_category(id, name, parent_id)

    def get_product_asin_review_entries_tuples(self):
        '''Returns a generator of tuples containing the product asin and the review entries of that product'''

        products_with_reviews = (
            product for product in self.products if product.review != None)

        asin_entries_tuples_list_generator = (
            (product.asin, product.review.entries) for product in products_with_reviews)

        return asin_entries_tuples_list_generator

    def get_similar_to_pairs(self):
        similar_to_list_generator = (
            [(product.asin, s) for s in product.similar] for product in self.products if product.similar != None)

        return chain.from_iterable(similar_to_list_generator)

    def get_product_asin_leaf_category_tuples(self):
        return chain.from_iterable((product.get_asin_leaf_category_tuples() for product in self.products))


class DatabaseParser:
    def __init__(self) -> None:
        self._dataset = Dataset()

    def _parse_categories_and_add_to_the_tree(self, categories: list[str]):
        category_regex = "\|([\w\s\,]*)\[(\d+)\]"

        name_id_pairs_seq = [re.findall(category_regex, c) for c in categories]
        leaves = set()

        for seq in name_id_pairs_seq:
            parent_id = 0
            for name, id in seq:
                # skip invalid categories
                if name == '':
                    continue

                self._dataset.add_category(int(id), name, int(parent_id))
                parent_id = id

            name, id = seq[-1]
            if name != '':
                leaves.add(id)

        return leaves

    def _parse_product_lines(self, lines: list[str]) -> Product:
        attribute_map = {}
        raw_category_entries = []
        reviewEntries = []

        while len(lines) > 0:
            split_line = split_product_data_line(lines.pop())

            match split_line:
                case[attribute, *value] if attribute in ATTRIBUTES:
                    parsed_attribute, parsed_value = parse_key_value_attribute(
                        attribute, ' '.join(value))
                    attribute_map[parsed_attribute] = parsed_value

                case['reviews:', 'total:', total, 'downloaded:', downloaded, 'avg', 'rating:', avgRating]:
                    attribute_map['review'] = Review(
                        total=int(total), downloaded=int(downloaded), avgRating=float(avgRating), entries=reviewEntries)

                case split_line if split_line[0].startswith('|'):
                    raw_category_entries.append(' '.join(split_line))

                case [date,  'cutomer:', customerId, 'rating:', rating, 'votes:', votes, 'helpful:',   helpful]:
                    entry = ReviewEntries(
                        date, customerId, int(rating), int(votes), int(helpful))
                    reviewEntries.append(entry)

            attribute_map['category_leaves'] = self._parse_categories_and_add_to_the_tree(
                raw_category_entries)

        return Product(attribute_map)

    def load_dataset(self) -> Dataset:

        with open(DATASET_PATH, 'r') as dataset:

            current_product_lines = []

            # skip the first 3 lines
            for line in islice(dataset, 3, None):

                if line == NEXT_PRODUCT_DELIMITER:
                    if len(current_product_lines) > 0:
                        product = self._parse_product_lines(
                            current_product_lines)

                        self._dataset.add_product(product)

                    current_product_lines = []

                else:
                    current_product_lines.append(line)

        dataset = self._dataset
        self._dataset = Dataset()

        return dataset
