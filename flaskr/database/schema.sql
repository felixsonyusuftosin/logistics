DROP TABLE IF EXISTS products;

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  mass_g int NOT NULL,
  product_name TEXT NOT NULL
);

DROP TABLE IF EXISTS stock;
CREATE TABLE stock (
  product_id INTEGER NOT NULL REFERENCES products (product_id),
  quantity INTEGER DEFAULT  0
);


CREATE VIEW IF NOT EXISTS v_stock
AS 
SELECT 
    p.product_id,
    p.mass_g,
    s.quantity As quantity,
    s.quantity * p.mass_g As available_mass_g
FROM 
   products as p
INNER JOIN stock as s ON s.product_id = p.product_id
