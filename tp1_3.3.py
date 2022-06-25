import psycopg2
import os
import sys


def clear_screen():
    os.system('clear')

def print_searching_data():
    print('Buscando dados...')


class QueryManager:
    def __init__(self, conn):
        self.conn = conn

    def _print_query1_result(self, reviews, product_asin):
        for product_title in reviews.keys():
            print(f'Produto {product_asin}: \'{product_title}\'\n')

            i = 1
            for review in reviews[product_title]:
                print(f'\t{i}. Data da avaliação: {review[6]} Usuário {review[2]}')
                print(f'\t\tÚtil: {review[3]}')
                print(f'\t\tVotos: {review[4]}')
                print(f'\t\tClassificação: {review[5]}\n')

                i += 1

            print()

    def _query1(self):
        clear_screen()

        print('ASIN do produto:')
        product_asin = input()

        clear_screen()

        print_searching_data()
        with self.conn.cursor() as curr:
            curr.execute('''
                SELECT p.title, p.asin, r.user_id, r.helpful, r.votes, r.rating, r.reviewed_at
                FROM review r
                LEFT JOIN product p ON p.asin = r.product_asin
                WHERE product_asin = %s
                ORDER BY helpful DESC, rating DESC
                LIMIT 10
	        ''', (product_asin,))
            clear_screen()

            reviews = dict()
            for record in curr:
                if record[0] not in reviews.keys():
                    reviews[record[0]] = []

                reviews[record[0]].append(record)
            
            self._print_query1_result(reviews, product_asin)

    def _print_query2_result(self, similars, product_asin):
        for product_title in similars.keys():
            print(f'Produto {product_asin}: \'{product_title}\'\n')

            i = 1
            for similar in similars[product_title]:
                print(f'\t{i}. Produto {similar[4]}: \'{similar[3]}\'')
                print(f'\t\tRanking das vendas: {similar[5]}\n')

                i += 1

            print()

    def _query2(self):
        clear_screen()

        print('ASIN do produto:')
        product_asin = input()

        clear_screen()

        print_searching_data()
        with self.conn.cursor() as curr:
            curr.execute('''
                SELECT po.title AS origin_title, po.asin AS origin_asin, po.sales_rank AS origin_sales_rank,
                ps.title AS similar_title, ps.asin AS similar_asin, ps.sales_rank AS similar_sales_rank
                FROM similar_to st
                LEFT JOIN product po ON po.asin = st.product_origin_asin
                LEFT JOIN product ps ON ps.asin = st.product_similar_asin
                WHERE (st.product_origin_asin = %s) AND (ps.sales_rank < po.sales_rank)
                ORDER BY ps.sales_rank ASC
            ''', (product_asin,))
            clear_screen()

            similars = dict()
            for record in curr:
                if record[0] not in similars.keys():
                    similars[record[0]] = []

                similars[record[0]].append(record)
            
            self._print_query2_result(similars, product_asin)

    def _print_query3_result(self, products, product_asin):
        for product_title in products.keys():
            print(f'Produto {product_asin} \'{product_title}\'\n')

            i = 1
            for product in products[product_title]:
                print(f'\t{i}. Data: {product[1]}')
                print(f'\t\tMédia de avaliações: {product[2]}\n')

                i += 1
            
            print()

    def _query3(self):
        clear_screen()

        print('ASIN do produto:')
        product_asin = input()

        clear_screen()

        print_searching_data()
        with self.conn.cursor() as curr:
            curr.execute('''
                SELECT p.title, r.reviewed_at, AVG(r.rating) AS rating_avg
                FROM product p
                LEFT JOIN review r ON p.asin = r.product_asin
                WHERE asin = %s
                GROUP BY p.title, r.reviewed_at
            ''', (product_asin,))
            clear_screen()

            products = dict()
            for record in curr:
                if record[0] not in products.keys():
                    products[record[0]] = []

                products[record[0]].append(record)
 
            self._print_query3_result(products, product_asin)

    def _print_query4_result(self, groups):
        for group_name in groups.keys():
            print(f'Grupo {group_name}\n')

            for product in groups[group_name]:
                print(f'\t{product[4]}. {product[2]} ({product[1]}) - Ranking de venda: {product[3]}')
            
            print()

    def _query4(self):
        clear_screen()

        print_searching_data()
        with self.conn.cursor() as curr:
            curr.execute('''
                SELECT name, asin, title, sales_rank, ranked_product_group
                FROM (
                SELECT *, rank() OVER (PARTITION BY product_group_id ORDER BY sales_rank ASC) ranked_product_group
                FROM product p
                LEFT JOIN product_group pg ON pg.id = p.product_group_id
                ) AS ranked_products
                WHERE ranked_product_group <= 10 AND product_group_id IS NOT NULL
                ORDER BY product_group_id
            ''')
            clear_screen()

            groups = dict()
            for record in curr:
                if record[0] not in groups.keys():
                    groups[record[0]] = []

                groups[record[0]].append(record)

            self._print_query4_result(groups)

    def _print_query5_result(self, record, rank):
        print(f'{rank}. Produto {record[0]} \'{record[1]}\'\n')
        print(f'\tMédia de avaliações úteis: {record[2]}\n')

    def _query5(self):
        clear_screen()

        print_searching_data()
        with self.conn.cursor() as curr:
            curr.execute('''
                SELECT p.asin, p.title, AVG(r.helpful) AS avg_helpful
                FROM review r
                LEFT JOIN product p ON P.asin = r.product_asin
                GROUP BY p.asin
                ORDER BY avg_helpful DESC
                LIMIT 10
            ''')
            clear_screen()

            i = 1
            for record in curr:
                self._print_query5_result(record, i)

                i += 1

    def _print_query6_result(self, record, rank):
        print(f'{rank}. Categoria {record[0]} \'{record[1]}\'\n')
        print(f'\tMédia de avaliações úteis: {record[2]}\n')

    def _query6(self):
        clear_screen()

        print_searching_data()
        with self.conn.cursor() as curr:
            curr.execute('''
                SELECT c.id, c.name, AVG(r.helpful) AS avg_helpful
                FROM review r
                LEFT JOIN product p ON p.asin = r.product_asin
                LEFT JOIN product_category pg ON pg.product_asin = p.asin
                LEFT JOIN category c ON c.id = pg.category_id
                GROUP BY c.id
                ORDER BY avg_helpful DESC
                LIMIT 5
            ''')
            clear_screen()

            i = 1
            for record in curr:
                self._print_query6_result(record, i)

                i += 1

    def _print_query7_result(self, groups):
        for group_name in groups.keys():
            print(f'Grupo {group_name}\n')

            for review in groups[group_name]:
                print(f'\t{review[3]}. Usuário {review[1]} - Quantidade de avaliações: {review[2]}')
        
            print()

    def _query7(self):
        clear_screen()

        print_searching_data()
        with self.conn.cursor() as curr:
            curr.execute('''
                SELECT name, user_id, reviews, ranked
                FROM (
                SELECT *, rank() OVER (PARTITION BY product_group_id ORDER BY reviews DESC) AS ranked
                FROM (
                    SELECT pg.name, p.product_group_id, r.user_id, COUNT(r.id) AS reviews
                    FROM review r
                    LEFT JOIN product p ON r.product_asin = p.asin
                    LEFT JOIN product_group pg ON pg.id = p.product_group_id
                    GROUP BY pg.name, p.product_group_id, r.user_id
                )   grouped_products
                ORDER BY product_group_id, reviews DESC
                ) ranked_reviews
                WHERE ranked <= 10
            ''')
            clear_screen()

            groups = dict()
            for record in curr:
                if (record[0] not in groups.keys()):
                    groups[record[0]] = []

                groups[record[0]].append(record)

            self._print_query7_result(groups)

    def execute_query(self, selected_query: int):
        if selected_query == 1:
            self._query1()
        elif selected_query == 2:
            self._query2()
        elif selected_query == 3:
            self._query3()
        elif selected_query == 4:
            self._query4()
        elif selected_query == 5:
            self._query5()
        elif selected_query == 6:
            self._query6()
        elif selected_query == 7:
            self._query7()
        else:
            sys.exit()


def print_options():
    print('Escolha uma das consultas disponíveis para executar:')
    print('(1) Dado um produto, listar os 5 comentários mais úteis e com maior avaliação e os 5 comentários mais úteis e com menor avaliação')
    print('(2) Dado um produto, listar os produtos similares com maiores vendas do que ele')
    print('(3) Dado um produto, mostrar a evolução diária das médias de avaliação ao longo do intervalo de tempo coberto no arquivo de entrada')
    print('(4) Listar os 10 produtos líderes de venda em cada grupo de produtos')
    print('(5) Listar os 10 produtos com a maior média de avaliações úteis positivas')
    print('(6) Listar a 5 categorias de produto com a maior média de avaliações úteis positivas')
    print('(7) Listar os 10 clientes que mais fizeram comentários por grupo de produto')
    print('(8) Sair')
    print('Opção escolhida:')


def get_query_option_input():
    print_options()

    selected_query = int(input())

    while selected_query < 1 or selected_query > 8:
        os.system('clear')
        print('Opção inválida. Digite novamente:')
        print_options()
        selected_query = int(input())

    return selected_query


def main_loop():
    conn_string = 'user=postgres password=db host=localhost port=1999 dbname=bdtp1'
    conn = psycopg2.connect(conn_string)
    queries = QueryManager(conn)

    while True:
        query_option = get_query_option_input()
        queries.execute_query(query_option)


main_loop()
