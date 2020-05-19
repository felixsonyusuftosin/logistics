CREATE TRIGGER IF NOT EXISTS 
  create_stock_from_catalog_insert
   AFTER INSERT
   ON products
   BEGIN 
     INSERT INTO stock (product_id, quantity) 
        VALUES (NEW.product_id, 0);
   END;


CREATE TRIGGER IF NOT EXISTS 
   delete_stock_from_catalog_delete
   AFTER DELETE
   ON products 
   BEGIN 
     DELETE from stock 
       WHERE  product_id=OLD.product_id;
   END;