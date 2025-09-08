from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):

    user_id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    user_fname = db.Column(db.String(500),nullable=False)
    user_lname = db.Column(db.String(500),nullable=False)
    user_email = db.Column(db.String(300),nullable=False,unique=True)
    user_password = db.Column(db.String(500),nullable=False)
    user_address = db.Column(db.String(500))
    user_phone = db.Column(db.String(20))
    user_dp = db.Column(db.String(200))
    user_status = db.Column(db.Enum('active','inactive'),default='inactive')
    user_date_created = db.Column(db.DateTime(),default=datetime.now)
    user_date_updated = db.Column(db.DateTime(),default=datetime.now,onupdate=datetime.now)

    def __repr__(self):
        return f"{self.user_fname} : {self.user_lname}"
 
class Box(db.Model):
    box_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    box_name = db.Column(db.String(200))
    box_size = db.Column(db.Enum('Large','Medium','Small'))
    box_price = db.Column(db.Integer)
    box_image = db.Column(db.String(300))
    box_status = db.Column(db.Enum('enabled','disabled'),default='enabled')
    box_created_at = db.Column(db.DateTime(),default=datetime.now)
    box_updated_at = db.Column(db.DateTime(),default=datetime.now,onupdate=datetime.now)

    def __repr__(self):
        return f"{self.box_name} : {self.box_id}"

class Plan(db.Model):
    plan_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    plan_frequency = db.Column(db.Enum('weekly','one_off','biweekly','monthly'),nullable=False)
    plan_created_at = db.Column(db.DateTime(),default=datetime.now)
    plan_updated_at = db.Column(db.DateTime(),default=datetime.now,onupdate=datetime.now)


class Orders(db.Model):
    order_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    order_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    order_box_id = db.Column(db.Integer,db.ForeignKey('box.box_id'))
    order_plan_id = db.Column(db.Integer,db.ForeignKey('plan.plan_id'))
    order_pay_status = db.Column(db.Enum('pending','paid'))
    order_delivery_status = db.Column(db.Enum('pending','paid'))
    is_one_time = db.Column(db.Boolean())
    is_reoccuring = db.Column(db.Boolean())
    order_created_at = db.Column(db.DateTime(),default=datetime.now)
    order_updated_at = db.Column(db.DateTime(),default=datetime.now,onupdate=datetime.now)
    # order_ref =  db.Column(db.Integer)

    user = db.relationship('User', backref='orders')
    plan = db.relationship('Plan', backref='planorders')
    box = db.relationship('Box', backref='orders')


class Subscriptions(db.Model):
    sub_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    sub_userid = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    sub_boxid = db.Column(db.Integer,db.ForeignKey('box.box_id'))
    sub_planid = db.Column(db.Integer,db.ForeignKey('plan.plan_id'))
    sub_orderid = db.Column(db.Integer,db.ForeignKey('orders.order_id'))
    sub_startdate = db.Column(db.DateTime,default=datetime.now())
    sub_nextdeliverydate = db.Column(db.DateTime)
    sub_authorization_code = db.Column(db.String(300))
    sub_status = db.Column(db.Enum('active','inactive','cancelled'),default='inactive')
    sub_lastdeliverydate = db.Column(db.DateTime)
    sub_createdat = db.Column(db.DateTime,default=datetime.now)
    sub_updatedat = db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)


    #relationships
    user = db.relationship('User',backref="usersub")
    box = db.relationship('Box',backref="boxsub")
    plan = db.relationship('Plan',backref="plansub")
    order = db.relationship('Orders',backref="ordersub")


class Payments(db.Model):
    pay_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    pay_orderid = db.Column(db.Integer,db.ForeignKey('orders.order_id'))
    pay_subid = db.Column(db.Integer,db.ForeignKey('subscriptions.sub_id'))
    pay_userid = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    pay_amount = db.Column(db.Integer)
    
    pay_status = db.Column(db.Enum('pending','successful','failed'))
    pay_transactionref = db.Column(db.String(500))
    pay_attemptedat = db.Column(db.DateTime,default=datetime.now)
    pay_createdat = db.Column(db.DateTime,default=datetime.now)
    pay_updatedat = db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    pay_actual = db.Column(db.Float(), nullable=True) #actual amount deducted
    pay_data = db.Column(db.Text(),nullable=True)

    #relationships
    orders = db.relationship('Orders',backref="orderpay")
    subscriptions = db.relationship('Subscriptions',backref="subpay")
    user = db.relationship('User',backref="userpay")


class Fruit(db.Model):
    fruit_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    fruit_name = db.Column(db.String(100))


class FruitBox(db.Model):
    fruitbox_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    fruitbox_boxid = db.Column(db.Integer,db.ForeignKey('box.box_id'))
    fruitbox_fruitid = db.Column(db.Integer,db.ForeignKey('fruit.fruit_id'))

    box = db.relationship('Box',backref="fruitbox")
    fruitss = db.relationship('Fruit',backref="myfruits",uselist=False)
    def __repr__(self):
        return f"{self.fruitbox_fruitid} : {self.fruitbox_boxid}"


class Admin(db.Model):
    admin_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    admin_email = db.Column(db.String(50))
    admin_pwd = db.Column(db.String(200))
    admin_loggedin = db.Column(db.Enum('1','0'),default='0')


