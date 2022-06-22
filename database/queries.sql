-- consulta A
-- Dado um produto, listar os 5 comentários mais úteis e com maior avaliação 
-- e os 5 comentários mais úteis e com menor avaliação
(
  SELECT *
  FROM review
  WHERE product_asin = '111'
  ORDER BY rating DESC, helpful DESC
  LIMIT 5
)
UNION
(
  SELECT *
  FROM review
  WHERE product_asin = '111'
  ORDER BY rating DESC, helpful ASC
  LIMIT 5
);

-- consulta B
-- Dado um produto, listar os produtos similares com maiores vendas do que ele
SELECT ps.*
FROM similar_to st
LEFT JOIN product po ON po.asin = st.product_origin_asin
LEFT JOIN product ps ON ps.asin = st.product_similar_asin
WHERE (st.product_origin_asin = '0827229534') AND (ps.sales_rank > po.sales_rank);

-- consulta C
-- Dado um produto, mostrar a evolução diária das médias de avaliação
-- ao longo do intervalo de tempo coberto no arquivo de entrada
SELECT p.title, r.reviewed_at, AVG(r.rating) as rating_avg
FROM product p
LEFT JOIN review r ON p.asin = r.product_asin
WHERE asin = '111'
GROUP BY p.title, r.reviewed_at

-- consulta D
-- Listar os 10 produtos líderes de venda em cada grupo de produtos
SELECT *
FROM (
  SELECT *, rank() OVER (PARTITION BY product_group_id ORDER BY sales_rank ASC) ranked_product_group
  FROM product
) as ranked_products
WHERE ranked_product_group <= 10 AND product_group_id IS NOT NULL
ORDER BY product_group_id

-- consulta E
-- Listar os 10 produtos com a maior média de avaliações úteis positivas por produto

-- consulta F
-- Listar a 5 categorias de produto com a maior média de avaliações úteis positivas por produto

-- consulta G
-- Listar os 10 clientes que mais fizeram comentários por grupo de produto
