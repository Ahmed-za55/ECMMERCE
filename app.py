import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-key')

# =====================
# إعداد قاعدة البيانات
# =====================
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '4752'),
        database=os.getenv('DB_NAME', 'E-commerce'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    return connection

# =====================
# Decorator: تأكد من تسجيل الدخول
# =====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('يجب تسجيل الدخول أولاً', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================
# الصفحة الرئيسية
# =====================
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT p.*, c.categoryName 
            FROM PRODUCT p 
            JOIN CATEGORY c ON p.categoryID = c.categoryID
        ''')
        products = cursor.fetchall()
        cursor.execute('SELECT * FROM CATEGORY')
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        cart_count = len(session.get('cart', {}))
        return render_template('index.html', products=products, categories=categories, cart_count=cart_count)
    except Exception as e:
        return f"حدث خطأ في الاتصال: {e}"

# =====================
# تسجيل الدخول
# =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'customer_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not email or not password:
            flash('يرجى ملء جميع الحقول', 'error')
            return render_template('login.html')
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM CUSTOMER WHERE email = %s', (email,))
            customer = cursor.fetchone()
            if customer and check_password_hash(customer['passwordHash'], password):
                cursor.execute('''
                    UPDATE CUSTOMER 
                    SET lastLogin = %s, loginCount = loginCount + 1, status = 'active'
                    WHERE customerID = %s
                ''', (datetime.datetime.now(), customer['customerID']))
                conn.commit()
                session['customer_id'] = customer['customerID']
                session['customer_name'] = f"{customer['fname']} {customer['lname']}"
                session['customer_email'] = customer['email']
                flash(f"أهلاً بك، {customer['fname']}!", 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('index'))
            else:
                flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'error')
            cursor.close()
            conn.close()
        except Exception as e:
            flash(f'حدث خطأ: {str(e)}', 'error')
    return render_template('login.html')

# =====================
# إنشاء حساب جديد
# =====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'customer_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        fname = request.form.get('fname', '').strip()
        lname = request.form.get('lname', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        if not all([fname, lname, email, password, phone]):
            flash('يرجى ملء جميع الحقول المطلوبة', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('كلمتا المرور غير متطابقتين', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return render_template('register.html')
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT customerID FROM CUSTOMER WHERE email = %s', (email,))
            if cursor.fetchone():
                flash('البريد الإلكتروني مسجل بالفعل', 'error')
                cursor.close()
                conn.close()
                return render_template('register.html')
            hashed_pw = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO CUSTOMER (fname, lname, email, passwordHash, phone, status)
                VALUES (%s, %s, %s, %s, %s, 'active')
            ''', (fname, lname, email, hashed_pw, phone))
            conn.commit()
            cursor.close()
            conn.close()
            flash('تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'حدث خطأ: {str(e)}', 'error')
    return render_template('register.html')

# =====================
# تسجيل الخروج
# =====================
@app.route('/logout')
def logout():
    if 'customer_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE CUSTOMER SET status = 'inactive' WHERE customerID = %s",
                           (session['customer_id'],))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

# =====================
# إضافة للسلة
# =====================
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM PRODUCT WHERE productID = %s', (product_id,))
            product = cursor.fetchone()
            cursor.close()
            conn.close()
            if product:
                cart[str(product_id)] = {
                    'name': product['productName'],
                    'price': float(product['price']),
                    'quantity': quantity
                }
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    session['cart'] = cart
    session.modified = True
    cart_count = sum(item['quantity'] for item in cart.values())
    return jsonify({'success': True, 'cart_count': cart_count})

# =====================
# عرض السلة
# =====================
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    cart_count = sum(item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total, cart_count=cart_count)

# =====================
# حذف من السلة
# =====================
@app.route('/cart/remove/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('cart'))

# =====================
# تأكيد الطلب
# =====================
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('السلة فارغة!', 'warning')
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            total = sum(item['price'] * item['quantity'] for item in cart.values())
            customer_id = session['customer_id']
            cursor.execute('SELECT addressID FROM CUSTOMER_ADDRESS WHERE customerID = %s LIMIT 1',
                           (customer_id,))
            address = cursor.fetchone()
            address_id = address['addressID'] if address else None
            cursor.execute('''
                INSERT INTO `ORDER` (customerID, orderPrice, shippingAddressID, status)
                VALUES (%s, %s, %s, 'pending')
            ''', (customer_id, total, address_id))
            order_id = cursor.lastrowid
            for product_id, item in cart.items():
                cursor.execute('''
                    INSERT INTO ORDER_PRODUCT (orderID, productID, quantity)
                    VALUES (%s, %s, %s)
                ''', (order_id, int(product_id), item['quantity']))
                cursor.execute('''
                    UPDATE PRODUCT SET stock = stock - %s WHERE productID = %s
                ''', (item['quantity'], int(product_id)))
            conn.commit()
            cursor.close()
            conn.close()
            session.pop('cart', None)
            flash(f'تم تأكيد طلبك بنجاح! رقم الطلب: #{order_id}', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'حدث خطأ في تأكيد الطلب: {str(e)}', 'error')
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    cart_count = len(cart)
    return render_template('checkout.html', cart=cart, total=total, cart_count=cart_count)

# =====================
# ملف الشخصي
# =====================
@app.route('/profile')
@login_required
def profile():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM CUSTOMER WHERE customerID = %s', (session['customer_id'],))
        customer = cursor.fetchone()
        cursor.execute('''
            SELECT o.*, COUNT(op.productID) as item_count
            FROM `ORDER` o
            LEFT JOIN ORDER_PRODUCT op ON o.orderID = op.orderID
            WHERE o.customerID = %s
            GROUP BY o.orderID
            ORDER BY o.orderDate DESC
        ''', (session['customer_id'],))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        cart_count = len(session.get('cart', {}))
        return render_template('profile.html', customer=customer, orders=orders, cart_count=cart_count)
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)