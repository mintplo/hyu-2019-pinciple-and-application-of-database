## 배달의 한양 어플리케이션 Term Project

2019 HYU 데이터베이스의 원리와 응용(Principle and Application of database) TERM PROJECT

## Implementation

1. 판매자와 구매자 배달대행자를 연결해주는 앱과 서비스를 개발하는 시나리오
2. 주어진 소스 코드 (app.py) 와 DB를 기반으로 제시되는 시나리오를 만족하는 앱 개발

## Provided

- app.py 및 html 파일
- 데이터 csv 파일
    - customer.csv
    - delivery.csv
    - menu.csv
    - owner.csv
    - pay.csv
    - store.csv

## Develop Environment
Based on Mac OSX 10.15 (Catalina)

- Docker for Mac
- Python 3.7.x
- Flask
- PyMySQL
- Pipenv (for Python Virtual Environment)
- PyCharm Professional Edition

## Project Specifications

### Database

- 데이터는 UTF-8로 인코딩 되어 있음 따라서 DB와 테이블 생성시 기본 인코딩 설정도 UTF-8로 설정해 주어야 함.
- menu 데이터 로드 시 skipped(warning이 뜸) 되는 에러는 무시해도 됨

```
LOAD DATA LOCAL INFILE "d:\customer.csv"

INTO table db명.테이블명 FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';
```

### Customers

- `name`, `passwd`, `phone`, `email`, `address`, `customer_id(PK)`
- 입력 데이터 파일: `customer.csv`
- 고객은 메뉴를 선택하여 각 가게(Seller)에 주문을 하는 사람

### Sellers

- `sellers_id(PK)`, `name`, `phone`, `email`, `passwd`
- 가게 점주
- 입력 데이터 파일: `seller.csv`

### Delivery

- `del_id(PK)`, `name`, `email`, `passwd`, `area`, `phone`, `available`, `stock`
- 배달원 정보(area: 배달 지역, available: 배달 가능 여부 1 or 0, stock: 남은 배달 건수)
- 입력 데이터 파일: `deliverer.csv`

### Stores

- `store_id(PK)`, `address`, `sname`, `phone`, `seller_id(FK)`, `open_time`, `close_time`, `type`
- 점주가 소유하는 가게, (sname: 가게명, type: 가게 유형)
- 입력 데이터 파일: `store.csv`

### Menu

- `menu_id(PK)`, `name`, `price`, `event`, `store_id(FK)`
- 메뉴, (event: 할인율)
- 입력 데이터 파일: `menu.csv`

### Payment

- `payment_id, customer_id(FK) [PK]`, `pay_num`, `pay_type`
- 결제, (pay_num: 결제수단의 번호, pay_type: 결제수단 타입, 1 ~ 4)
- 입력 데이터 파일: `pay.csv`

### Orders

- 주문 테이블은 다음의 컬럼들만 가진다.
    - `order_id(PK)`, `order_time(주문시간, timestamp)`, `delivery_done(배송 완료 여부, 1 or 0)` = 일반 어트리뷰트
    - `del_id`, `payment_id`, `customer_id`, `store_id` = FK
    - **_주문 테이블에 위의 7개 속성(필드)들 이외에 다른 속성을 임의로 추가하지 말것._**
- FK를 어떤 테이블에서 어떻게 끌어오는지는 각자 생각할 것.

### Orderdetail

- `detail_order_id, order_id(FK) [PK]`, `menu_id(FK)`, `quantity (주문수량)`
- **_Orderdetail 테이블에는 위의 4개 속성(필드)들 이외에 다른 속성을 임의로 추가하지 말것._**
- 주문(order) 취소 시 해당 orderdetail도 **_함께 삭제되도록 제약조건을_** 설정해야 함.
- 가게에서 메뉴 삭제 시 현재 주문 중인 메뉴가 아니라면, 즉 배달 완료 된 메뉴가 삭제 가능해야 하며 삭제 시 Orderdetail의 메뉴 관련 정보는 NULL로 변경되어야 함.

## Running

1. Running MariaDB for Development with Docker-compose

```bash
docker-compose up -d
```

2. Python Library Installation with Pipenv

```bash
pipenv install
pipenv shell
```

3. SQL Script Run

```bash
mysql -h127.0.0.1 -uroot -prootpw hanyang < database.sql
```

4. Running Flask Application (activated with pipenv)

```bash
python app.py
```

4. Go to `localhost:5000`
