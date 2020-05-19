
from flaskr.orders.queries_.query import QueryOrder


class ReadyQueries(QueryOrder):
    def add_order_to_ready_orders(self, order):
        requested = order['requested']
        order_id = order['order_id']
        order_status = 1
        existing_orders = self._get_order_by_id(order_id)
        order_exists = len(existing_orders) > 0

        if not order_exists:
            self._insert_order(order_id)

        for req in requested:
            product_id = req['product_id']
            quantity = req['quantity']
            existing_product = self._get_product_by_product_id_order_id(
                product_id, order_id)
            product_exists_in_order = existing_product is not None
            if not product_exists_in_order:
                self._insert_product(product_id, quantity,
                                     order_id, order_status, 'quantity_fulfilled')
            else:
                q = '''
                    UPDATE order_details SET quantity_fulfilled={} WHERE order_id={} AND product_id={}
                    ;'''.format(quantity, order_id, product_id)
                cursor = self.execute_query(q)
                self.db.commit()

        return {'message': 'Successfully uploaded items ready to ship'}

    def get_ready_items(self):
        q = 'SELECT * FROM v_ready_orders;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        list_rows = self.convert_rows_to_list(rows, cursor)
        return self._format_order_respone(list_rows)
