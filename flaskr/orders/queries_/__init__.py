from flaskr.orders.queries_.backlog_queries import BacklogQueries
from flaskr.orders.queries_.ready_queries import ReadyQueries
from flaskr.orders.queries_.ship_queries import ShipQueries

class Query(BacklogQueries, ReadyQueries, ShipQueries):
  pass




