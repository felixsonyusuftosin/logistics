from flaskr.orders.orders import Process


class ProcessBacklogOrders(Process):
    def process_backlog_queue(self):
        to_ship = self._query.get_backlog_items()
        for item in to_ship:
            self.initiate_order(item)
        return

    def _set_order_into_backlog_queue(self, order):
        requested = order['requested']
        if len(requested) > 0:
            self._query.add_order_to_backlog(order)
        else:
            self._query.clear_backlog_for_order(order['order_id'])
  
