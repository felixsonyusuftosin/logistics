# implement utils for prcessing requests
from flaskr.database import get_db
from flaskr.orders.queries_ import Query


class Process:
    ''' 
     Base class for processing orders  
     Includes a string representation of the class and also a method to check against the contraints of the app
    
    '''
    def __init__(self):
        self._cutoff_mass = 1800
        db = get_db()
        self._query = Query(db)

    def __repr__(self):
        backlog = self._query.get_backlog_items()
        ready = self._query.get_ready_items()
        shipped = self._query.get_shipped_items()
        return 'Backlog: {}\nReady Shipment: {}\nShipped: {}'.format(len(backlog), len(ready), len(shipped))

    def _update_stock(self, order):
        ''' method to ship the order and removes the order from stock '''
        ship_items = order['requested']
        for item in ship_items:
            self._query.remove_from_stock(item)
        print('updated stock {}'.format(order))
   

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
