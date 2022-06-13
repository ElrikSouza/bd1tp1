CREATE TABLE Group (
  id SERIAL PRIMARY KEY,

  name VARCHAR(100) UNIQUE NOT NULL,
);

CREATE TABLE User (
  id INT PRIMARY KEY,
);

CREATE TABLE Category (
  id INT PRIMARY KEY,

  categoryIdParent INT,
  categoryIdChild INT,

  name VARCHAR(100) NOT NULL,

  FOREIGN KEY(categoryIdParent) REFERENCES Category (id),
  FOREIGN KEY(categoryIdChild) REFERENCES Category (id),
);

CREATE TABLE Product (
  asin INT PRIMARY KEY NOT NULL,

  groupId INT NOT NULL,

  title VARCHAR(100) NOT NULL,
  sales_rank INT NOT NULL,

  FOREIGN KEY(groupId) REFERENCES Group (id),
);

CREATE TABLE SimilarTo (
  productOriginAsin INT NOT NULL,
  productSimilarAsin INT NOT NULL,

  PRIMARY KEY (productOriginAsin, productSimilarAsin)

  FOREIGN KEY(productOriginAsin) REFERENCES Product (asin),
  FOREIGN KEY(productSimilarAsin) REFERENCES Product (asin),
);

CREATE TABLE ProductCategory (
  productAsin INT NOT NULL,
  categoryId INT NOT NULL,

  PRIMARY KEY (productAsin, categoryId),

  FOREIGN KEY(productAsin) REFERENCES Product (asin),
  FOREIGN KEY(categoryId) REFERENCES Category (id),
);

CREATE TABLE Review (
  productAsin INT NOT NULL,
  userId INT NOT NULL,

  date DATE NOT NULL,
  helpful INT,
  votes INT,
  rating INT,

  PRIMARY KEY (productAsin, userId),

  FOREIGN KEY(productAsin) REFERENCES Product (asin),
  FOREIGN KEY(userId) REFERENCES Category (id),
);