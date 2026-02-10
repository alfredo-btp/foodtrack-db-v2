
CREATE DATABASE FoodTrack;

USE Foodtrack;

-- foodtruck_id,name,cuisine_type,city

 
CREATE TABLE foodtrucks (
	foodtruck_id INT PRIMARY  KEY,
	name NVARCHAR(100) NOT NULL, 
	cuisine_type NVARCHAR(100),
	city NVARCHAR(100) NOT NULL
	);


CREATE TABLE locations (
    location_id INT PRIMARY KEY,
    foodtruck_id INT NOT NULL,
    location_date DATE NOT NULL,
    zone NVARCHAR(100) NOT NULL,
    CONSTRAINT FK_locations_foodtrucks FOREIGN KEY (foodtruck_id)
        REFERENCES foodtrucks(foodtruck_id)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    foodtruck_id INT NOT NULL,
    name NVARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    CONSTRAINT FK_products_foodtrucks FOREIGN KEY (foodtruck_id)
        REFERENCES foodtrucks(foodtruck_id)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    foodtruck_id INT NOT NULL,
    order_date DATE NOT NULL,
    status NVARCHAR(50) NOT NULL,
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    CONSTRAINT FK_orders_foodtrucks FOREIGN KEY (foodtruck_id)
        REFERENCES foodtrucks(foodtruck_id)
);

-- Tabla: order_items (depende de orders y products)
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    CONSTRAINT FK_order_items_orders FOREIGN KEY (order_id)
        REFERENCES orders(order_id),
    CONSTRAINT FK_order_items_products FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


