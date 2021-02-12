from flask import Flask
from flask import request, jsonify
from collections import OrderedDict
import sqlite3
import os
import datetime
from dateutil.relativedelta import relativedelta

""" Flask app """

# open schema
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schema.sql'), 'r') as f:
    schema = f.read()

# initialize database in memory
connection = sqlite3.connect(":memory:", check_same_thread=False)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
cursor.executescript(schema)
cursor.execute("PRAGMA foreign_keys = ON")

app = Flask(__name__)

@app.route('/shipt/api/v1/history/<int:customer_id>', methods=['GET'])
def customer_history(customer_id):
    """
    An API endpoint that returns all orders for a customer sorted by date.
    :param customer_id: customer id used for orders
    :type customer_id: string
    """

    cursor.execute("""
        SELECT 
            order_volumes_view.id, 
            order_baskets.datetime, 
            order_baskets.ready, 
            order_baskets.on_its_way, 
            order_baskets.delivered, 
            order_volumes_view.product_id,
            order_volumes_view.name,
            order_volumes_view.volume
        FROM 
            order_baskets
        INNER JOIN 
            order_volumes_view
        ON 
            order_baskets.id == order_volumes_view.id AND order_baskets.customer_id == {}
        ORDER BY
            order_baskets.datetime DESC
    """.format(customer_id))

    orders = cursor.fetchall()
    # use dict to collect multiple products for a single order
    orders_dict = OrderedDict()
    for row in orders:
        tup = tuple(row)
        order_id = str(tup[0])
        if order_id in orders_dict:
            orders_dict[order_id]["products"][str(tup[5])] = {tup[6]: float(tup[7])}
        else:
            orders_dict[order_id] = {}
            orders_dict[order_id]["datetime"] = datetime.datetime.utcfromtimestamp(tup[1]).strftime('%Y-%m-%d')
            orders_dict[order_id]["ready"] = tup[2]
            orders_dict[order_id]["on its way"] = tup[3]
            orders_dict[order_id]["delivered"] = tup[4]
            orders_dict[order_id]["products"] = {str(tup[5]): {tup[6]: float(tup[7])}}
    if not orders_dict:
        return jsonify({customer_id: "no orders!"})

    # create list of orders
    orders_list = []
    for key, value in orders_dict.items():
        value["order id"] = key
        orders_list.append(value)

    return jsonify({str(customer_id): orders_list})

@app.route('/shipt/api/v1/purchase', methods=['POST'])
def customer_purchase():
    """
    An API endpoint to create an Order for a Customer where input products can be
    specified by Product IDs.
    :param customer_id:
    :type customer_id:
    """

    bought = request.json["products"]
    customer_id = request.json["customer"]

    # check products and volumes
    for product_id, volume in dict(bought).items():
        error = False
        try:
            int(product_id)
            volume = float(volume)
        except BaseException:
            error = True
        if not error:
            cursor.execute("SELECT * FROM products WHERE id == {}".format(product_id))
        if not cursor.fetchone() or error:
            bought.pop(product_id)

    if not bought:
        return jsonify({"error": "need valid products and volumes"})

    # check if valid customer name or id
    try:
        customer_id = int(customer_id)
    except BaseException as e:
        if customer_id.replace(" ", "").isalpha():
            cursor.execute("INSERT INTO customers(name) VALUES ('{}')".format(customer_id))
            customer_id = cursor.execute("SELECT last_insert_rowid()").lastrowid
        else:
            return jsonify({"error": "need valid customer name or id"})

    # create order basket id
    try:
        cursor.execute("INSERT INTO order_baskets(customer_id) VALUES ({})".format(customer_id))
        order_id = cursor.execute("SELECT last_insert_rowid()").lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error": "need valid customer id"})

    # parse items
    purchase = {}
    for product_id, volume in bought.items():
        cursor.execute("INSERT INTO order_volumes(id, product_id, volume) VALUES ({}, {}, {})".format(order_id, product_id, volume))
        cursor.execute("UPDATE products SET inventory = inventory - {} WHERE id == {}".format(volume, product_id))
        purchase[product_id] = volume

    return jsonify({"order": order_id, "purchase": purchase, "customer_id": customer_id})

@app.route('/shipt/api/v1/data/<starting>/<ending>/<unit>', methods=['GET'])
def sales_data(starting, ending, unit):
    """
    An API endpoint that accepts a date range and a day, week, or month and
    returns a breakdown of products sold by quantity per day/week/month.
    :param starting: starting date
    :type starting: string
    :param ending: ending date
    :type ending: string
    :param unit: display sales by (day, week, or month)
    :type unit: string
    """

    start = datetime.date(int(starting[:4]), int(starting[4:6]), int(starting[6:]))
    end = datetime.date(int(ending[:4]), int(ending[4:6]), int(ending[6:]))

    if unit == "day":
        increment = datetime.timedelta(days=1)
        formatter = "j"
    elif unit == "week":
        increment = datetime.timedelta(weeks=1)
        formatter = "W"
    elif unit == "month":
        increment = relativedelta(months=1)
        formatter = "m"
    else:
        return jsonify(
            {"error": "/shipt/api/v1/data/<starting:yyyymmdd>/<ending:yyyymmdd>/<unit:['day','week','month']>"}
        )

    intervals = {}
    intervals[unit] = OrderedDict()

    while start <= end:
        cursor.execute("""
            SELECT 
                SUM(order_volumes_dates_view.volume),
                order_volumes_dates_view.name,
                order_volumes_dates_view.product_id
            FROM 
                order_volumes_dates_view
            WHERE
                strftime('%Y%{}', order_volumes_dates_view.datetime, 'unixepoch') == '{}'
            GROUP BY
                order_volumes_dates_view.product_id
        """.format(formatter, start.strftime("%Y%" + formatter)))

        orders = cursor.fetchall()
        start_key = start.strftime("%" + formatter + "-%Y")
        for row in orders:
            tup = tuple(row)
            if start_key not in intervals[unit]:
                intervals[unit][start_key] = []
            intervals[unit][start_key].append({"volume": tup[0], "name": tup[1], "product id": tup[2]})

        start = start + increment

    return jsonify(intervals)