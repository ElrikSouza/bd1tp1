-- consulta A
-- Dado um produto, listar os 5 comentários mais úteis e com maior avaliação 
-- e os 5 comentários mais úteis e com menor avaliação
(
  SELECT *
  FROM review
  WHERE productAsin = 111
  ORDER BY helpful DESC, rating DESC
  LIMIT 5
)
UNION
(
  SELECT *
  FROM review
  WHERE productAsin = 111
  ORDER BY helpful DESC, rating ASC
  LIMIT 5
);

-- consulta B
-- Dado um produto, listar os produtos similares com maiores vendas do que ele
SELECT ps.asin, ps.groupId, ps.title, ps.sales_rank
FROM similarTo st
JOIN product po ON po.asin = st.productOriginAsin
JOIN product ps ON ps.asin = st.productSimilarAsin
WHERE (st.productOriginAsin = 111) AND (ps.sales_rank > po.sales_rank);

-- consulta C
-- Dado um produto, mostrar a evolução diária das médias de avaliação
-- ao longo do intervalo de tempo coberto no arquivo de entrada
SELECT p.title, r.reviewedAt, AVG(r.rating) as rating_avg
FROM product p
JOIN review r ON p.asin = r.productAsin
WHERE asin = 111
GROUP BY p.title, r.reviewedAt


-- As consultas abaixo tem todas a mesma essência de n-per-group
-- ver: https://stackoverflow.com/questions/1442527/how-to-select-the-newest-four-items-per-category/1442867#1442867
-- ver: https://stackoverflow.com/questions/2129693/using-limit-within-group-by-to-get-n-results-per-group

-- consulta D
-- Listar os 10 produtos líderes de venda em cada grupo de produtos

-- consulta E
-- Listar os 10 produtos com a maior média de avaliações úteis positivas por produto

-- consulta F
-- Listar a 5 categorias de produto com a maior média de avaliações úteis positivas por produto

-- consulta G
-- Listar os 10 clientes que mais fizeram comentários por grupo de produto
