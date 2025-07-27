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
    user_date_created = db.Column(db.DateTime(),default=datetime.now())
    user_date_updated = db.Column(db.DateTime(),default=datetime.now(),onupdate=datetime.now())

    def __repr__(self):
        return f"{self.user_fname} : {self.user_lname}"
 
class Box(db.Model):
    box_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    box_name = db.Column(db.String(200))
    box_size = db.Column(db.String(200))
    box_price = db.Column(db.Integer)
    box_content = db.Column(db.String(2000))
    box_created_at = db.Column(db.DateTime(),default=datetime.now())
    box_updated_at = db.Column(db.DateTime(),default=datetime.now(),onupdate=datetime.now())

    def __repr__(self):
        return f"{self.box_name} : {self.box_id}"

class Plan(db.Model):
    plan_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    plan_frequency = db.Column(db.Enum('weekly','biweekly','monthly'),nullable=False)
    plan_created_at = db.Column(db.DateTime(),default=datetime.now())
    plan_updated_at = db.Column(db.DateTime(),default=datetime.now(),onupdate=datetime.now())

# class Subscription(db.Model,Plan):
#     sub_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
#     if Plan.plan_frequency == 'weekly':
#         next_delivery_date = db.Column(db.DateTime(),default=datetime.now() + timedelta(days=7))
#     elif Plan.plan_frequency == 'biweekly':
#         next_delivery_date = db.Column(db.DateTime(),default=datetime.now() + timedelta(days=14))
#     elif Plan.plan_frequency == 'monthly':
#         next_delivery_date = db.Column(db.DateTime(),default=datetime.now() + timedelta(days=30))

class Orders(db.Model):
    order_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    order_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    order_box_id = db.Column(db.Integer,db.ForeignKey('box.box_id'))
    order_pay_status = db.Column(db.Enum('pending','paid'))
    # order_delivery_status = db.Column(db.Integer,db.Enum('pending','paid'))
    is_one_time = db.Column(db.Boolean())
    is_reoccuring = db.Column(db.Boolean())
    order_created_at = db.Column(db.DateTime(),default=datetime.now())
    order_updated_at = db.Column(db.DateTime(),default=datetime.now(),onupdate=datetime.now())

    user = db.relationship('User', backref='orders')
    box = db.relationship('Box', backref='orders')


# class Payment(db.Model):
#     payment_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
#     payment_order_id = db.Column(db.Integer,db.ForeignKey('order.order_id'))
#     payment_sub_id = db.Column(db.Integer,db.ForeignKey('subscription.sub_id'))
#     payment_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'))
#     payment_method = 