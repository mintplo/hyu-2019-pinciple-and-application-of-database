from flask import Flask, redirect, render_template, request
import pymysql
import datetime

app = Flask(__name__)

userid = {'id': None, 'email': None, 'passwd': None, 'storesid': None}
userinfo = [0, 0, 0]  # seller, customer, delivery
menulist = []  # 메뉴 리스트

db_connector = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'rootpw',
    'db': 'hanyang',
    'charset': 'utf8'
}

# TODO: 메뉴가 삭제되면 menu_count나 관련된 부분은 NO?


@app.route("/")
def index():
    userid['email'] = None
    userid['passwd'] = None
    userid['id'] = None
    userinfo[0] = 0
    userinfo[1] = 0
    userinfo[2] = 0
    return render_template("login.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    passwd = request.form.get('pw')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT seller_id FROM sellers WHERE passwd = '{passwd}' AND email = '{email}'"
    cur.execute(sql)
    seller = cur.fetchall()
    sql = f"SELECT customer_id FROM customers WHERE passwd = '{passwd}' AND email = '{email}'"
    cur.execute(sql)
    customer = cur.fetchall()
    sql = f"SELECT del_id FROM delivery WHERE passwd = '{passwd}' AND email = '{email}'"
    cur.execute(sql)
    delivery = cur.fetchall()

    if (not seller) and (not customer) and (not delivery):
        return render_template('error.html')
    if seller:
        userinfo[0] = 1
    if customer:
        userinfo[1] = 1
    if delivery:
        userinfo[2] = 1

    userid['email'] = email
    userid['passwd'] = passwd

    if seller:
        userid['id'] = seller[0]['seller_id']
    elif customer:
        userid['id'] = customer[0]['customer_id']
    elif delivery:
        userid['id'] = delivery[0]['del_id']
    else:
        userid['id'] = None
    conn.close()
    return redirect("/login/user")


# 로그인 성공
@app.route("/login/user", methods=['GET', 'POST'])
def user():
    """
    로그인 성공 페이지
    로그인에 성공한 사용자 정보(판매자, 구매자, 배달대행원)와 이름을 반환
    사용자 정보(판매자, 구매자, 배달대행원)에 맞는 로그인 성공 페이지를 보여주기 위함
    """
    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if not userid['id']:
        return render_template('error.html')

    if userinfo[0]:
        # seller
        sql = f"SELECT s.name, st.store_id FROM sellers s, stores st WHERE s.seller_id = {userid['id']} AND st.seller_id = s.seller_id"
    elif userinfo[1]:
        # customer
        sql = f"SELECT * FROM customers WHERE customer_id = {userid['id']}"
    elif userinfo[2]:
        # delivery
        sql = f"SELECT * FROM delivery WHERE del_id = {userid['id']}"
    else:
        return render_template('error.html')

    cur.execute(sql)
    info = cur.fetchone()

    conn.close()

    # 이름 정보 저장
    name = info['name']

    # Seller 일 경우 store_id 정보도 저장
    if userinfo[0]:
        userid['storesid'] = info['store_id']

    return render_template("user.html", info=userinfo, k=name)


# ========== 판매자 ==========


# 판매자 개인 정보 변경
@app.route("/login/user/schange", methods=['GET', 'POST'])
def schange():
    """
    판매자 개인 정보 변경 페이지
    현재 비밀번호와 이름을 확인하기 위함
    """
    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if not userinfo[0] or not userid['id']:
        return render_template('error.html')

    sql = f"SELECT s.name, st.store_id FROM sellers s, stores st WHERE s.seller_id = {userid['id']} AND st.seller_id = s.seller_id"
    cur.execute(sql)
    info = cur.fetchone()

    conn.close()

    # 이름 정보 저장
    sname = info['name']

    return render_template("schange.html",
                           info=userinfo,
                           name=sname,
                           passwd=userid['passwd'])


# 판매자 비밀번호 변경
@app.route("/login/user/schange/pw", methods=['GET', 'POST'])
def spw():
    """
    로그인한 판매자 비밀번호 변경
    """
    password = request.form.get('passwd')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if not userinfo[0] or not userid['id'] or not password:
        return render_template('error.html')

    sql = f"UPDATE sellers SET passwd = '{password}' WHERE seller_id = {userid['id']}"
    cur.execute(sql)

    conn.commit()
    conn.close()

    # 정보 갱신
    userid['passwd'] = password

    return redirect("/login/user")


# 판매자 이름 변경
@app.route("/login/user/schange/name", methods=['GET', 'POST'])
def schname():
    """
    로그인한 판매자 이름 변경
    """
    name = request.form.get('name')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if not userinfo[0] or not userid['id'] or not name:
        return render_template('error.html')

    sql = f"UPDATE sellers SET name = '{name}' WHERE seller_id = {userid['id']}"
    cur.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/login/user")


# 소유중인 가게 리스트
@app.route("/login/user/seller", methods=['GET', 'POST'])
def seller():
    """
    소유중인 가게 리스트 페이지
    로그인한 판매자가 소유중인 가게 리스트를 보여주기 위함
    """
    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if not userid['id'] or not userinfo[0]:
        return render_template('error.html')

    sql = f"SELECT * FROM stores WHERE seller_id = '{userid['id']}'"
    cur.execute(sql)

    store = cur.fetchall()
    conn.close()

    return render_template("seller.html", info=userinfo, store=store)


# 가게 정보, 메뉴 정보, 현재 주문
@app.route("/login/user/seller/store", methods=['GET', 'POST'])
def store():
    sid = request.form.get('sid')

    if sid:
        userid["storesid"] = sid
    sid = userid["storesid"]
    """
    가게 정보, 메뉴 정보, 현재 주문 페이지
    가제 정보, 메뉴 정보, 현재 주문을 확인하기 위함
    """
    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM stores WHERE store_id = {sid}"
    cur.execute(sql)
    store = cur.fetchone()

    sql = f"SELECT * FROM menu WHERE store_id = {sid}"
    cur.execute(sql)
    menu = cur.fetchall()
    """
    SELECT
    (SELECT c.email FROM customers c WHERE c.customer_id = od.customer_id) as customer_email, 
    (SELECT p.pay_type FROM payment p WHERE p.payment_id = od.payment_id) as pay_type,
    od.*
    FROM `order` od WHERE od.store_id = {sid}
    """
    sql = f"SELECT (SELECT c.email FROM customers c WHERE c.customer_id = od.customer_id) as customer_email, (SELECT p.pay_type FROM payment p WHERE p.payment_id = od.payment_id) as pay_type, od.* FROM `order` od WHERE od.store_id = {sid}"
    cur.execute(sql)
    order = cur.fetchall()

    return render_template("store.html",
                           info=userinfo,
                           store=store,
                           menu=menu,
                           sid=sid,
                           order=order)


# 메뉴 이름 변경
@app.route("/login/user/seller/store/menuchan", methods=['GET', 'POST'])
def menuchan():
    """
    메뉴 이름 변경
    해당 가게의 새로 입력 받은 메뉴 이름으로 변경하기 위함
    """
    sid = request.form.get('sid')
    menu = request.form.get('menu')
    newname = request.form.get('newname')

    if not userid['id'] or not userinfo[0]:
        return render_template('error.html')

    if not sid or not menu or not newname:
        return render_template(
            'error.message.html',
            message="스토어 정보 또는 메뉴 정보가 올바르지 않습니다. 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # menu_id 는 Primary Key 이기 때문에 중복 가능성이 없음. 단독으로 WHERE 조건에 와도 된다고 생각
    sql = f"UPDATE menu SET name = '{newname}' WHERE menu_id = {menu}"
    cur.execute(sql)

    conn.commit()
    conn.close()

    return redirect("/login/user/seller/store")


# 메뉴 삭제
@app.route("/login/user/seller/store/menudel", methods=['GET', 'POST'])
def menudel():
    sid = request.form.get('sid')
    menu = request.form.get('menu')
    """
    메뉴 삭제(현재 주문중인 메뉴는 삭제 불가)
    해당 가게의 메뉴를 삭제하기 위함
    """
    if not userid['id'] or not userinfo[0]:
        return render_template('error.html')

    if not sid or not menu:
        return render_template(
            'error.message.html',
            message="스토어 정보 또는 메뉴 정보가 올바르지 않습니다. 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # TODO: (현재 주문중인 메뉴는 삭제 불가) 조건을 만족해야 함. = 배달 완료된 주문은 주문중인 메뉴로 안치는건가?
    # menu_id 는 Primary Key 이기 때문에 중복 가능성이 없음. 단독으로 WHERE 조건에 와도 된다고 생각
    sql = f"DELETE FROM menu WHERE menu_id = {menu}"
    cur.execute(sql)

    conn.commit()
    conn.close()

    return redirect("/login/user/seller/store")


# 메뉴 추가
@app.route("/login/user/seller/store/menuadd", methods=['GET', 'POST'])
def menuadd():
    """
    메뉴 추가
    해당 가게의 새로 입력(메뉴명, 가격, 할인율) 받은 메뉴를 추가하기 위함
    """
    sid = request.form.get('sid')
    newmenuname = request.form.get('newmenuname')
    newmenuprice = request.form.get('newmenuprice')
    newmenuevent = request.form.get('newmenuevent')

    # TODO: decorator 처리 before.request
    if not userid['id'] or not userinfo[0]:
        return render_template('error.html')

    if not sid or not newmenuname or not newmenuprice or not newmenuevent:
        return render_template(
            'error.message.html',
            message="스토어 정보 새로 등록하려는 메뉴 정보가 올바르지 않습니다. 획인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"INSERT INTO menu(store_id, name, price, event) VALUES ({sid}, '{newmenuname}', '{newmenuprice}', '{newmenuevent}')"
    cur.execute(sql)

    conn.commit()
    conn.close()

    return redirect("/login/user/seller/store")


# 배달원 할당
@app.route("/login/user/seller/store/ordercheck", methods=['GET', 'POST'])
def ordercheck():
    orderinfo = request.form.get('orderinfo')
    """
    배달원 할당
    현재 주문에 대해 배달 가능한 배달대행원을 최대 5명까지 확인하기 위함(남은 횟수가 높은 순서로 확인)
    
    배달 가능한 배달대행원:
    1. 배달 가능한 지역(가게와 가까운 지역)
    2. 현재 배달 가능한 상태
    3. 남은 횟수가 0이 아닌 상태
    """
    # TODO: decorator 처리 before.request
    if not userid['id'] or not userinfo[0]:
        return render_template('error.html')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT c.address FROM `order` od, customers c WHERE od.order_id = {orderinfo} AND c.customer_id = od.customer_id"
    cur.execute(sql)

    customer = cur.fetchone()
    address = customer['address']

    sql = f"SELECT * FROM delivery d WHERE d.area LIKE '%{address}%' AND d.available = 1 AND d.stock > 0 ORDER BY d.stock DESC LIMIT 5"
    cur.execute(sql)

    deli = cur.fetchall()

    conn.close()

    return render_template("ordercheck.html",
                           info=userinfo,
                           view=deli,
                           orderinfo=orderinfo)


# 현재 주문에 배달원 ID 할당
@app.route("/login/user/seller/store/ordercheck/real", methods=['GET', 'POST'])
def orderreal():
    """
    현재 주문에 배달원 ID 할당
    현재 주문에 대해 배달대행원의 배달원 ID를 할당하기 위함
    """
    # TODO: decorator 처리 before.request
    if not userid['id'] or not userinfo[0]:
        return render_template('error.html')

    del_id = request.form.get('did')
    order_info = request.form.get('orderinfo')

    if not del_id or not order_info:
        return render_template(
            'error.message.html',
            message="배달원 할당 정보가 올바르지 않습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"UPDATE `order` SET del_id = {del_id} WHERE order_id = {order_info}"
    cur.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/login/user/seller/store")


# 주문 취소
@app.route("/login/user/seller/store/orderdel", methods=['GET', 'POST'])
def orderdel():
    """
    주문 취소
    현재 주문을 취소하기 위함
    """
    # TODO: decorator 처리 before.request
    if not userid['id'] or not userinfo[0]:
        return render_template('error.html')

    order_id = request.form.get('orderinfo')

    if not order_id:
        return render_template(
            'error.message.html',
            message="삭제할 주문 정보가 올바르지 않습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"DELETE FROM `order` WHERE order_id = {order_id}"
    cur.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/login/user/seller/store")


# ========== 구매자 ==========


# 구매자 관리 화면
@app.route("/login/user/customer", methods=['GET', 'POST'])
def customer():
    """
    구매자 관리 화면 페이지
    현재 비밀번호와 이름과 주소를 확인하기 위함
    """
    if not userid['id'] or not userinfo[1]:
        return render_template('error.html')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM customers WHERE customer_id = {userid['id']}"
    cur.execute(sql)

    customer = cur.fetchone()

    conn.commit()
    conn.close()

    return render_template("customer.html", info=userinfo, customer=customer)


# 구매자 비밀번호 변경
@app.route("/login/user/customer/pw", methods=['GET', 'POST'])
def cpw():
    """
    로그인한 구매자 비밀번호 변경
    """
    password = request.form.get('passwd')

    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    if not password:
        return render_template(
            'error.message.html',
            message="변경할 비밀번호를 입력하지 않으셨습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"UPDATE customers SET passwd = '{password}' WHERE customer_id = {userid['id']}"
    cur.execute(sql)

    conn.commit()
    conn.close()

    # 정보 갱신
    userid['passwd'] = password

    return redirect("/login/user")


# 구매자 이름 변경
@app.route("/login/user/customer/name", methods=['GET', 'POST'])
def cname():
    """
    로그인한 구매자 이름 변경
    """
    name = request.form.get('name')

    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    if not name:
        return render_template('error.message.html',
                               message="변경할 이름을 입력하지 않으셨습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"UPDATE customers SET name = '{name}' WHERE customer_id = {userid['id']}"
    cur.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/login/user")


# 구매자 주소 변경
@app.route("/login/user/customer/address", methods=['GET', 'POST'])
def addchan():
    """
    로그인한 구매자 주소 변경
    """
    address = request.form.get('address')

    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    if not address:
        return render_template('error.message.html',
                               message="변경할 주소를 입력하지 않으셨습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"UPDATE customers SET address = '{address}' WHERE customer_id = {userid['id']}"
    cur.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/login/user/customer")


# 구매자 구매화면
@app.route("/login/user/customer/buy", methods=['GET', 'POST'])
def buy():
    """
    구매화면 페이지
    로그인한 구매자의 주소로 가게 검색을 하기 위함
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM customers WHERE customer_id = {userid['id']}"
    cur.execute(sql)

    caddress = cur.fetchall()
    conn.close()

    return render_template("buy.html", info=userinfo, cus_addr=caddress)


# 고객 기본 주소로 가게 검색
@app.route("/login/user/schange/consearch", methods=['GET', 'POST'])
def consearch():
    """
    고객 기본 주수로 가게 검색
    로그인한 구매자의 주소로 부터 가까운 가게 검색을 하기 위함
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    address = request.form.get('address')
    if not address:
        return render_template('error.message.html',
                               message="검색할 주소를 입력하지 않으셨습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM stores WHERE address LIKE '%{address}%'"
    cur.execute(sql)

    store = cur.fetchall()
    conn.close()

    return render_template("storesearch.html", info=userinfo, store=store)


# 이름으로 가게 검색
@app.route("/login/user/schange/namesearch", methods=['GET', 'POST'])
def namesearch():
    """
    이름으로 가게 검색
    가게의 이름으로 검색하기 위함(부분 일치 가능)
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    name = request.form.get('name')
    if not name:
        return render_template('error.message.html',
                               message="검색할 이름을 입력하지 않으셨습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM stores WHERE sname LIKE '%{name}%'"
    cur.execute(sql)

    store = cur.fetchall()
    conn.close()

    return render_template("storesearch.html", info=userinfo, store=store)


# 입력 주소로 가게 검색
@app.route("/login/user/schange/addresssearch", methods=['GET', 'POST'])
def addresssearch():
    """
    입력 주소로 가게 검색
    입력한 주소로 가게를 검색하기 위함(부분 일치 가능)
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    keyaddr = request.form.get('keyaddr')
    if not keyaddr:
        return render_template('error.message.html',
                               message="검색할 주소를 입력하지 않으셨습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM stores WHERE address LIKE '%{keyaddr}%'"
    cur.execute(sql)

    store = cur.fetchall()
    conn.close()

    return render_template("storesearch.html", info=userinfo, store=store)


# 가게 정보, 메뉴 정보, 장바구니
@app.route("/login/user/customer/storebuy", methods=['GET', 'POST'])
def storebuy():
    buystoresid = request.form.get('storesid')
    o_menu_id = request.form.get('menu_id')
    o_menu = request.form.get('menu')
    o_num = request.form.get('num')
    o_sid = request.form.get('sid')

    if not buystoresid:
        buystoresid = o_sid
    if o_num and o_num != "0":
        # TODO: 중복 메뉴 수량 추가
        menulist.append([o_menu, o_num, o_menu_id])
    """
    가게 정보, 메뉴 정보, 장바구니 페이지
    가게 정보 및 메뉴 정보를 확인하기 위함
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM stores WHERE store_id = {buystoresid}"
    cur.execute(sql)
    store = cur.fetchone()

    sql = f"SELECT * FROM menu WHERE store_id = {buystoresid}"
    cur.execute(sql)
    menu = cur.fetchall()

    conn.close()

    return render_template("order.html",
                           info=userinfo,
                           store=store,
                           menu=menu,
                           menulist=menulist,
                           sid=buystoresid)


# 주문 메뉴 확인, 결제 수단
@app.route("/login/user/customer/storebuy/pay", methods=['GET', 'POST'])
def pay():
    buystoresid = request.form.get('sid')
    if not menulist:
        return render_template("payerror.html")
    """
    결제 수단
    로그인한 구매자의 결제 수단 및 결제정보를 확인하여 원하는 방식으로 결제하기 위함
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM payment WHERE customer_id = {userid['id']}"
    cur.execute(sql)
    payment = cur.fetchall()

    conn.close()

    return render_template("realpay.html",
                           info=userinfo,
                           sid=buystoresid,
                           payment=payment,
                           menulist=menulist)


# Order 및 Orderdetail
@app.route("/login/user/customer/storebuy/pay/done", methods=['GET', 'POST'])
def realpay():
    """
    구매자의 주문을 추가와 주문의 상세 내용을 추가하기 위함
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    sid = request.form.get('sid')
    payment_id = request.form.get('payment_id')
    pay_type = request.form.get('pay_type')
    pay_num = request.form.get('pay_num')

    if not sid or not pay_type or not pay_num or not payment_id:
        return render_template('error.message.html',
                               message="결제 정보가 올바르지 않습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    sql = f"INSERT INTO `order`(payment_id, customer_id, store_id, order_time, delivery_done) VALUES ({payment_id}, {userid['id']}, {sid}, '{now}', 0)"
    cur.execute(sql)

    order_id = conn.insert_id()
    for item in menulist:
        sql = f"INSERT INTO orderdetail(order_id, menu_id, quantity) VALUES ({order_id}, {item[2]}, {item[1]})"
        cur.execute(sql)

    conn.commit()
    conn.close()

    del menulist[:]
    return redirect("/login/user/customer")


# 주문Order 화면
@app.route("/login/user/customer/order", methods=['GET', 'POST'])
def cusorder():
    """
    주문Order 화면
    주문한 가게 이름, 주문한 총 메뉴 수, 결제수단, 주문 시간, 배달 완료 여부를 확인하기 위함
    """
    if not userinfo[1] or not userid['id']:
        return render_template('error.html')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    """
    SELECT
    od.*,
    (SELECT stores.sname FROM stores WHERE od.store_id = od.store_id) as store_name,
    (SELECT count(dt.menu_id) FROM orderdetail dt WHERE dt.order_id = od.order_id GROUP BY dt.order_id) as menu_count,
    (SELECT p.pay_type FROM payment p WHERE p.payment_id = od.payment_id) as pay_type
    FROM `order` od WHERE od.customer_id = 10100001;
    """
    sql = f"SELECT od.*, (SELECT stores.sname FROM stores WHERE stores.store_id = od.store_id) as store_name, (SELECT count(dt.menu_id) FROM orderdetail dt WHERE dt.order_id = od.order_id GROUP BY dt.order_id) as menu_count, (SELECT p.pay_type FROM payment p WHERE p.payment_id = od.payment_id) as pay_type FROM `order` od WHERE od.customer_id = {userid['id']}"
    cur.execute(sql)

    od = cur.fetchall()
    conn.close()

    return render_template("payhistory.html", info=userinfo, order=od)


# ========== 배달대행원 ==========


# 현재 배송 중인 주문
# TODO: 배송 완료된 주문은 어떻게 해야하는지?
@app.route("/login/user/delivery", methods=['GET', 'POST'])
def delivery():
    """
    현재 OOO님의 배송 중인 주문 페이지
    가게 이름, 주문자 이름, 주문자 전화번호, 배송지, 주문시간, 배송 완료 여부를 확인하기 위함
    """
    if not userinfo[2] or not userid['id']:
        return render_template('error.html')

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"SELECT * FROM delivery WHERE del_id = {userid['id']}"
    cur.execute(sql)
    deli = cur.fetchone()

    sql = f"SELECT o.order_id, s.sname, c.name, c.phone, c.address, o.order_time FROM `order` o, stores s, customers c WHERE s.store_id = o.store_id AND c.customer_id = o.customer_id"
    cur.execute(sql)
    oorder = cur.fetchall()

    conn.close()

    return render_template("delivery.html",
                           info=userinfo,
                           order=oorder,
                           deli=deli)


# 배송 완료
@app.route("/login/user/delivery/deliverydone", methods=['GET', 'POST'])
def deliverydone():
    """
    배송 완료
    배달대행원이 배달 완료 시 배달 완료 여부를 배달 완료로 갱신하기 위함
    """
    if not userinfo[2] or not userid['id']:
        return render_template('error.html')

    order_id = request.form.get('order_id')
    if not order_id:
        return render_template('error.message.html',
                               message="주문 정보가 올바르지 않습니다. 확인 후 다시 시도해 주세요.")

    conn = pymysql.connect(**db_connector)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = f"UPDATE `order` SET delivery_done = 1 WHERE order_id = {order_id}"

    cur.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/login/user/delivery")


if __name__ == '__main__':
    app.run(debug=True)
