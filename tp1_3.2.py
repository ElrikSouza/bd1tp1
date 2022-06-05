# Parser

from itertools import islice


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


def split_product_data_line(line: str):
    return [f for f in line.strip().split(' ') if f != '']


def parse_simple_attribute(raw_attribute: str, raw_value):
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


# def parse_category_entry(category_entry: list[list]):
#     categories = ' '.join(category_entry).split('|')[1:]
#     name_id_pairs = [c[:-1].split('[') for c in categories]
#     category_id_name_map = {id: name for name, id in name_id_pairs}
#     print(category_id_name_map)


def parse_raw_product_data(lines: list[str]):
    attribute_map = {}
    reviewEntries = []

    while len(lines) > 0:
        split_line = split_product_data_line(lines.pop())

        match split_line:
            case[attribute, *value] if attribute in ATTRIBUTES:
                parsed_attribute, parsed_value = parse_simple_attribute(
                    attribute, ' '.join(value))
                attribute_map[parsed_attribute] = parsed_value

            case['reviews:', 'total:', total, 'downloaded:', downloaded, 'avg', 'rating:', avgRating]:
                attribute_map['review'] = Review(
                    total=total, downloaded=downloaded, avgRating=avgRating, entries=reviewEntries)

            case split_line if split_line[0].startswith('|'):
                # attribute_map['raw_category_entries'].append(
                #     parse_category_entry(split_line))
                continue

            case [date,  'cutomer:', customerId, 'rating:', rating, 'votes:', votes, 'helpful:',   helpful]:
                entry = ReviewEntries(date, customerId, rating, votes, helpful)
                reviewEntries.append(entry)

    return Product(attribute_map)


with open(DATASET_PATH, 'r') as dataset:
    products = []
    current_product_lines = []

    # skip the first 3 lines
    for line in islice(dataset, 3, None):

        if line == '\n':
            if len(current_product_lines) > 0:
                product = parse_raw_product_data(current_product_lines)
                products.append(product)

            current_product_lines = []

        else:
            current_product_lines.append(line)

    # for i in range(10):
    #     pprint(products[i])
    #     print('\n-------------------\n')
