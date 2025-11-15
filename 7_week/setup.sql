USE appdb;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  price DECIMAL(10,2),
  stock INT DEFAULT 0
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  order_date DATE,
  amount DECIMAL(10,2),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  product_id INT,
  quantity INT,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO users (name, email) VALUES
('Kim', 'kim@example.com'),
('Lee', 'lee@example.com'),
('Park', 'park@example.com');

INSERT INTO products (name, price, stock) VALUES
('Laptop', 1200.00, 10),
('Mouse', 25.00, 100),
('Keyboard', 45.00, 50);

INSERT INTO orders (user_id, order_date, amount) VALUES
(1, '2025-11-01', 1225.00),
(2, '2025-11-02', 45.00);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 1),
(2, 3, 1);
