CREATE TABLE group (
  id SERIAL PRIMARY KEY,

  name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE amazonUser (
  id INT PRIMARY KEY
);

CREATE TABLE category (
  id INT PRIMARY KEY,

  categoryIdParent INT,
  categoryIdChild INT,

  name VARCHAR(100) NOT NULL,

  FOREIGN KEY(categoryIdParent) REFERENCES Category (id),
  FOREIGN KEY(categoryIdChild) REFERENCES Category (id)
);

CREATE TABLE product (
  asin INT PRIMARY KEY NOT NULL,

  groupId INT NOT NULL,

  title VARCHAR(100) NOT NULL,
  sales_rank INT NOT NULL,

  FOREIGN KEY(groupId) REFERENCES Group (id)
);

CREATE TABLE similarTo (
  productOriginAsin INT NOT NULL,
  productSimilarAsin INT NOT NULL,

  PRIMARY KEY (productOriginAsin, productSimilarAsin)

  FOREIGN KEY(productOriginAsin) REFERENCES Product (asin),
  FOREIGN KEY(productSimilarAsin) REFERENCES Product (asin)
);

CREATE TABLE productCategory (
  productAsin INT NOT NULL,
  categoryId INT NOT NULL,

  PRIMARY KEY (productAsin, categoryId),

  FOREIGN KEY(productAsin) REFERENCES Product (asin),
  FOREIGN KEY(categoryId) REFERENCES Category (id)
);

CREATE TABLE review (
  productAsin INT NOT NULL,
  userId INT NOT NULL,

  helpful INT,
  votes INT,
  rating INT,

  reviewedAt DATE NOT NULL,

  PRIMARY KEY (productAsin, userId),

  FOREIGN KEY(productAsin) REFERENCES Product (asin),
  FOREIGN KEY(userId) REFERENCES Category (id)
);