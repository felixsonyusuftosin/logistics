DROP TABLE IF EXISTS products;

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  mass_g int NOT NULL,
  product_name TEXT NOT NULL
);

CREATE TABLE STOCK (
  product_id INTEGER NOT NULL REFERENCES products (product_id),
  quantiy INTEGER NOT NULL DEFAULT 0

)