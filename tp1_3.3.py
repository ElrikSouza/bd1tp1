import psycopg2
import os
import sys

class Queries:
  def __init__(self, conn):
    self.conn = conn
    self.cursor = conn.cursor()

  def query1(self):
    print('ASIN do produto:')
    product_asin = input()

    self.cursor.execute('''
        SELECT *
        FROM review
        WHERE product_asin = %s
        ORDER BY helpful DESC, rating DESC
        LIMIT 10
    ''', (product_asin,))

    os.system('clear')
    for record in self.cursor:
      print(f'ID da avaliação: {record[0]}')
      print(f'ASIN do produto: {record[1]}')
      print(f'ID do usuário: {record[2]}')
      print(f'Útil: {record[3]}')
      print(f'Votos: {record[4]}')
      print(f'Classificação: {record[5]}')
      print(f'Data da avaliação: {record[6]}')
      print('\n')

  def query2(self):
    print('ASIN do produto:')
    product_asin = input()

    self.cursor.execute('''
        SELECT po.asin AS origin_asin, po.title AS origin_title, po.sales_rank AS origin_sales_rank, 
          ps.asin AS similar_asin, ps.title AS similar_title, ps.sales_rank AS similar_sales_rank
        FROM similar_to st
        LEFT JOIN product po ON po.asin = st.product_origin_asin
        LEFT JOIN product ps ON ps.asin = st.product_similar_asin
        WHERE (st.product_origin_asin = %s) AND (ps.sales_rank < po.sales_rank)
    ''', (product_asin,))

    os.system('clear')
    for record in self.cursor:
      print(f'ASIN do produto original: {record[0]}')
      print(f'Título do produto original: {record[1]}')
      print(f'Classificação das vendas do produto original: {record[2]}')
      print(f'ASIN do produto similar: {record[3]}')
      print(f'Título do produto similar: {record[4]}')
      print(f'Classificação das vendas do produto similar: {record[5]}')
      print('\n')

  def query3(self):
    print('ASIN do produto:')
    product_asin = input()

    self.cursor.execute('''
        SELECT p.title, r.reviewed_at, AVG(r.rating) as rating_avg
        FROM product p
        LEFT JOIN review r ON p.asin = r.product_asin
        WHERE asin = %s
        GROUP BY p.title, r.reviewed_at
    ''', (product_asin,))

    os.system('clear')
    for record in self.cursor:
      print(f'Título do produto: {record[0]}')
      print(f'Data da avaliação: {record[1]}')
      print(f'Média de avaliação da classificação na data: {record[2]}')
      print('\n')

  def query4(self):
    self.cursor.execute('''
        SELECT name, asin, title, sales_rank, ranked_product_group
        FROM (
          SELECT *, rank() OVER (PARTITION BY product_group_id ORDER BY sales_rank ASC) ranked_product_group
          FROM product p
          LEFT JOIN product_group pg ON pg.id = p.product_group_id
        ) as ranked_products
        WHERE ranked_product_group <= 10 AND product_group_id IS NOT NULL
        ORDER BY product_group_id
    ''')

    os.system('clear')
    for record in self.cursor:
      print(record)
      print('\n')


  def query5(self):
    self.cursor.execute('''
        SELECT p.asin, p.title, avg(r.helpful) AS avg_helpful
        FROM review r
        LEFT JOIN product p ON P.asin = r.product_asin
        GROUP BY p.asin
        ORDER BY avg_helpful DESC
        LIMIT 10
    ''')
    
    os.system('clear')
    for record in self.cursor:
      print(f'ASIN do produto: {record[0]}')
      print(f'Título do produto: {record[1]}')
      print(f'Média de avaliações úteis: {record[2]}')
      print('\n')

  def query6(self):
    self.cursor.execute('''
        SELECT c.id, c.name, avg(r.helpful) as avg_helpful
        FROM review r
        LEFT JOIN product p ON p.asin = r.product_asin
        LEFT JOIN product_category pg ON pg.product_asin = p.asin
        LEFT JOIN category c ON c.id = pg.category_id
        GROUP BY c.id
        ORDER BY avg_helpful DESC
        LIMIT 5
    ''')

    os.system('clear')
    for record in self.cursor:
      print(f'ID da categoria: {record[0]}')
      print(f'Nome da categoria: {record[1]}')
      print(f'Média de avaliações úteis: {record[2]}')
      print('\n')

  def query7(self):
    self.cursor.execute('''
        SELECT name, user_id, reviews, ranked
        FROM (
          SELECT *, rank() OVER (PARTITION BY product_group_id ORDER BY reviews DESC) AS ranked
          FROM (
            SELECT pg.name, p.product_group_id, r.user_id, count(r.id) as reviews
            FROM review r
            LEFT JOIN product p ON r.product_asin = p.asin
            LEFT JOIN product_group pg ON pg.id = p.product_group_id
            GROUP BY pg.name, p.product_group_id, r.user_id
          )   grouped_products
          ORDER BY product_group_id, reviews DESC
        ) ranked_reviews
        WHERE ranked <= 10
    ''')

    os.system('clear')
    for record in self.cursor:
      print(f'Nome do grupo: {record[0]}')
      print(f'ID do usuário: {record[1]}')
      print(f'Quantidade de avaliações: {record[2]}')
      print(f'Rank: {record[3]}')
      print('\n')

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

def show_options():
  print_options()

  selected_query = int(input())
  while(selected_query < 1 or selected_query > 8):
    os.system('clear')
    print('Opção inválida. Digite novamente:')
    print_options()
    selected_query = int(input())
  
  if (selected_query == 1):
    queries.query1()
  elif (selected_query == 2):
    queries.query2()
  elif (selected_query == 3):
    queries.query3()
  elif (selected_query == 4):
    queries.query4()
  elif (selected_query == 5):
    queries.query5()
  elif (selected_query == 6):
    queries.query6()
  elif (selected_query == 7):
    queries.query7()
  else:
    sys.exit()

  show_options()
  
conn_string = 'user=postgres password=db host=localhost port=1999 dbname=bdtp1'
conn = psycopg2.connect(conn_string)
queries = Queries(conn)
show_options()