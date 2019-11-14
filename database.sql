-- # 이 SCRIPT 파일은 데이터베이스 초기화 + 테이블 생성을 목적으로 하는 SQL
-- # 빈 데이터베이스를 전제 조건으로 생각
CREATE DATABASE IF NOT EXISTS hanyang;
use hanyang;

SET @@session.unique_checks = 0;
SET @@session.foreign_key_checks = 0;

-- # Customers 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `customers`;
-- # Customers 테이블 생성
CREATE TABLE customers (
    customer_id INT UNSIGNED NOT NULL COMMENT '고객 식별 번호', -- AUTO_INCREMENT
    email VARCHAR(128) NOT NULL COMMENT '고객 이메일',
    name VARCHAR(16) NOT NULL COMMENT '고객 이름',
    passwd VARCHAR(128) NOT NULL COMMENT '비밀번호',
    phone VARCHAR(11) NOT NULL COMMENT '전화번호',
    address VARCHAR(255) NOT NULL COMMENT '고객 주소',
    PRIMARY KEY(customer_id),
    UNIQUE KEY EMAIL_UNIQUE_IDX(email) -- 이메일 중복 제약 조건
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

-- # Sellers 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `sellers`;
-- # Sellers 테이블 생성
CREATE TABLE sellers (
    seller_id INT UNSIGNED NOT NULL COMMENT '점주 식별 번호', -- AUTO_INCREMENT
    email VARCHAR(128) NOT NULL COMMENT '점주 이메일',
    name VARCHAR(16) NOT NULL COMMENT '점주 이름',
    passwd VARCHAR(128) NOT NULL COMMENT '비밀번호',
    phone VARCHAR(11) NOT NULL COMMENT '전화번호',
    PRIMARY KEY(seller_id),
    UNIQUE KEY EMAIL_UNIQUE_IDX(email) -- 이메일 중복 제약 조건
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

-- # Delivery 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `delivery` CASCADE;
-- # Delivery 테이블 생성
CREATE TABLE delivery (
    del_id INT UNSIGNED NOT NULL COMMENT '배달원 식별 번호', -- AUTO_INCREMENT
    email VARCHAR(128) NOT NULL COMMENT '배달원 이메일',
    name VARCHAR(16) NOT NULL COMMENT '배달원 이름',
    passwd VARCHAR(128) NOT NULL COMMENT '비밀번호',
    area VARCHAR(255) NOT NULL COMMENT '배달 지역',
    phone VARCHAR(11) NOT NULL COMMENT '전화번호',
    available INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '배달 가능 여부 - 0 or 1',
    stock INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '남은 배달 건수',
    PRIMARY KEY(del_id),
    UNIQUE KEY EMAIL_UNIQUE_IDX(email) -- 이메일 중복 제약 조건
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

-- # Stores 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `stores`;
-- # Stores 테이블 생성
CREATE TABLE stores (
    store_id INT UNSIGNED NOT NULL COMMENT '가게 식별 번호', -- AUTO_INCREMENT
    seller_id INT UNSIGNED NOT NULL COMMENT '점주 식별 번호(FK)',
    sname VARCHAR(128) NOT NULL COMMENT '가게명',
    type VARCHAR(32) NOT NULL COMMENT '가게 유형',
    address VARCHAR(255) NOT NULL COMMENT '가게 주소',
    phone VARCHAR(11) NOT NULL COMMENT '가게 전화번호',
    open_time TIME NOT NULL COMMENT '가게 개장시간',
    close_time TIME NOT NULL COMMENT '가게 폐장시간',
    PRIMARY KEY(store_id),
    FOREIGN KEY(seller_id) REFERENCES sellers(seller_id)
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

-- # Menu 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `menu`;
-- # Menu 테이블 생성
CREATE TABLE menu (
    menu_id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '메뉴 식별 번호',
    store_id INT UNSIGNED NOT NULL COMMENT '가게 식별 번호(FK)',
    name VARCHAR(128) NOT NULL COMMENT '메뉴 이름',
    price INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '가격',
    event DECIMAL(10, 8) NOT NULL DEFAULT 0 COMMENT '할인율',
    PRIMARY KEY(menu_id),
    FOREIGN KEY(store_id) REFERENCES stores(store_id)
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

-- # Payment 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `payment`;
-- # Payment 테이블 생성
CREATE TABLE payment (
    payment_id INT UNSIGNED NOT NULL COMMENT '결제 수단 식별 번호', -- AUTO_INCREMENT
    customer_id INT UNSIGNED NOT NULL COMMENT '고객 식별 번호(FK)',
    pay_num VARCHAR(128) NOT NULL COMMENT '결제수단의 번호',
    pay_type INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '결제수단 타입, 1 ~ 4',
    PRIMARY KEY(payment_id, customer_id),
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

-- # Order 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `order`;
-- # Order 테이블 생성
CREATE TABLE `order` (
    order_id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '주문 식별 번호',
    del_id INT UNSIGNED COMMENT '배달원 식별 번호',
    payment_id INT UNSIGNED NOT NULL COMMENT '결제 수단 식별 번호',
    customer_id INT UNSIGNED NOT NULL COMMENT '고객 식별 번호',
    store_id INT UNSIGNED NOT NULL COMMENT '가게 식별 번호',
    order_time TIMESTAMP NOT NULL COMMENT '주문 시간',
    delivery_done INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '배송 완료 여부, 0 or 1',
    PRIMARY KEY(order_id),
    FOREIGN KEY(del_id) REFERENCES delivery(del_id),
    FOREIGN KEY(payment_id) REFERENCES payment(payment_id),
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(store_id) REFERENCES stores(store_id)
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

-- # Orderdetail 테이블이 기존에 존재하는 경우 DROP TABLE
DROP TABLE IF EXISTS `orderdetail`;
-- # Orderdetail 테이블 생성
CREATE TABLE orderdetail (
    detail_order_id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '주문 상세 식별 번호',
    order_id INT UNSIGNED NOT NULL COMMENT '주문 식별 번호(FK)',
    menu_id INT UNSIGNED COMMENT '메뉴 식별 번호(FK)',
    quantity INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '주문 수량',
    PRIMARY KEY(detail_order_id, order_id),
    FOREIGN KEY(order_id) REFERENCES `order`(order_id) ON DELETE CASCADE,
    FOREIGN KEY(menu_id) REFERENCES menu(menu_id) ON DELETE SET NULL
) ENGINE = InnoDB
DEFAULT CHARACTER SET = 'utf8';

SET @@session.unique_checks = 1;
SET @@session.foreign_key_checks = 1;

-- # LOAD customer.csv
LOAD DATA LOCAL INFILE './data/customer.csv'
INTO TABLE customers
CHARACTER SET utf8
FIELDS
    TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
LINES
    TERMINATED BY '\r\n'
(name, passwd, phone, email, address, customer_id);

-- # LOAD delivery.csv
LOAD DATA LOCAL INFILE './data/delivery.csv'
INTO TABLE delivery
CHARACTER SET utf8
FIELDS
    TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
LINES
    TERMINATED BY '\r\n'
(del_id, name, email, passwd, area, phone, available, stock);

-- # LOAD seller.csv
LOAD DATA LOCAL INFILE './data/seller.csv'
INTO TABLE sellers
CHARACTER SET utf8
FIELDS
    TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
LINES
    TERMINATED BY '\r\n'
(seller_id, name, phone, email, passwd);

-- # LOAD store.csv
LOAD DATA LOCAL INFILE './data/store.csv'
INTO TABLE stores
CHARACTER SET utf8
FIELDS
    TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
LINES
    TERMINATED BY '\r\n'
(store_id, address, sname, phone, seller_id, open_time, close_time, type);

-- # LOAD menu.csv
LOAD DATA LOCAL INFILE './data/menu.csv'
INTO TABLE `menu`
CHARACTER SET utf8
FIELDS
    TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
LINES
    TERMINATED BY '\r\n'
(menu_id, name, price, event, store_id);

-- # LOAD pay.csv
LOAD DATA LOCAL INFILE './data/pay.csv'
INTO TABLE payment
CHARACTER SET utf8
FIELDS
    TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
LINES
    TERMINATED BY '\r\n'
(payment_id, customer_id, pay_num, pay_type);
