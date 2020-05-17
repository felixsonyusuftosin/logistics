# Define sql queries here
from flaskr.utils.exceptions import DatabaseWriteError
import sqlite3
import json


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
    def update_one_stock(self, stock):
      q = 'UPDATE stock SET quantity={} where product_id = {}'.format(stock['quantity'], stock['product_id'])
      cursor = self.execute_query(q)
      self.db.commit()
    
    def read_all_stocks(self):
      q = 'SELECT * FROM stock;'
      cursor = self.execute_query(q)
      rows = cursor.fetchall()
      return self.convert_rows_to_list(rows, cursor)
    
    def update_stocks(self, stocks):
      for stock in stocks:
        self.update_one_stock(stock)
      return { 'message': 'successfully updated all stocks' }
  
    ''' 
    Stock_view queryies. 
    ------------------------
    '''
    def get_stock_info(self, product_id):
      q = 'SELECT * from v_stock WHERE v_stock.product_id ={};'.format(product_id)
      cursor = self.execute_query(q)
      row = cursor.fetchone()
      return self.convert_row_to_dict(row)
    


    '''
     Utility Methods
     ------------------------
    '''

    def execute_query(self, query):
        try:
            cursor = self.db.execute(query)
            return cursor
        except sqlite3.Error as e:
            raise DatabaseWriteError(
                'Database error {}'.format(e), status_code=500)
        except Exception as e:
            raise DatabaseWriteError(
                'Exception in query {}'.format(e), status_code=500)

    def convert_rows_to_list(self, rows, cursor):
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return results
      
    def convert_row_to_dict(self, row):
        return dict(zip(row.keys(), row))  