# implement utils for prcessing requests
from flaskr.utils.queries import Query
from flaskr.database import get_db

class ProcessOrder:
    ''' Contain methods to process orders '''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProcessOrder, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._cutoff_mass = 1800
        self._unfulfilled_queue = self.Queue()
        db = get_db()
        self._query = Query(db)

    def enqueue(self, func, args=[], kwargs={}, high_priority=False):
        item = self.packCall(func, args, kwargs)
        return self._queue.enqueue(item, high_priority)

    def attempt_process_unfulfilled_orders(self):
        while self._unfulfilled_queue.has_more():
            element = self._unfulfilled_queue.dequeue()
            (func, args, kwargs) = element
            func(args, kwargs)
        return

    def packCall(self, func, args, kwargs):
        return (func, args, kwargs)

    def _pipeline_stock_constraint(self, **kwargs):
        ''' Run a pipe to check if what is available can fulfill the order '''
        order_quantity = kwargs['order_quantity']
        available_quantity = kwargs['available_quantity']
        order_mass = kwargs['order_mass']
        available_mass = kwargs['available_mass']
        if order_mass > available_mass:
            stockable_order = order_quantity - available_quantity
            unstockable_order = abs(stockable_order - order_quantity)
            return {'fillable': stockable_order, 'unfillable': unstockable_order}
        return {'fillable': order_quantity, 'unfillable': 0}

    def _pipeline_mass_constraint(self, **kwargs):
        ''' Run a pipe to check if the order does not exceed the allowable mass '''
        fulfilment_stats = kwargs['fulfilment_stats']
        order_mass = kwargs['order_mass']
        unit_mass = kwargs['unit_mass']
        fillable = fulfilment_stats['fillable']
        unfillable = fulfilment_stats['unfillable']
        fillable_mass = fillable * unit_mass
        if fillable_mass > self._cutoff_mass:
            excess_quantity = (self._cutoff_mass -
                                (fillable_mass))/order_mass
            fillable = fillable - abs(excess_quantity)
            unfillable = unfillable + abs(excess_quantity)
            return {'fillable': fillable, 'unfillable': unfillable}
        return fulfilment_stats

    def _compute_order_from_stock(self, order, stock, order_mass=0):
        available_mass = stock['available_mass_g']
        available_quantity = stock['quantity']
        unit_mass = stock['mass_g']
        order_mass = order['quantity'] * unit_mass
        order_quantity = order['quantity']
        product_id = stock['product_id']
        after_stock_constraint = self._pipeline_stock_constraint(
            order_quantity=order_quantity, available_quantity=available_quantity,
            order_mass=order_mass, available_mass=available_mass)
        after_pipeline_mass_constraint = self._pipeline_mass_constraint(
            fulfilment_stats=after_stock_constraint, order_mass=order_mass, unit_mass=unit_mass)
        # Todo update the stock table
        new_stock_quantity = available_quantity - \
            after_pipeline_mass_constraint['fillable']
        self._query.update_one_stock(
            {'product_id': product_id, 'quantity': new_stock_quantity})
        new_order_mass = (new_stock_quantity * unit_mass) + order_mass
        return {'fillable': after_pipeline_mass_constraint['fillable'],
                'unfillable': after_pipeline_mass_constraint['unfillable'], 'order_mass': new_order_mass}

    def initiate_order(self, order):
        order_id = order['order_id']
        requested = order['requested']
        order_mass = 0
        unfulfilled_orders = {'order_id': order_id, 'requested': []}
        fulfilled_orders = {'order_id': order_id, 'shipped': []}
        for req in requested:
            stock = self._query.get_stock_info(req['product_id'])
            processed_order = self._compute_order_from_stock(
                req, stock, order_mass)
            order_mass = processed_order['order_mass']
            unfulfilled_orders_quantity = processed_order['unfillable']
            fulfilled_orders_quantity = processed_order['fillable']
            unfulfilled_orders['requested'].append(
                {'product_id': req['product_id'], 'quantity': unfulfilled_orders_quantity})
            fulfilled_orders['shipped'].append(
                {'product_id': req['product_id'], 'quantity': unfulfilled_orders_quantity})
        if len(unfulfilled_orders['requested']) > 0:
            self.queue_unfulfilled_order(unfulfilled_orders, order_id)
        return self.ship_package(fulfilled_orders, unfulfilled_orders)

    def ship_package(self, order, unfulfilled):
        return 'Process: {}, unFulifilled: {}'.format(order, unfulfilled)

    def queue_unfulfilled_order(self, order, order_id):
        self._unfulfilled_queue.enqueue(self.initiate_order, [order_id, order])
        print(
            'Queued unfulfilled order with details {} to run un next restock '.format(order))

    class Queue:
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

