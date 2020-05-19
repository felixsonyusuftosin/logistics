from flaskr.orders.queries_.query import QueryOrder


class BacklogQueries(QueryOrder):

    def get_backlog_items(self):
        q = 'SELECT * FROM v_backlog_orders;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        list_rows = self.convert_rows_to_list(rows, cursor)
        return self._format_order_respone(list_rows)

    def add_order_to_backlog(self, order):
        requested = order['requested']
        order_id = order['order_id']
        order_status = 0
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
                                     order_id, order_status, 'quantity_unfulfilled')
            else:
                self._update_product(product_id, quantity,
                                     order_id, order_status, 'quantity_unfulfilled')

        return {'message': 'Successfully uploaded backlog items'}

    def clear_backlog_for_order(self, order_id):
        q = 'SELECT * FROM order_details where order_id={}'.format(order_id)
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        products = self.convert_rows_to_list(rows, cursor)
        for product in products:
            quantity_fulfilled = product['quantity_fulfilled'] + \
                product['quantity_unfulfilled']
            q = 'UPDATE order_details SET quantity_unfulfilled=0, quantity_fulfilled={} WHERE product_id={};'.format(
                quantity_fulfilled, product['product_id'])
            cursor = self.execute_query(q)
            self.db.commit()
        return
