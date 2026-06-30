import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, FlowerProduct, Order, Address

app = Flask(__name__)
app.secret_key = 'flower_delivery_course_2024'

# 数据库适配：本地SQLite，线上Render PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///flower.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 登录管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- 公共路由 ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            role_route = {
                'consumer': 'consumer_home',
                'shop': 'shop_orders',
                'rider': 'rider_orders',
                'admin': 'admin_dashboard'
            }
            return redirect(url_for(role_route.get(user.role, 'consumer_home')))
        flash('账号或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------- 消费者端路由 ----------
@app.route('/')
@login_required
def consumer_home():
    flowers = FlowerProduct.query.all()
    return render_template('consumer_home.html', flowers=flowers)

@app.route('/address')
@login_required
def address_list():
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('address.html', addresses=addresses)

@app.route('/my/orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('my_orders.html', orders=orders)

# ---------- 商家端路由 ----------
@app.route('/shop/orders')
@login_required
def shop_orders():
    if current_user.role != 'shop':
        return redirect(url_for('login'))
    orders = Order.query.all()
    return render_template('shop_orders.html', orders=orders)

# ---------- 骑手端路由 ----------
@app.route('/rider/orders')
@login_required
def rider_orders():
    if current_user.role != 'rider':
        return redirect(url_for('login'))
    orders = Order.query.filter_by(rider_id=current_user.id).all()
    return render_template('rider_orders.html', orders=orders)

# ---------- 初始化数据 ----------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='consumer1').first():
        users = [
            User(username='consumer1', password=generate_password_hash('123456'), role='consumer', phone='13800000001'),
            User(username='shop1', password=generate_password_hash('123456'), role='shop', phone='13800000002'),
            User(username='rider1', password=generate_password_hash('123456'), role='rider', phone='13800000003'),
            User(username='admin', password=generate_password_hash('admin123'), role='admin', phone='13800000000')
        ]
        flowers = [
            FlowerProduct(name='红玫瑰花束', price=99.9, stock=50, category='花束'),
            FlowerProduct(name='向日葵礼盒', price=129, stock=30, category='礼盒')
        ]
        db.session.add_all(users + flowers)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)