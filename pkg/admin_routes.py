import os,secrets
from datetime import datetime,timedelta
from functools import wraps
from flask import render_template,request,url_for,session,redirect,flash
from werkzeug.security import check_password_hash,generate_password_hash
from pkg import app
from pkg.models import Admin,db,Fruit,Box,Orders,Payments,User,FruitBox
from pkg.forms import LoginForm,CreateBox,UpdateBox


@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache,no-store,must-revalidate'
    return response


def login_required(fn):
    @wraps(fn)
    def login_decorator(*args,**kwargs):
        if session.get('adminonline'):
           return fn(*args,**kwargs)

        else:
            flash('You need to be logged in',category='error')
            return redirect(url_for('admin_login'))
    return login_decorator






@app.route('/admin/login/',methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        login = LoginForm()
        return render_template('admin/login.html')
    else:
        
        password = request.form.get('password')
        email = request.form.get('email')

        admin = db.session.query(Admin).filter(Admin.admin_email == email).first()
        if admin:
            hashed_password = admin.admin_pwd
            check = check_password_hash(hashed_password,password)

            if check:
                session['adminonline'] = admin.admin_id
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid password')
                return redirect(url_for('admin_login'))
        else:
            flash('email does not match any record')
            return redirect(url_for('admin_login'))




@app.route('/admin/dashboard/')
@login_required
def admin_dashboard():
    user = User.query.limit(5).all()
    box = Box.query.all()

    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()

    return render_template('admin/dashboard.html',user=user,box=box,enabled_boxes=enabled_boxes,todays_order=todays_order,sales=sales,users=users)


@app.route('/add/fruit/',methods=['GET','POST'])
@login_required
def add_fruit():
    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()

    if request.method == 'POST':
        fruits = request.form.get('fruit')
        if fruits == '':
            flash('This field cant be empty',category='error')
            return redirect(url_for('add_fruit'))
        else:
            fruit = Fruit(
                fruit_name = fruits
            )
            db.session.add(fruit)
            db.session.commit()
            flash('Fruit added successfully',category='feedback')

    return render_template('admin/addfruit.html',enabled_boxes=enabled_boxes,todays_order=todays_order,sales=sales,users=users)



@app.route('/create/box/',methods=['GET','POST'])
@login_required
def create_box():
    
    createbox = CreateBox()
    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()

    if request.method == 'GET':
        return render_template('admin/createbox.html',createbox=createbox,enabled_boxes=enabled_boxes,todays_order=todays_order,sales=sales,users=users)
    else:
        if createbox.validate():
            boxname = createbox.boxname.data
            boxprice = createbox.boxprice.data
            boxsize = createbox.boxsize.data
            boximage = request.files.get("boximage")

            # Check if box already exists
            box = Box.query.filter(Box.box_name == boxname).first()
            if box:
                flash('This box already exists',category='error')
                return redirect(url_for('create_box'))
            else:

                if boximage and boximage.filename:
                
                    image = boximage.filename
                    img_name,ext = os.path.splitext(image)
                    newname = secrets.token_hex(10) + ext
                    boximage.save("pkg/static/userimages/"+newname)
  

                box = Box(
                    box_name = boxname,
                    box_size = boxsize,
                    box_price = boxprice,
                    box_image = newname
                )     
                db.session.add(box)
                db.session.commit()
        else:
            flash('Enter correct inputs',category='error')
            return redirect(url_for('create_box'))
        
        flash('Box created successfully',category='feedback')
        return redirect(url_for('create_box'))
    

        

@app.route('/update/box/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_box(id):
    Update_box = UpdateBox()
    box = Box.query.get_or_404(id)
    fruits = Fruit.query.all()
    fruit_and_box = FruitBox.query.filter(FruitBox.fruitbox_boxid == id).all()

    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()


    if request.method == 'GET':
        return render_template('admin/updatebox.html', Update_box=Update_box, box=box,fruits=fruits,fruit_and_box=fruit_and_box,enabled_boxes=enabled_boxes,todays_order=todays_order,sales=sales,users=users)

    if Update_box.validate_on_submit():
        box.box_name = Update_box.boxname.data
        box.box_price = Update_box.boxprice.data
        box.box_size = Update_box.boxsize.data

        # GRAB ALL THE SELECTED FRUITS
        selected_fruits = request.form.getlist('fruit_ids')
        # LOOP OVER THE SELECTED FRUITS, ADD EACH SELECTED FRUIT INTO THE FRUITBOX TABLE

        for selected_fruit in selected_fruits:
            fruit_box = FruitBox(
                fruitbox_boxid = id,
                fruitbox_fruitid = selected_fruit
            )
            db.session.add(fruit_box)
            db.session.commit()

        boximage = request.files.get("boximage")
        if boximage and boximage.filename:
            image = boximage.filename
            img_name, ext = os.path.splitext(image)
            newname = secrets.token_hex(10) + ext
            boximage.save("pkg/static/userimages/" + newname)
            box.box_image = newname

        db.session.commit()
        flash('Box updated successfully', 'feedback')
        return redirect(url_for('admin_dashboard'))

    flash('Enter correct inputs', 'error')
    return render_template('admin/updatebox.html', Update_box=Update_box, box=box,fruits=fruits,fruit_and_box=fruit_and_box)



@app.route('/admin/logout/')
@login_required
def admin_logout():
    session.pop('adminonline')
    return redirect(url_for('admin_login'))


@app.route('/orders/')
@login_required
def all_orders():
    
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    # print(todays_order)
    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()

    return render_template('admin/all_orders.html',todays_order=todays_order,enabled_boxes=enabled_boxes,sales=sales,users=users)




@app.route('/admin/payments/')
@login_required
def admin_payments():
    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()

    pay = Payments.query.all()
    return render_template('admin/payments.html',pay=pay,enabled_boxes=enabled_boxes,todays_order=todays_order,sales=sales,users=users)


@app.route('/view/users/')
@login_required
def view_users():

    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()

    user = User.query.all()
    return render_template('admin/view_users.html',user=user,enabled_boxes=enabled_boxes,todays_order=todays_order,sales=sales,users=users)




@app.route('/user/page/<id>/')
@login_required
def user_page(id):

    user = User.query.get(id)
    return render_template('admin/user_page.html',user=user)



@app.route('/user/order/<id>/')
@login_required
def user_order(id):
    user = User.query.get(id)

    order = Orders.query.filter(Orders.order_user_id == id).all()
    return render_template('admin/user_order.html',order=order,user=user)




@app.route('/view/boxes/')
@login_required
def view_boxes():
    users = User.query.filter(User.user_status == 'active').all()
    boxes = Box.query.all()
    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()

    return render_template('admin/view_boxes.html',boxes=boxes,users=users,todays_order=todays_order,sales=sales,enabled_boxes=enabled_boxes)


@app.route('/box/contents/<id>/')
@login_required
def box_contents(id):
    box = Box.query.get(id)
    fruit_box = FruitBox.query.filter(FruitBox.fruitbox_boxid == id).all()

    enabled_boxes = Box.query.filter(Box.box_status == 'enabled').all()
    today = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    todays_order = Orders.query.filter(Orders.order_created_at >= today, Orders.order_created_at < tomorrow,Orders.order_pay_status == 'paid').all()
    sales = Payments.query.filter(Payments.pay_createdat >= today, Payments.pay_createdat < tomorrow,Payments.pay_status == 'successful').all()
    users = User.query.filter(User.user_status == 'active').all()

    return render_template('admin/box_content.html',box=box,fruit_box=fruit_box,enabled_boxes=enabled_boxes,todays_order=todays_order,sales=sales,users=users)



@app.route('/box/status/<id>/')
@login_required
def box_status(id):
    box = Box.query.get(id)
    if box.box_status == 'enabled':
        box.box_status = 'disabled'
        db.session.commit()
        flash('Box disabled successfully',category='feedback')
        return redirect(url_for('view_boxes'))
    else:
        box.box_status = 'enabled'
        db.session.commit()
        flash('Box enabled successfully',category='feedback')
        return redirect(url_for('view_boxes'))
    
