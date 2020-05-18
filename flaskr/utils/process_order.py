# implement utils for prcessing requests
from flaskr.utils.queries import Query
from flaskr.database import get_db


class ProcessOrder:
    ''' Contain methods to process orders, a singleton for the purpose of maintaining queue states  '''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProcessOrder, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._cutoff_mass = 1800
        self._backlog_queue = self.__Queue()
        self._ship_queue = self.__Queue()

        db = get_db()

        self._query = Query(db)

    def initiate_order(self, order):
        ''' Called when we want to ship an order, checks the constraints and enqueue into ship queue as appropriate.'''

        order_id = order['order_id']
        requested = order['requested']
        order_mass = 0
        count = 0
        unfulfilled_orders = {'order_id': order_id, 'requested': []}
        fulfilled_orders = {'order_id': order_id, 'requested': []}

        while order_mass < self._cutoff_mass and count < len(requested) - 1:
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
                    {'product_id': product_id, 'quantity': unfulfillable})
            count += 1

        self._set_order_into_backlog_queue(fulfilled_orders)
        self._set_order_into_backlog_queue(unfulfilled_orders)

        return {
            'message':
            'Set processed orders: {} -- {} into shipment Queue Set unfulfillable orders: {} --{} into backlogQueue'
            .format(fulfillable, fulfilled_orders, unfulfillable, unfulfilled_orders)}

    def process_backlog_queue(self):
        while self._backlog_queue.has_more():
            element = self._backlog_queue.dequeue()
            (func, args, kwargs) = element
            self._ship_queue._enqueue(element)
        self.process_ship_queue()
        return

    def process_ship_queue(self):
        while self._ship_queue.has_more():
            element = self._ship_queue.dequeue()
            (func, args, kwargs) = element
            func(args, kwargs)
        return

    def _enqueue(self, func, args=[], kwargs={}, high_priority=False):
        item = self.packCall(func, args, kwargs)
        return self._queue.enqueue(item, high_priority)

    def _packCall(self, func, args, kwargs):
        return (func, args, kwargs)

    def _set_order_into_ship_queue(self, order):
        ship_items = order['requested']
        if len(ship_items) > 0:
            self._ship_queue.enqueue(
                self._ship_order, [order])
        print('set order {} into ship queue'.format(order))

    def _set_order_into_backlog_queue(self, order):
        requested = order['requested']
        if len(requested) > 0:
            self._backlog_queue.enqueue(self.initiate_order, [order])
        print('set order {} into backlog queue'.format(order))

    def _ship_order(self, order):
        ''' method to ship the order and removes the order from stock '''

        ship_items = order['requested']
        for item in ship_items:
            self._query.update_one_stock(item)
        print('shipped {}'.format(order))

    def _check_order_constraint(self, cutoff_mass, current_order_quantity, order_unit_mass, available_quantity, order_cumulated_mass):
        ''' util method to check constaints  '''

        if current_order_quantity == 0:
            return current_order_quantity

        def _check_availability():
            orders_abailable = 0
            excess_order = current_order_quantity - available_quantity
            if excess_order > 0:
                orders_available = available_quantity
            else:
                orders_available = current_order_quantity
            return orders_available

        def _check_mass_constraint(fillable_orders):
            if (order_unit_mass * fillable_orders) + order_cumulated_mass <= cutoff_mass or fillable_orders < 1:
                return fillable_orders
            fillable_orders = fillable_orders - 1
            return _check_mass_constraint(fillable_orders)
        _orders_available = _check_availability()
        fillable_orders = _check_mass_constraint(_orders_available)

        return fillable_orders

    class __Queue:
        ''' Utility queue class. '''

        def __init__(self):
            self._list = []

        def enqueue(self, item, high_priority):
            if high_priority:
                self._list.insert(0, item)
            else:
                self._list.append(item)
            return

        def has_more(self):
            return len(self._list) > 0

        def dequeue(self):
            return self._list.pop(0)
