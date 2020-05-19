DROP TABLE IF EXISTS products;

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  mass_g int NOT NULL,
  product_name TEXT NOT NULL
);

DROP TABLE IF EXISTS stock;
CREATE TABLE stock (
  product_id INTEGER NOT NULL PRIMARY KEY REFERENCES products (product_id),
  quantity INTEGER DEFAULT  0
);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  order_id INTEGER NOT NULL,
  position INTEGER PRIMARY KEY AUTOINCREMENT
);

DROP TABLE IF EXISTS order_details;
CREATE TABLE order_details (
  order_id INTEGER NOT NULL REFERENCES orders(order_id),
  order_status INTEGER NOT NULL DEFAULT 0,
  quantity_fulfilled INTEGER NOT NULL DEFAULT 0,
  quantity_unfulfilled INTEGER NOT NULL DEFAULT 0,
  quantity_shipped INTEGER NOT NULL DEFAULT 0,
  product_id INTEGER NOT NULL,
  id INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE VIEW IF NOT EXISTS v_backlog_orders
AS 
SELECT 
   d.order_id,
   d.order_status,
   d.quantity_unfulfilled as quantity,
   d.product_id,
   o.position
FROM 
   order_details as d 
LEFT JOIN orders as o ON d.order_id = o.order_id 
WHERE d.quantity_unfulfilled > 0;


CREATE VIEW IF NOT EXISTS v_ready_orders
AS 
SELECT 
   d.order_id,
   d.order_status,
   d.quantity_fulfilled as quantity,
   d.product_id,
   o.position
FROM 
   order_details as d 
LEFT JOIN orders as o ON d.order_id = o.order_id 
WHERE d.quantity_fulfilled > 0;


CREATE VIEW IF NOT EXISTS v_shipped_orders
AS 
SELECT 
   d.order_id,
   d.order_status,
   d.quantity_shipped as quantity,
   d.product_id,
   o.position
FROM 
   order_details as d 
LEFT JOIN orders as o ON d.order_id = o.order_id 
WHERE d.quantity_shipped > 0;


CREATE VIEW IF NOT EXISTS v_stock
AS 
SELECT 
    p.product_id,
    p.mass_g,
    s.quantity As quantity,
    s.quantity * p.mass_g As available_mass_g
FROM 
   products as p
INNER JOIN stock as s ON s.product_id = p.product_id;
