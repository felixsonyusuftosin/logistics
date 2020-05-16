DROP TABLE IF EXISTS products;

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  mass_g int NOT NULL,
  product_name TEXT NOT NULL
)