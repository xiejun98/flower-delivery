from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# 用户基类：封装通用属性，不同角色复用
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # consumer/shop/rider/admin
    phone = db.Column(db.String(20))

# 鲜花商品类
class FlowerProduct(db.Model):
    __tablename__ = 'flower_product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))

# 收货地址类
class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    detail = db.Column(db.String(200))
    is_default = db.Column(db.Boolean, default=False)

# 订单类：状态多态（待付款/待接单/配送中/已完成/异常）
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(30), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    flower_id = db.Column(db.Integer, db.ForeignKey('flower_product.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    status = db.Column(db.String(20), default='pending')
    create_time = db.Column(db.DateTime, default=datetime.now)
    rider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)