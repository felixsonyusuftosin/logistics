
from flaskr.orders.queries_.query import QueryOrder


class ShipQueries(QueryOrder):
    def commit_ship_orders(self, order):
        requested = order['requested']
        order_id = order['order_id']

        for req in requested:
            product_id = req['product_id']
            quantity = req['quantity']
            q = '''
                UPDATE order_details SET quantity_fulfilled=0, quantity_shipped={} WHERE order_id={} AND product_id={}
                ;'''.format(quantity, order_id, product_id)
            cursor = self.execute_query(q)
            self.db.commit()


    def get_shipped_items(self):
        q = 'SELECT * FROM v_shipped_orders;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        list_rows = self.convert_rows_to_list(rows, cursor)
        return self._format_order_respone(list_rows)
