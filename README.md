# API Challenge
Create a very basic REST API application where a customer can have an order that is
made up of products. You are expected to query this API using a RESTful interface.
Product names are not expected to be unique.
Please do not use ORM functionality in your submission.
All endpoints should return data in JSON format.
## Author
Brent Janski  
[janskibf@gmail.com](mailto:janskibf@gmail.com)  
November, 2020
## Tasks
Please implement the following features:
1. A product belongs to many categories. A category has many products. A product
can be sold in decimal amounts (such as weights).
2. A customer can have many orders. An order is comprised of many products. An
order has a status stating if the order is “ready”, “on its way”, or “delivered”.
3. An API endpoint that accepts a date range and a day, week, or month and
returns a breakdown of products sold by quantity per day/week/month.
4. An API endpoint that returns all orders for a customer sorted by date.
5. An API endpoint to create an Order for a Customer where input products can be
specified by Product IDs.

## How to run

### Requirements:

Installed?: `python3`

pip3:

```
flask
python-dateutil
```
Change directory to project root (location of this README), then run and enter port:
```
python3 shipt <port_number>
```

Test: change directory to project root (location of this README):
```
python3 -m unittest
```

## Endpoints
### GET products sold by date range and increment: `/shipt/api/v1/data/<starting>/<ending>/<unit>`
starting date: `yyyymmdd`  
ending date: `yyyymmdd`  
unit: `day`, `week`, or `month`

Will return product sales by day, week, or month in the range given

### GET customer sales history `/shipt/api/v1/history/<customer_id>`

Returns sales history by customer id

### POST new order `/shipt/api/v1/purchase`
Required JSON keys:
- `customer` = new customer name (string) `"Joe"` or existing id (int) `1`
- `products` = `{"<product id>": <quantity>, "<product_id>": <quantity>, ...}`

examples:
```
'{"customer": "brent", "products": {"2": 1}}'
```
```
'{"customer": 1, "products": {"2": 1, "4": 2.5}}'
```
## Assumptions made
- App can be started with single command, no manual database setup
- API limited to scope of questions (no need for price and other data)
- Can assume users are trusted and knowledgeable (minimal validation, minimal messaging)
- No need to go down edge case rabbit holes

## What I would do with more time

- More SQL views to consolidate disparate SQL insertion calls
- Validation of user inputs
- Endpoint to delete or modify orders
- Use a full fledged SQL server like Postgres
- Sorting and parsing of data done in more SQL views rather than python
- More comprehensive unit tests
- More comprehensive documentation/comments
- Integration test
- PEP8 compliance
