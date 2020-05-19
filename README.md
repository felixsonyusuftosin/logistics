## HOW TO 

- clone the repo https://github.com/felixsonyusuftosin/logistics 
- activate virtual env `source venv/bin/activate`
- install dependencies  `pip3 install -r requirements.txt`
- create a .env file and copy the contents of .env.example into the .env file 
- run the app with `flask run`
- open a new termminal and run `flask init-db` to initialize db


## Available endpints 
- http://127.0.0.1:5000/catalog/init  intialize catalog POST and GET
- http://127.0.0.1:5000/catalog/restock to restock   POST and GET
- http://127.0.0.1:5000/order/process to process order  POST and GET
- http://127.0.0.1:5000/order/ship to ship orders  POST and GET

## Caveats 
There is a check on that ensure the json is in the required and error free format. 

## Database 
uses sqlite , shipped with flask 