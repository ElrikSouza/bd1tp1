CREATE TABLE product_group (
  id SERIAL PRIMARY KEY,

  name VARCHAR(15) UNIQUE NOT NULL
);

CREATE TABLE amazon_user (
  id INT PRIMARY KEY
);

CREATE TABLE category (
  id INT PRIMARY KEY,

  category_id_parent INT,

  name VARCHAR(100) NOT NULL,

  FOREIGN KEY(category_id_parent) REFERENCES category(id),
);

CREATE TABLE product (
  asin INT PRIMARY KEY NOT NULL,

  product_group_id INT NOT NULL,

  title VARCHAR(100) NOT NULL,
  sales_rank INT NOT NULL,

  FOREIGN KEY(product_group_id) REFERENCES product_group(id)
);

CREATE TABLE similar_to (
  product_origin_asin INT NOT NULL,
  product_similar_asin INT NOT NULL,

  PRIMARY KEY (product_origin_asin, product_similar_asin),

  FOREIGN KEY(product_origin_asin) REFERENCES product(asin),
  FOREIGN KEY(product_similar_asin) REFERENCES product(asin)
);

CREATE TABLE product_category (
  product_asin INT NOT NULL,
  category_id INT NOT NULL,

  PRIMARY KEY (product_asin, category_id),

  FOREIGN KEY(product_asin) REFERENCES product(asin),
  FOREIGN KEY(category_id) REFERENCES category(id)
);

CREATE TABLE review (
  product_asin INT NOT NULL,
  user_id INT NOT NULL,

  helpful INT,
  votes INT,
  rating INT,

  reviewed_at DATE NOT NULL,

  PRIMARY KEY (product_asin, user_id),

  FOREIGN KEY(product_asin) REFERENCES product(asin),
  FOREIGN KEY(user_id) REFERENCES amazon_user(id)
);