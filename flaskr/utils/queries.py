# Define sql queries here
from flaskr.utils.exceptions import DatabaseWriteError
import sqlite3
import json
from collections import defaultdict


class Query():
    def __init__(self, db):
        self.db = db
    ''' 
    Catalog queryies. 
    ------------------------
    '''

    def load_single_catalog(self, catalog):
        q = '''INSERT INTO products
          (product_id, mass_g, product_name)
          VALUES 
        ("{}", "{}", "{}");
        '''.format(catalog['product_id'], catalog['mass_g'], catalog['product_name'])
        cursor = self.execute_query(q)
        self.db.commit()

    def load_all_catalogs(self, catalogs):
        for catalog in catalogs:
            self.load_single_catalog(catalog)
        return {'message': 'Successfully captured all the catalog items'}

    def read_all_catalogs(self):
        q = 'SELECT * FROM products;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        return self.convert_rows_to_list(rows, cursor)

    ''' 
    Stock queryies. 
    ------------------------
    '''
    def get_one_stock(self, product_id):
      q = 'SELECT * FROM stock WHERE product_id={}'.format(product_id)
      cursor = self.execute_query(q)
      row = cursor.fetchone()
      return self.convert_row_to_dict(row)

    def update_one_stock(self, stock):
        q = 'UPDATE stock SET quantity={} WHERE product_id = {}'.format(
            stock['quantity'], stock['product_id'])
        cursor = self.execute_query(q)
        self.db.commit()

    def remove_from_stock(self, stock):
        old_stock = self.get_one_stock(stock['product_id'])
        new_quantity = old_stock['quantity'] - stock['quantity']
        if new_quantity < 0:
          new_quantity = 0
        stock['quantity'] = new_quantity
        q = 'UPDATE stock SET quantity={} WHERE product_id = {}'.format(
            stock['quantity'], stock['product_id'])
        cursor = self.execute_query(q)
        self.db.commit()

    def read_all_stocks(self):
        q = 'SELECT * FROM stock;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        return self.convert_rows_to_list(rows, cursor)

    def update_stocks(self, stocks):
        for stock in stocks:
            q = 'SELECT quantity FROM stock WHERE product_id={}'.format(
                stock['product_id'])
            cursor = self.execute_query(q)
            row = cursor.fetchone()
            old_quantity = self.convert_row_to_dict(row)['quantity']
            new_quantity = stock['quantity'] + old_quantity
            stock['quantity'] = new_quantity
            self.update_one_stock(stock)
        return {'message': 'successfully updated all stocks'}

    ''' 
    Stock_view queries. 
    ------------------------
    '''

    def get_stock_info(self, product_id):
        q = 'SELECT * from v_stock WHERE v_stock.product_id ={};'.format(
            product_id)
        cursor = self.execute_query(q)
        row = cursor.fetchone()
        return self.convert_row_to_dict(row)

    '''
    order queries
    '''

    def _get_order_by_id(self, order_id):
        q = 'SELECT order_id FROM orders where order_id={}'.format(order_id)
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        return rows

    def _get_product_by_product_id_order_id(self, product_id, order_id):
        q = 'SELECT * FROM order_details where order_id={} and product_id={}'.format(
            order_id, product_id)
        cursor = self.execute_query(q)
        row = cursor.fetchone()
        if row is None:
            return
        return self.convert_row_to_dict(row)

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

    def commit_ship_orders(self, order):
      requested = order['requested']
      order_id = order['order_id']

      for req in requested:
          product_id = req['product_id']
          quantity = req['quantity']
          q = '''
            UPDATE order_details SET quantity_fulfilled=0, quantity_shipped={} WHERE order_id={} AND product_id={}
            ;'''.format(quantity, order_id, product_id)
          cursor = self.execute_query(q)
          self.db.commit()

    def get_backlog_items(self):
        q = 'SELECT * FROM v_backlog_orders;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        list_rows = self.convert_rows_to_list(rows, cursor)
        return self._format_order_respone(list_rows)

    def get_ready_items(self):
        q = 'SELECT * FROM v_ready_orders;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        list_rows = self.convert_rows_to_list(rows, cursor)
        return self._format_order_respone(list_rows)

    def get_shipped_items(self):
        q = 'SELECT * FROM v_shipped_orders;'
        cursor = self.execute_query(q)
        rows = cursor.fetchall()
        list_rows = self.convert_rows_to_list(rows, cursor)
        return self._format_order_respone(list_rows)

    def _insert_order(self, order_id):
        q = 'INSERT INTO orders (order_id) VALUES ("{}");'.format(
            order_id)
        cursor = self.execute_query(q)
        self.db.commit()

    def _insert_product(self, product_id, quantity, order_id, order_status, quantity_type):
        q = '''
              INSERT INTO 
                order_details (order_id, product_id, {}, order_status)
                VALUES ("{}", "{}", "{}", "{}");'''.format(quantity_type, order_id, product_id, quantity, order_status)
        cursor = self.execute_query(q)
        self.db.commit()

    def _update_product(self, product_id, quantity, order_id, order_status, quantity_type):
        q = '''
              UPDATE order_details SET {}={}  WHERE order_id={} AND product_id={}
              ;'''.format(quantity_type, quantity, order_id, product_id)
        cursor = self.execute_query(q)
        self.db.commit()

    '''
     Utility Methods
     ------------------------
    '''

    def execute_query(self, query):
        try:
            cursor = self.db.execute(query)
            return cursor
        except sqlite3.Error as e:
            print(e)
            raise DatabaseWriteError(
                'Database error {}'.format(e), status_code=500)
        except Exception as e:
            print(e)
            raise DatabaseWriteError(
                'Exception in query {}'.format(e), status_code=500)

    def convert_rows_to_list(self, rows, cursor):
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return results

    def convert_row_to_dict(self, row):
        return dict(zip(row.keys(), row))

    def _format_order_respone(self, order_list):
        tmp = defaultdict(list)
        for item in order_list:
            tmp[item['order_id']].append(
                {'quantity': item['quantity'], 'product_id': item['product_id']})
        parsed_list = [{'order_id': k, 'requested': v} for k, v in tmp.items()]
        return parsed_list
