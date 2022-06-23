-- consulta A
-- Dado um produto, listar os 5 comentários mais úteis e com maior avaliação 
-- e os 5 comentários mais úteis e com menor avaliação
SELECT *
FROM review
WHERE product_asin = '0738700797'
ORDER BY helpful DESC, rating DESC
LIMIT 10

-- consulta B
-- Dado um produto, listar os produtos similares com maiores vendas do que ele
SELECT po.asin AS origin_asin, po.title AS origin_title, po.sales_rank AS origin_sales_rank, 
       ps.asin AS similar_asin, ps.title AS similar_title, ps.sales_rank AS similar_sales_rank
FROM similar_to st
LEFT JOIN product po ON po.asin = st.product_origin_asin
LEFT JOIN product ps ON ps.asin = st.product_similar_asin
WHERE (st.product_origin_asin = '0827229534') AND (ps.sales_rank < po.sales_rank);

-- consulta C
-- Dado um produto, mostrar a evolução diária das médias de avaliação
-- ao longo do intervalo de tempo coberto no arquivo de entrada
SELECT p.title, r.reviewed_at, AVG(r.rating) as rating_avg
FROM product p
LEFT JOIN review r ON p.asin = r.product_asin
WHERE asin = '0827229534'
GROUP BY p.title, r.reviewed_at

-- consulta D
-- Listar os 10 produtos líderes de venda em cada grupo de produtos
SELECT name, asin, title, sales_rank, ranked_product_group
FROM (
  SELECT *, rank() OVER (PARTITION BY product_group_id ORDER BY sales_rank ASC) ranked_product_group
  FROM product p
  LEFT JOIN product_group pg ON pg.id = p.product_group_id
) as ranked_products
WHERE ranked_product_group <= 10 AND product_group_id IS NOT NULL
ORDER BY product_group_id

-- consulta E
-- Listar os 10 produtos com a maior média de avaliações úteis positivas
SELECT p.asin, p.title, avg(r.helpful) AS avg_helpful
FROM review r
LEFT JOIN product p ON P.asin = r.product_asin
GROUP BY p.asin
ORDER BY avg_helpful DESC
LIMIT 10

-- consulta F
-- Listar a 5 categorias de produto com a maior média de avaliações úteis positivas
SELECT c.id, c.name, avg(r.helpful) as avg_helpful
FROM review r
LEFT JOIN product p ON p.asin = r.product_asin
LEFT JOIN product_category pg ON pg.product_asin = p.asin
LEFT JOIN category c ON c.id = pg.category_id
GROUP BY c.id
ORDER BY avg_helpful DESC
LIMIT 5

-- consulta G
-- Listar os 10 clientes que mais fizeram comentários por grupo de produto
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
