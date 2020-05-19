from flaskr.orders.orders_backlog import ProcessBacklogOrders
from flaskr.orders.orders_ready import ProcessReadyOrders
from flaskr.orders.orders import Process

class ProcessInitiateOrder(Process):
    def initiate_order(self, order):
        ''' Called when we want to ship an order, checks the constraints and enqueue into ship queue as appropriate.'''

        order_id = order['order_id']
        requested = order['requested']
        order_mass = 0
        count = 0
        unfulfilled_orders = {'order_id': order_id, 'requested': []}
        fulfilled_orders = {'order_id': order_id, 'requested': []}

        while order_mass < self._cutoff_mass and count < len(requested):
            req = requested[count]
            stock = self._query.get_stock_info(req['product_id'])
            order_unit_mass = stock['mass_g']
            current_order_quantity = req['quantity']
            available_quantity = stock['quantity']
            product_id = req['product_id']

            fulfillable = self._check_order_constraint(
                self._cutoff_mass, current_order_quantity, order_unit_mass, available_quantity, order_mass)
            order_mass += fulfillable * order_unit_mass
            unfulfillable = abs(fulfillable - current_order_quantity)

            if (unfulfillable > 0):
                unfulfilled_orders['requested'].append(
                    {'product_id': product_id, 'quantity': unfulfillable})
            if (fulfillable > 0):
                fulfilled_orders['requested'].append(
                    {'product_id': product_id, 'quantity': fulfillable})
            count += 1
        ready_instance = ProcessReadyOrders()
        backlog_instance = ProcessBacklogOrders()
        ready_instance._set_order_into_ship_queue(fulfilled_orders)
        backlog_instance._set_order_into_backlog_queue(unfulfilled_orders)

        backlog = self._query.get_backlog_items()
        ready = self._query.get_ready_items()
        shipped = self._query.get_shipped_items()
        return 'Backlog: {}\nReady Shipment: {}\nShipped: {}'.format(len(backlog), len(ready), len(shipped))
