from itertools import islice, chain
from treelib import Tree
from entities import *
import re

DATASET_PATH = 'amazon-meta.txt'

NEXT_PRODUCT_DELIMITER = '\n'


class CategoryHierarchy:
    '''An abstraction to handle the product categories.'''

    def __init__(self) -> None:
        # This tree is used solely to obtain the correct order of insertion
        self._category_order = Tree()

        # This dictionary holds the actual data since the treelib's iterables don't come with the node's data
        # and require searching for the node again to get its content.
        # It's much faster and the memory overhead is not that noticiable.
        self._category_data = {}

        # auxiliary node that holds all the category branches together
        self._category_order.create_node('sentinel_node', 0)
        self._category_data[0] = (None, None)

    def add_category(self, id, name, parent_id):
        if id not in self._category_data:
            self._category_data[id] = (parent_id, name)
            self._category_order.create_node(identifier=id, parent=parent_id)

    def _get_node_data(self, node_id) -> Category:
        parent_id, name = self._category_data[node_id]

        return Category(node_id, parent_id, name)

    def get_width_iterator(self):
        '''Returns a generator that visits all nodes (skipping the sentinel node) by width/bfs order'''

        category_generator = (self._get_node_data(node)
                              for node in self._category_order.expand_tree(0, Tree.WIDTH))

        # skip the sentinel node
        return islice(category_generator, 1, None)


class Dataset:
    '''In-memory representation of the amazon sales dataset. It provides several generators to iterate over its data.'''

    def __init__(self) -> None:
        self._num_of_groups = 0
        self.products = list[Product]()
        self.category_hierarchy = CategoryHierarchy()
        self.unique_product_groups = set[str]()
        self.amazon_users = set[str]()
        self.product_group_dict = dict[str, str]()

    def _add_product_group(self, group):
        if group == None:
            return

        if group not in self.product_group_dict:
            self.product_group_dict[group] = self._num_of_groups
            self._num_of_groups += 1

    def add_product(self, product: Product):
        self.products.append(product)
        self._add_product_group(product.group)

        # replaces the name of the group by its id
        if product.group != None:
            product.group = self.product_group_dict[product.group]

        for review_entry in product.review_entries:
            self.amazon_users.add(review_entry.customerId)

    def add_category(self, id, name, parent_id):
        self.category_hierarchy.add_category(id, name, parent_id)

    def get_review_entries(self):
        '''Returns a generator with all the review entries of the dataset'''

        return chain.from_iterable((product.review_entries for product in self.products))

    def get_similar_to_pairs(self):
        '''Returns a generator of tuples containing the product asin and the asin of another similar product'''

        similar_to_list_generator = (
            [(product.asin, s) for s in product.similar] for product in self.products if product.similar != None)

        return chain.from_iterable(similar_to_list_generator)

    def get_product_asin_leaf_category_tuples(self):
        '''Returns a generator of tuples containing the product asin and a category it belongs to'''

        return chain.from_iterable((product.get_asin_leaf_category_tuples() for product in self.products))


class DatasetParser:
    '''Loads the dataset into a Dataset object'''

    def __init__(self) -> None:
        self._dataset = Dataset()

    def _parse_categories_and_add_to_the_tree(self, categories: list[str]):
        '''Parses a list of raw categories, adds them to the tree, and returns the ids of the leaves'''

        regex = "\|([\w\s\,]*)\[(\d+)\]"

        name_id_list_of_lists = [re.findall(regex, c) for c in categories]
        leaves = set()

        for name_id_list in name_id_list_of_lists:
            parent_id = 0

            for name, id in name_id_list:
                # skip invalid categories
                if name == '':
                    continue

                self._dataset.add_category(int(id), name, int(parent_id))
                parent_id = id

            name, id = name_id_list[-1]

            if name != '':
                leaves.add(id)

        return leaves

    def _split_product_data_line(self, line: str):
        '''Splits a line every empty space and removes empty strings from the final array'''

        return [line_fragment for line_fragment in line.strip().split(' ') if line_fragment != '']

    def _parse_product_lines(self, lines: list[str]) -> Product:
        '''Parses an array of lines from the dataset and returns the parsed product'''

        raw_category_entries = []
        product = Product()

        for line in lines:
            split_line = self._split_product_data_line(line)

            match split_line:
                case ["ASIN:", asin]:
                    product.asin = asin

                case ["title:", *split_title]:
                    title = ' '.join(split_title)
                    product.title = title

                case ["group:", *group]:
                    product.group = ' '.join(group)

                case ["salesrank:", salesrank]:
                    product.salesrank = int(salesrank)

                case ["similar:", _, *similar_products]:
                    product.similar = similar_products

                # a line containing a category hieararchy always starts with '|'
                case split_line if split_line[0].startswith('|'):
                    raw_category = ' '.join(split_line)
                    raw_category_entries.append(raw_category)

                case [date,  'cutomer:', customerId, 'rating:', rating, 'votes:', votes, 'helpful:', helpful]:
                    entry = ReviewEntries(
                        date, customerId, int(rating), int(votes), int(helpful), product.asin)
                    product.review_entries.append(entry)

        product.categories = self._parse_categories_and_add_to_the_tree(
            raw_category_entries)

        return product

    def load_dataset(self) -> Dataset:
        '''Loads the dataset into a Dataset object'''

        with open(DATASET_PATH, 'r') as dataset:

            current_product_lines = []

            # skip the first 3 lines since they are useless
            for line in islice(dataset, 3, None):

                if line == NEXT_PRODUCT_DELIMITER:
                    if len(current_product_lines) > 0:
                        product = self._parse_product_lines(
                            current_product_lines)

                        self._dataset.add_product(product)

                    current_product_lines = []

                else:
                    current_product_lines.append(line)

        # reset the internal state and eject the dataset object
        dataset = self._dataset
        self._dataset = Dataset()

        return dataset
