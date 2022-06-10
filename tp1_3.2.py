# Parser

from itertools import islice
from treelib import Tree
import re


DATASET_PATH = 'amazon-meta.txt'

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
            # remove the length, and return the rest of the similar ids
            return attribute, value.split(' ')[1:]

        case _:
            return attribute, value


def parse_categories_and_add_to_the_tree(categories: list[str], gtree: Tree):
    t = Tree()
    t.create_node('sentinel', 0)
    category_regex = "\|([\w\s\,]*)\[(\d+)\]"

    name_id_pairs_seq = [re.findall(category_regex, c) for c in categories]
    leaves = set()

    for seq in name_id_pairs_seq:
        last_id = 0
        for name, id in seq:
            if id not in gtree and name != '':
                gtree.create_node(name, id, parent=last_id, data=last_id)
            if name != '':
                last_id = id

        leaves.add(seq[-1][1])

    return leaves


def parse_raw_product_data(lines: list[str], gtree: Tree):
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

    if len(raw_category_entries):
        attribute_map['category_leaves'] = parse_categories_and_add_to_the_tree(
            raw_category_entries, gtree)

    return Product(attribute_map)


with open(DATASET_PATH, 'r') as dataset:
    products = []
    current_product_lines = []
    global_tree = Tree()
    global_tree.create_node('sentinel', 0)

    # skip the first 3 lines
    for line in islice(dataset, 3, None):

        if line == '\n':
            if len(current_product_lines) > 0:
                product = parse_raw_product_data(
                    current_product_lines, global_tree)
                products.append(product)

            current_product_lines = []

        else:
            current_product_lines.append(line)

    global_tree.show()
