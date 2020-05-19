from flaskr.orders.initiate_order import ProcessInitiateOrder
from flaskr.orders.orders_backlog import ProcessBacklogOrders
from flaskr.orders.orders_ready import ProcessReadyOrders

class Orders(ProcessBacklogOrders, ProcessInitiateOrder, ProcessReadyOrders):
  pass 

