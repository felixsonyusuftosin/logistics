from flaskr.orders.orders import Process

class ProcessReadyOrders(Process):
    def process_ship_queue(self):
        to_ship = self._query.get_ready_items()
        for item in to_ship:
            self._query.commit_ship_orders(item)
        return

    def _set_order_into_ship_queue(self, order):
        ship_items = order['requested']
        if len(ship_items) > 0:
            self._query.add_order_to_ready_orders(order)
            self._update_stock(order)
        print('set order {} into ship queue'.format(order))
