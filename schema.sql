-- customers
CREATE TABLE customers (
    name VARCHAR NOT NULL,
    id INTEGER PRIMARY KEY AUTOINCREMENT
);

-- products and their volumes and categories
CREATE TABLE products(
    name VARCHAR NOT NULL,
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auto BOOLEAN,
    food BOOLEAN,
    outdoor BOOLEAN,
    inventory REAL NOT NULL,
    tools BOOLEAN,
    home BOOLEAN,
    toys BOOLEAN
);

-- customer order ids and their status
CREATE TABLE order_baskets(
    ready BOOLEAN,
    on_its_way BOOLEAN,
    delivered BOOLEAN,
    customer_id INTEGER NOT NULL,
    datetime DATETIME DEFAULT (strftime('%s')),
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- products and the purchased volumes that correspond to an order_basket id, could be many for each basket
CREATE TABLE order_volumes(
    id INTEGER,
    product_id INTEGER NOT NULL,
    volume REAL NOT NULL,
    FOREIGN KEY(id) REFERENCES order_baskets(id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- merge product names with product order volumes
CREATE VIEW order_volumes_view AS
    SELECT
        order_volumes.id, order_volumes.volume, products.name, products.id AS product_id
    FROM
        order_volumes
    LEFT JOIN
        products
    ON
        products.id == order_volumes.product_id
;

-- merge datetimes with product order volumes and sort
CREATE VIEW order_volumes_dates_view AS
    SELECT
        order_volumes_view.id,
        order_volumes_view.volume,
        order_volumes_view.name,
        order_volumes_view.product_id,
        order_baskets.datetime
    FROM
        order_volumes_view
    LEFT JOIN
        order_baskets
    ON
        order_volumes_view.id = order_baskets.id
    ORDER BY
        datetime DESC
;

INSERT INTO products(id, name, auto, inventory) VALUES (1, 'tire', 1, 8) ;
INSERT INTO products(id, name, toys, outdoor, inventory) VALUES (2, 'bike', 1, 1, 3);
INSERT INTO products(id, name, auto, inventory) VALUES (3, 'oil', 1, 13);
INSERT INTO products(name, auto, inventory) VALUES ('headlight', 1, 17);
INSERT INTO products(name, toys, inventory) VALUES ('ninja turtle', 1, 32);
INSERT INTO products(name, food, inventory) VALUES ('rice', 1, 99.5);
INSERT INTO products(name, tools, auto, inventory) VALUES ('wrench', 1, 1, 5);
INSERT INTO products(name, home, inventory) VALUES ('chair', 1, 2);
INSERT INTO products(name, food, inventory) VALUES ('oil', 1, 23);

INSERT INTO customers(name, id) VALUES ('Joe', 1);
INSERT INTO customers(name, id) VALUES ('Sue', 2);
INSERT INTO customers(name, id) VALUES ('Tom', 3);

INSERT INTO order_baskets(customer_id, id, datetime) VALUES (1, 1, strftime('%s', '2020-01-01'));
INSERT INTO order_baskets(customer_id, id, datetime) VALUES (2, 2, strftime('%s', '2020-01-03'));
INSERT INTO order_baskets(customer_id, id, datetime) VALUES (1, 3, strftime('%s', '2020-07-15'));
INSERT INTO order_baskets(customer_id, id, datetime) VALUES (1, 4, strftime('%s', '2020-11-02'));
INSERT INTO order_baskets(customer_id, id, datetime) VALUES (2, 5, strftime('%s', '2020-11-03'));

INSERT INTO order_volumes(id, product_id, volume) VALUES (1, 1, 2);
INSERT INTO order_volumes(id, product_id, volume) VALUES (1, 2, 1);
INSERT INTO order_volumes(id, product_id, volume) VALUES (2, 3, 1);
INSERT INTO order_volumes(id, product_id, volume) VALUES (3, 3, 1);
INSERT INTO order_volumes(id, product_id, volume) VALUES (4, 1, 1);
INSERT INTO order_volumes(id, product_id, volume) VALUES (5, 1, 1);