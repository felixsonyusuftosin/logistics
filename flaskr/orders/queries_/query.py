from flaskr.utils.queries import Query


class QueryOrder(Query):
    def _insert_order(self, order_id):
        q = 'INSERT INTO orders (order_id) VALUES ("{}");'.format(
            order_id)
        cursor = self.execute_query(q)
        self.db.commit()

    def _insert_product(self, product_id, quantity, order_id, order_status, quantity_type):
        q = '''
            INSERT INTO 
              order_details (order_id, product_id, {}, order_status)
              VALUES ("{}", "{}", "{}", "{}");'''.format(quantity_type, order_id, product_id, quantity, order_status)
        cursor = self.execute_query(q)
        self.db.commit()

    def _update_product(self, product_id, quantity, order_id, order_status, quantity_type):
        q = '''
            UPDATE order_details SET {}={}  WHERE order_id={} AND product_id={}
            ;'''.format(quantity_type, quantity, order_id, product_id)
        cursor = self.execute_query(q)
        self.db.commit()
    def _get_order_by_id(self, order_id):
        q = 'SELECT order_id FROM orders where order_id={}'.format(order_id)
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        return rows

    def _get_product_by_product_id_order_id(self, product_id, order_id):
        q = 'SELECT * FROM order_details where order_id={} and product_id={}'.format(
            order_id, product_id)
        cursor = self.execute_query(q)
        row = cursor.fetchone()
        if row is None:
            return
        return self.convert_row_to_dict(row)
