# Parser

from itertools import islice
from treelib import Tree
import re


DATASET_PATH = 'amazon-meta.txt'

NEXT_PRODUCT_DELIMITER = '\n'

ATTRIBUTES = ["Id:", "categories:", "ASIN:", "title:",
              "group:", "salesrank:", "similar:", "categories:"]


class ReviewEntries:
    def __init__(self, date, customerId, rating, votes, helpful) -> None:
        self.date = date
        self.customerId = customerId
        self.rating = rating
        self.votes = votes
        self.helpful = helpful


class Review:
    def __init__(self, total, downloaded, avgRating, entries: list[ReviewEntries]) -> None:
        self.total = total
        self.downloaded = downloaded
        self.avgRating = avgRating
        self.entries = entries


class Product:
    def __init__(self, attribute_map: dict) -> None:
        self.asin = attribute_map.get('ASIN')
        self.title = attribute_map.get('title')
        self.group = attribute_map.get('group')
        self.salesrank = attribute_map.get('salesrank')
        self.similar = attribute_map.get('similar')
        self.review = attribute_map.get('review')
        self.categories = attribute_map.get('category_leaves')


class Category:
    def __init__(self, id, parent_category_id, name):
        self.id = id
        self.parent_category_id = parent_category_id
        self.name = name


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
            return attribute, ' '.join(value)

        case "similar":
            # remove the length, and return the rest of the similar ASINs
            return attribute, value.split(' ')[1:]

        case _:
            return attribute, value


def parse_categories_and_add_to_the_tree(categories: list[str], gtree: CategoryHierarchy):
    category_regex = "\|([\w\s\,]*)\[(\d+)\]"

    name_id_pairs_seq = [re.findall(category_regex, c) for c in categories]
    leaves = set()

    for seq in name_id_pairs_seq:
        parent_id = 0
        for name, id in seq:
            # skip invalid categories
            if name == '':
                continue

            gtree.add_category(id, name, parent_id)
            parent_id = id

        leaves.add(seq[-1][1])

    return leaves


def parse_product_lines(lines: list[str], categoryHierarchy: CategoryHierarchy) -> Product:
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
                    total=total, downloaded=downloaded, avgRating=avgRating, entries=reviewEntries)

            case split_line if split_line[0].startswith('|'):
                raw_category_entries.append(' '.join(split_line))

            case [date,  'cutomer:', customerId, 'rating:', rating, 'votes:', votes, 'helpful:',   helpful]:
                entry = ReviewEntries(date, customerId, rating, votes, helpful)
                reviewEntries.append(entry)

        attribute_map['category_leaves'] = parse_categories_and_add_to_the_tree(
            raw_category_entries, categoryHierarchy)

    return Product(attribute_map)


with open(DATASET_PATH, 'r') as dataset:
    all_products = []
    current_product_lines = []

    category_hierarchy = CategoryHierarchy()

    # skip the first 3 lines
    for line in islice(dataset, 3, None):

        if line == NEXT_PRODUCT_DELIMITER:
            if len(current_product_lines) > 0:
                product = parse_product_lines(
                    current_product_lines, category_hierarchy)

                all_products.append(product)

            current_product_lines = []

        else:
            current_product_lines.append(line)

    category_hierarchy.show()
