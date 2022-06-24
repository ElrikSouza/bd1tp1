# Parser

import psycopg2
from psycopg2.extras import execute_batch
from parser import *
from entities import *


class DatabaseSeeder:
    def __init__(self, connection_string: str) -> None:
        self.conn = self._get_pgsql_connection(connection_string)

    def _get_pgsql_connection(self, connection_string: str):
        conn = psycopg2.connect(connection_string)

        return conn

    def _destroy_database_schema(self):
        cursor = self.conn.cursor()

        cursor.execute('''
        DROP TABLE IF EXISTS product_group CASCADE;
        DROP TABLE IF EXISTS amazon_user CASCADE;
        DROP TABLE IF EXISTS category CASCADE;
        DROP TABLE IF EXISTS product CASCADE;
        DROP TABLE IF EXISTS review CASCADE;
        DROP TABLE IF EXISTS similar_to CASCADE;
        DROP TABLE IF EXISTS product_category CASCADE;
        ''')

        self.conn.commit()
        cursor.close()

    def _load_database_schema(self) -> str:
        database_schema = []

        with open('database/create-tables.sql', 'r') as sql_file:
            database_schema = ' '.join(sql_file.readlines())

        return database_schema

    def _create_tables(self):
        cursor = self.conn.cursor()

        database_schema = self._load_database_schema()
        cursor.execute(database_schema)

        self.conn.commit()
        cursor.close()

    def _populate_categories_table(self, categories_iterator):
        print('[AVISO] Inserindo categorias')

        curr = self.conn.cursor()
        curr.execute('delete from category;')

        execute_batch(curr, '''
        insert into category (id, category_id_parent, name)
        values (%(id)s,%(parent_category_id)s,%(name)s)
        ''', categories_iterator, page_size=1000)

        self.conn.commit()
        curr.close()

    def _populate_product_group_table(self, product_groups_dict):
        print('[AVISO] Inserindo grupos de produtos')

        curr = self.conn.cursor()

        execute_batch(curr, '''
                INSERT INTO product_group(id, name) values
                (%s, %s)
            ''', ([id, name] for name, id in product_groups_dict.items()))

        self.conn.commit()
        curr.close()

    def _populate_amazon_users_table(self, user_ids):
        print('[AVISO] Inserindo usuarios')

        curr = self.conn.cursor()

        execute_batch(curr, '''
                INSERT INTO amazon_user(id) values
                (%s)
            ''', [[user_id] for user_id in user_ids], page_size=2000)

        self.conn.commit()
        curr.close()

    def _populate_product_table(self, products: list[Product]):
        print('[AVISO] Inserindo produtos')

        curr = self.conn.cursor()

        execute_batch(curr, '''
            INSERT INTO product(asin, product_group_id, title, sales_rank) values
            (%(asin)s,%(group)s,%(title)s, %(salesrank)s)
            ''', products, page_size=2000)

        self.conn.commit()
        curr.close()

    def _populate_similar_to_table(self, similar_to_pairs: list, product_asin_set):
        print('[AVISO] Inserindo tabela de produtos similares')

        curr = self.conn.cursor()

        similar_pairs_generator = ([the_product_id, similar_product_id] for the_product_id,
                                   similar_product_id in similar_to_pairs if similar_product_id in product_asin_set)

        execute_batch(curr, '''
            INSERT INTO similar_to(product_origin_asin, product_similar_asin) values
                    (%s, %s)
        ''', similar_pairs_generator, page_size=2000)

        self.conn.commit()
        curr.close()

    def _populate_product_leaf_category_table(self, asin_leaf_tuples):
        print('[AVISO] Inserindo folhas de categorias/asin')

        curr = self.conn.cursor()

        execute_batch(curr, '''
            INSERT INTO product_category(product_asin, category_id) values (%s,%s)
        ''', asin_leaf_tuples, page_size=2000)

        self.conn.commit()
        curr.close()

        return

    def a(self, asin, entries):
        return ([asin, review_entry.customerId,
                 review_entry.helpful, review_entry.votes, review_entry.rating, review_entry.date] for review_entry in entries)

    def _populate_review_entries_table(self, asin_review_entries_tuples):
        print('[AVISO] Inserindo reviews (vai demorar)')

        curr = self.conn.cursor()

        asin_entry_gen = chain.from_iterable(
            (self.a(asin, review_entries) for asin, review_entries in asin_review_entries_tuples))

        # a = (self._q(asin, review_entry) for asin, review_entry in ((asin, review_entry) in ))

        execute_batch(curr, '''
                            INSERT INTO review(product_asin,  user_id, helpful, votes, rating, reviewed_at)
                    VALUES
                    (%s, %s, %s, %s, %s, %s);
        ''', asin_entry_gen, page_size=10000)

        self.conn.commit()
        curr.close()

    def populate_database(self, dataset: Dataset):
        self._destroy_database_schema()
        self._create_tables()

        categories = dataset.category_hiearchy.get_width_iterator()
        self._populate_categories_table(categories)

        self._populate_product_group_table(dataset.product_group_dict)

        self._populate_amazon_users_table(list(dataset.amazon_users))

        self._populate_product_table(dataset.products)

        self._populate_product_leaf_category_table(
            dataset.get_product_asin_leaf_category_tuples())

        self._populate_similar_to_table(dataset.get_similar_to_pairs(), set(
            [product.asin for product in dataset.products]))

        self._populate_review_entries_table(
            dataset.get_product_asin_review_entries_tuples())

    def close(self):
        self.conn.close()


conn_string = 'user=postgres password=db host=localhost port=1999 dbname=bdtp1'
print('[AVISO] Lendo dados')
dataset = DatabaseParser().load_dataset()
print('[AVISO] Dados lidos')
seeder = DatabaseSeeder(conn_string)
seeder.populate_database(dataset)
seeder.close()
print('Os dados foram armazenados com sucesso')
