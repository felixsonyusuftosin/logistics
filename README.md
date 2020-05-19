## HOW TO 

- clone the repo https://github.com/felixsonyusuftosin/logistics 
- activate virtual env `source venv/bin/activate`
- install dependencies  `pip3 install -r requirements.txt`
- initialize db `flaskr init-db`

Available endpints 
- http://127.0.0.1:5000/catalog/init  intialize catalog
- http://127.0.0.1:5000/catalog/restock to restock
- http://127.0.0.1:5000/order/process to process order
- http://127.0.0.1:5000/order/ship to ship orders
