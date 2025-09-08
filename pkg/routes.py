import os,secrets,random,json,requests,time,threading
from functools import wraps
from datetime import datetime,timedelta
from flask import Flask,render_template,redirect,flash,request,session,url_for,current_app
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf,mail
from flask_mail import Message
from pkg.forms import RegisterForm,FruitSizeForm,DeliveryDetailsForm,LoginForm,UpdateProfileForm,UpdatePasswordForm
from flask_wtf.file import FileAllowed
from pkg.models import db,User,Plan,Box,Orders,Subscriptions,Payments,FruitBox
import schedule

@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache,no-store,must-revalidate'
    return response


def login_required(fn):
    @wraps(fn)
    def login_decorator(*args,**kwargs):
        if session.get('user_online'):
           return fn(*args,**kwargs)

        else:
            flash('You need to be logged in',category='error')
            return redirect(url_for('login'))
    return login_decorator



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)



@app.route('/')
def index():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user = None 
    return render_template('index.html',user=user)

    


@app.route('/subscription/')
def subscription():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user = None
    return render_template('subscription.html',user = user)





@app.route('/ourmission/')
def ourmission():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user = None
    return render_template('ourMission.html',user=user)


@app.route('/market/')
def market():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online',None)
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user = None
    return render_template('market.html',user=user)




@app.route('/register/',methods=['GET','POST'])
def register():
    data = RegisterForm()
    if request.method == "POST" and data.validate():

        #CHECK IF THE EMAIL HAS BEEN USED BY ANOTHER USER
        confirm_email = User.query.filter(User.user_email == data.email.data).first()
        if confirm_email:

            flash('Email already exists',category='danger')
            return redirect(url_for('register'))
        else:

            #MAKE THE PASSWORD HASHED FOR SECURITY PURPOSE
            hashed_pass = generate_password_hash(data.password.data)

            #STORING ALL USER DATA IN THE DATABASE
            customer = User(
                user_fname = data.firstname.data,
                user_lname = data.lastname.data,
                user_email = data.email.data,
                user_password = hashed_pass
            )
            db.session.add(customer)
            db.session.commit()

            #AFTER SUCCESSFULLY REGISTERING THE USER, WE WILL SEND AN EMAIL TO THE USER TO CONFIRM THEIR REGISTRATION
            #WE WILL USE THE FLASK MAIL EXTENSION TO SEND THE EMAIL
            #SEND AN EMAIL TO THE USER TO CONFIRM THEIR REGISTRATION
            msg = Message(
                subject=" Welcome to Frrutts - Freshness Delivered to Your Doorstep!",
                sender=("Frrutts Support","frrutts@gmail.com"),
                recipients=[data.email.data]
            )
            msg.html = f"""<body style='font-family: Arial, sans-serif; text-align:center;'>
                <div style='text-align:center;'>
                    <h1>Welcome to Frrutts, {data.lastname.data.title}!</h1>
                    <p>We're so excited to bring the freshest fruits straight from the farm to your doorstep.</p> <br/>

                    <p>With Frrutts, you can:</p>
                    <ul style='list-style-type: none; text-align: left; margin-left: 20px;'>
                        <li> Shop fresh fruits anytime.</li>
                        <li> Subscribe for regular deliveries tailored to your needs.</li>
                        <li>Swap your boxes to try something new each time.</li>
                        <li> Update your plan whenever you like.</li>
                    </ul> <br/>

                    <p>Getting started is easy:</p>
                    <ul style='list-style-type: none; text-align: left; margin-left: 20px;'>
                        <li>Log in to your account.</li>
                        <li>Browse our box selection or set up your subscription.</li>
                        <li>Sit back, relax, and enjoy farm-fresh goodness delivered to you.</li>
                    </ul> <br/>

                    <p>If you ever need a hand, our friendly support team is here for you.</p>
                    <span><strong>📩 Contact us:</strong> <a href="mailto:frrutts@gmail.com">frrutts@gmail.com</a> </span>

                    <p>Here’s to fresh beginnings!</p>
                    <p>Cheers,</p>
                    <p>The Frrutts Team</p>
                    <p style='font-size: 0.8em; color: gray;'>P.S. Don't forget to check out our <a href='https://frrutts.com/'>website</a> for the latest updates and offers!</p>
                </div>
            </body> """
            threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


            flash('An account has been created for you, please login.',category='feedback')
            return redirect('/login/')

    return render_template('register.html',data=data)




@app.route('/selectplan/<id>/',methods=['GET','POST'])
@login_required
def selectplan(id):

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)    
    else:
        user = None

    if request.method=='POST':
        #GET THE PLAN CHOSEN BY THE USER
        selected_plan = request.form.get('plan')

        if selected_plan == None:
            flash('please select a plan', category='warning')
            return redirect(url_for('selectplan',id=id))
        else:             

            session['plan_frequency'] = selected_plan
            box = Box.query.get(id)
            plan = Plan.query.filter(Plan.plan_frequency == session.get('plan_frequency')).first()

            order = Orders(
                order_user_id = session.get('user_online'),
                order_box_id = box.box_id,
                order_pay_status = 'pending',
                order_delivery_status = 'pending',
                order_plan_id = plan.plan_id,
            )
            db.session.add(order)
            db.session.commit()

            print(session.get('plan_frequency'))
            flash('box selected',category='feedback')
            return redirect(url_for('confirm_details'))
            

    return render_template('selectplan.html',user=user)




@app.get('/confirm/details/')
@login_required
def confirm_details():
    user_session_id = session.get('user_online')
    order = Orders.query.filter_by(order_user_id=user_session_id).order_by(Orders.order_created_at.desc()).first()
    if order:
        #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
        
        if user_session_id:
            user = User.query.get(user_session_id)
        else:
            user = None

        delivery_details = DeliveryDetailsForm()
        return render_template('confirm.html',delivery_details=delivery_details,user=user,order=order)
    else:
        flash('You need to select a box first',category='warning')
        return redirect('/boxes/')


@app.post('/payment/')
@login_required
def payment():
    delivery_details = DeliveryDetailsForm()
    user_session_id = session.get('user_online')

    if delivery_details.validate():
        #GET THE DETAILS OF THE USER
        user_address = delivery_details.address.data
        user_phone = delivery_details.phone_number.data

            

        #UPDATE THE USER TABLE
        user = User.query.get(user_session_id)

        user.user_address = user_address
        user.user_phone = user_phone
        db.session.commit()

        order = Orders.query.filter_by(order_user_id=user_session_id).order_by(Orders.order_created_at.desc()).first()
        user_frequency = session.get('plan_frequency')

        plan = Plan.query.filter(Plan.plan_frequency == user_frequency).first()

        #check if plan is one off or reoccuring
        if user_frequency == 'one_off':
            order.is_one_time = True
            order.is_reoccuring = False
        else:
            order.is_one_time = False
            order.is_reoccuring = True
        db.session.commit()

        #if the user is on one off plan, don't create a subscription

        if user_frequency != 'one_off':

            sub = Subscriptions( 
                sub_userid = order.user.user_id,
                sub_boxid = order.box.box_id,
                sub_planid = plan.plan_id,
                sub_orderid = order.order_id,
                sub_startdate = datetime.now(),
                sub_status = 'inactive',
                sub_lastdeliverydate = datetime.now()
            )
            db.session.add(sub)
            db.session.commit()

        subscription = Subscriptions.query.filter(Subscriptions.sub_userid == user_session_id).first()

        # pay_method = request.form.get('payment_method')
        ref = int(random.random() * 1000000000000)
        pay = Payments(
            pay_orderid = order.order_id,
            pay_subid = subscription.sub_id if subscription else None,
            pay_userid = user_session_id,
            pay_amount = order.box.box_price,
            pay_status = 'pending',
            # pay_method = pay_method,
            pay_transactionref = ref,
            pay_attemptedat = datetime.now()
        )
        db.session.add(pay)
        db.session.commit()
        session['payref'] = ref
        return redirect(url_for('paystack_step1'))

    else:
        #IF THE FORM IS NOT VALID, RENDER THE TEMPLATE WITH THE FORM
        flash('Please fill in the form correctly',category='error')
        #RENDER THE TEMPLATE WITH THE FORM
        return redirect(url_for('confirm_details'))




@app.route('/login/',methods=['GET','POST'])
def login():


    login = LoginForm()
    if request.method == 'POST' and login.validate():
            
        email = login.email.data
        pwd = login.password.data
        
        #INSTANTIATE AN OBJECT OF THE USER TABLE
        #SEARCH IF THE EMAIL EXIST IN THE DATABASE, FETCH THE RECORD
        user = User.query.filter(User.user_email == email).first()
        
        #IF A USER WITH THE RECORD EXISTS, CHECK IF THE PASSWORD IN THE FORM AND THE PASSWORD IN THE DATABASE MATCHES
        if user:      
            #RETRIEVE THE HASHED PASSWORD FROM THE DATABASE AND COMPARE WITH THE PASSWORD FROM THE FORM
            hashed_pass = user.user_password

            rsp = check_password_hash(hashed_pass,pwd)
            #IF THE PASSWORD MATCHES THE EMAIL
            if rsp:
                session['user_online'] = user.user_id #WE ARE NOW LOGGED IN BY SAVING IN SESSION

                user = User.query.get(session.get('user_online'))
                user.user_status = 'active'
                db.session.commit()
                return redirect('/')
            else:
                #IF THE PASSWORD DOES NOT MATCH THE EMAIL
                flash('Invalid Credentials',category='error')
                return redirect('/login/')
        else:
            flash('Invalid Credentials',category='error')
            return redirect('/login/')       
    else:
        return render_template('login.html',login=login)
    


@app.route('/logout/')
def logout():

    if session.get('user_online') != None:   
        user = User.query.get(session.get('user_online'))
        if user:
            user.user_status = 'inactive'
            db.session.commit()
            session.pop('user_online',None)
            
    return redirect('/login/')





@app.route('/settings/',methods=['GET','POST'])
@login_required
def update_profile():
    title = "User Settings"
    profile_form = UpdateProfileForm()

    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user=None    


    if request.method == 'POST':
        
        #VALIDATE THE DATA AND IF ITS TRUE, UPDATE THE USER TABLE TO THE NEW DATA ENTERED
        
        if profile_form.validate():
            user_session_id = session.get('user_online')
            user = User.query.get(user_session_id)
            
            #UPDATE THE USER TABLE WITH THE NEW DATA
            user.user_fname = profile_form.firstname.data
            user.user_lname = profile_form.lastname.data
            user.user_email = profile_form.email.data
            user.user_address = profile_form.address.data
            user.user_phone = profile_form.phone.data


            #RETRIEVING THE USER DISPLAY PICTURE
            userdp = request.files.get('dp')
            if userdp:
                #rename the filenames to avoid clashes
                image = userdp.filename
                imagename,extension = os.path.splitext(image)
                newname = secrets.token_hex(10) + extension
                userdp.save("pkg/static/userimages/"+newname)

                user.user_dp = newname
            #COMITTING ALL DATA TO THE DATABASE
            db.session.commit()
            flash('Profile Updated',category='feedback')
            return redirect(url_for('update_profile'))

        else:
            flash('Enter correct inputs',category='error')          
            
    return render_template('settings.html',profile_form=profile_form,user=user,title=title)






@app.route('/password/',methods=['GET','POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    title = "Change Password"
    
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user=None

    if request.method == 'GET':
        return render_template('userprofile/password.html',form=form,user=user,title=title)
    else:
        form.validate()

        oldpassword = form.oldpassword.data
        confpass = form.confirmpassword.data
        newpassword = form.newpassword.data
        if confpass != newpassword:
            flash('Passwords do not match',category='error')
            return redirect(url_for('update_password'))
        else:

            user = User.query.get(session.get('user_online'))
            hashed_password = user.user_password
            check_hashed = check_password_hash(hashed_password,oldpassword)

            if check_hashed:
                user.user_pwd = newpassword
                db.session.commit()

                flash('Password changed successfully',category='info')
                session.pop('user_online',None)
                return redirect(url_for('login'))
            else:
                flash('Incorrect password, please check the password and try again',category='error')
                return redirect(url_for('update_password'))
        

@app.route('/boxes/')   
@login_required 
def boxes():
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user=None

    boxes = Box.query.all()
    fruitboxes = FruitBox.query.all()

    return render_template('boxes.html',boxes=boxes,user=user,fruitboxes=fruitboxes) 



    
@app.route('/paystack/')
@login_required
def paystack_step1():    

    ref = session.get('payref')

    pay_details = Payments.query.filter(Payments.pay_transactionref == ref).first()
    amount = pay_details.pay_amount
    user_details = User.query.get(session.get('user_online'))
    email = user_details.user_email #we can also use relationship to get this


    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Content-type": "application/json","Authorization":"Bearer sk_test_f1d30d38d492ebd83fb3e9da8ed0b128ebef2a6c"}
    data = {"reference":ref,"amount":amount*100,"email":email,"callback_url":"http://127.0.0.1:5800/paystack/update"}

    #we want to connect to the endpoint. it is a post request
    try:
        response = requests.post(url,headers=headers,data=json.dumps(data))
        
        json_response = response.json()


        if json_response['status'] == True:
            pay_url = json_response['data']['authorization_url']
            return redirect(pay_url)
        else:
            paystack_error = json_response['message']
            flash(f'Error from paystack: {paystack_error}',category='error')
            return json_response
        
    except requests.exceptions.RequestException as e:
        flash(f"Connection error: {str(e)}", category='error')
        return redirect(url_for('confirm_details'))


@app.route('/paystack/update/')
@login_required
def paystack_update():

        ref = session.get('payref')
        if ref:

            #update the database,we need to connect to paystack to verify the transaction
            url = f"https://api.paystack.co/transaction/verify/{ref}"
            headers = {"Content-type": "application/json","Authorization":"Bearer sk_test_f1d30d38d492ebd83fb3e9da8ed0b128ebef2a6c"}
            response = requests.get(url,headers=headers)
            json_response = response.json()

            actual = 0
            if json_response.get('status') == True:
                actual = json_response['data']['amount'] / 100
                gateway_rsp = json_response['data']['gateway_response']
                
                if gateway_rsp == 'Successful':
                    status = 'successful'
                    order = Orders.query.filter_by(order_user_id=session.get('user_online')).order_by(Orders.order_id.desc()).first()

                    # sub = Subscriptions.query.filter(Subscriptions.sub_userid ==session.get('user_online')).first()
                    sub = Subscriptions.query.filter_by(sub_userid=session.get('user_online')).order_by(Subscriptions.sub_id.desc()).first()

                    # UPDATE THE ORDER TABLE TO PAID SINCE THE TRANSACTION WAS SUCCESSFUL
                    if order:
                        order.order_pay_status = 'paid'
                        db.session.commit()

                    # UPDATE THE SUBSCRIPTION STATUS IN THE SUBSCRIPTION TABLE TO ACTIVE

                    if sub:
                        if order.plan.plan_frequency == 'weekly' :
                            sub_nextdeliverydate = datetime.now() + timedelta(days=7)
                        elif order.plan.plan_frequency == 'biweekly':
                            sub_nextdeliverydate = datetime.now() + timedelta(days=14)
                        elif order.plan.plan_frequency == 'monthly' :
                            sub_nextdeliverydate = datetime.now() + timedelta(days=30)
                        


                        sub.sub_nextdeliverydate = sub_nextdeliverydate
                        sub.sub_authorization_code = json_response['data']['authorization']['authorization_code']
                        sub.sub_status = 'active'
                        db.session.commit()

                else:
                    status = 'failed'
                    return redirect(url_for('user_profile'))
            else:
                status ='failed'
                return redirect(url_for('user_profile'))

            #THE FOLLOWING WILL BE EXECUTED REGARDLESS IF RESPONSE IS TRUE OR NOT. THAT IS WHY WE DID NOT INDENT IT
            pay = Payments.query.filter(Payments.pay_transactionref == ref).first()
            pay.pay_actual = actual
            pay.pay_status = status
            pay.pay_data = json.dumps(json_response)



            db.session.commit()
            flash(f'Transaction completed {status}',category='feedback')
            return redirect(url_for('user_profile'))
                
        else:
            flash('Continue from here',category='error')
            return redirect(url_for("confirm_details"))



@app.route('/payments/')
@login_required
def user_payments():

    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)    
    else:
        user = None

    title = "Payments Page"
    pay = Payments.query.filter(Payments.pay_userid == user_session_id)
    return render_template('userprofile/payments.html',user=user,title=title,pay=pay)






@app.errorhandler(404)
def page_not_found(e):

    return render_template('error_pages/404.html',e=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error_pages/500.html',e=e), 500






@app.route('/update/plan/<id>/',methods=['GET','POST'])
@login_required
def update_plan(id):

    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user = None
    
    plan = Plan.query.filter(Plan.plan_frequency != 'one_off').all()
    if request.method ==  'POST':
        #GET THE PLAN CHOSEN BY THE USER
        selected_plan = request.form.get('plan')
        if selected_plan:
            sub = Subscriptions.query.filter(Subscriptions.sub_id == id,Subscriptions.sub_userid == user_session_id).order_by(Subscriptions.sub_id.desc()).first()
            if sub:
                selected_plan = int(selected_plan)

                if sub.sub_planid == selected_plan:
                    flash('You are already subscribed to this plan',category='warning')
                    return redirect(url_for('update_plan',id=id))
                else:
                    sub.sub_planid = selected_plan
                    db.session.commit()
                    flash('Plan updated successfully',category='feedback')
                    return redirect(url_for('view_subscription'))
            else:
                flash('You do not have a subscription',category='error')
                return redirect(url_for('user_profile'))
        else:
            flash('Please select a plan',category='warning')
            return redirect(url_for('update_plan'))

    else:
        return render_template('userprofile/update_plan.html',user=user,plan=plan)
    




@app.route('/profile/')
@login_required
def user_profile():
    title = "User Profile"
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user=None    
    sub = Subscriptions.query.filter(Subscriptions.sub_userid == user_session_id).all()
    return render_template('userprofile/profile.html',user=user,title=title,sub=sub)




@app.route('/view/subscriptions/')
@login_required
def view_subscription():
    title = "User Subscriptions"
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user=None    
    sub = Subscriptions.query.filter(Subscriptions.sub_userid == user_session_id).all()
    return render_template('userprofile/view_subscription.html',user=user,title=title,sub=sub)




@app.route('/cancel/subscription/<int:id>/')
@login_required
def cancel_subscription(id):
    user_session_id = session.get('user_online')
    if user_session_id:
        user = User.query.get(user_session_id)
    else:
        user=None    

    sub = Subscriptions.query.filter(Subscriptions.sub_id == id).first()
    if sub:
        sub.sub_status = 'cancelled'
        db.session.commit()

        #SEND AN EMAIL TO THE USER TO NOTIFY THEM OF THE CANCELLATION
        #WE WILL USE THE FLASK MAIL EXTENSION TO SEND THE EMAIL
        msg = Message(
            subject=" Subscription Cancelled - We'll Miss You!",
            sender=("Frrutts Support", "frrutts@gmail.com"),
            recipients=[user.user_email]
        )

        msg.html = f"""
        <body style="font-family: Arial, sans-serif; text-align: center; color: #333;">
            <h1>Hi {user.user_fname.title}, your subscription has been cancelled.</h1>
            <p>We're sad to see you go! Your <strong>{sub.box.box_name.title}</strong> plan has been successfully cancelled.</p>

            <p style="margin-top: 15px;">
                 <strong>Last Delivery Date:</strong> {sub.sub_lastdeliverydate}<br/>
                🗓 <strong>Next Subscription Date (no longer active):</strong> {sub.sub_nextdeliverydate}
            </p>

            <p>After your last delivery, you will no longer be charged and deliveries will stop.</p>

            <p style="margin-top: 20px;">
                Changed your mind? You can easily reactivate your plan anytime in your 
                <a href="https://frrutts.com/account" style="color:#27ae60; text-decoration:none;">account</a>.
            </p>

            <p style="margin-top: 25px;">
                Thank you for being part of the Frrutts family  — we'd love to serve you again in the future!
            </p>

            <p style="margin-top: 30px; font-size: 14px; color: #555;">
                Cheers,<br/>
                <strong>The Frrutts Team</strong><br/>
                 <a href="mailto:support@frrutts.com" style="color:#27ae60;">support@frrutts.com</a>
            </p>
        </body>
        """
        # Send email asynchronously
        threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


        flash('Subscription cancelled successfully',category='feedback')
        return redirect(url_for('view_subscription'))
    else:
        flash('You do not have a subscription',category='error')
        return redirect(url_for('view_subscription'))
    




@app.route('/swap/box/<int:id>/',methods=['GET','POST'])
def swap_box(id):
    fruitboxes = FruitBox.query.all()
    user_session_id = session.get('user_online')
    if user_session_id: 
        user = User.query.get(user_session_id)
    else:
        user = None
    boxes = Box.query.all()
    title = "Swap Box"
    if request.method == 'POST':
        selected_box = request.form.get('box')
        if selected_box:
            selected_box = int(selected_box)
            sub = Subscriptions.query.filter(Subscriptions.sub_id == id,Subscriptions.sub_userid == user_session_id,Subscriptions.sub_status == 'active').first()
            print(f"sub2.sub_boxid={sub.sub_boxid}, selected_box={selected_box}, type={type(selected_box)}")

            if sub:
                if sub.sub_boxid == selected_box:
                    flash('You are already subscribed to this box',category='warning')
                    return redirect(url_for('swap_box',id=id))
                else:
                    #UPDATE THE SUBSCRIPTION TO THE NEW BOX
                    sub.sub_boxid = selected_box
                    db.session.commit()

                    #SEND AN EMAIL TO THE USER TO NOTIFY THEM OF THE BOX SWAP
                    msg = Message(
                        subject=" Box Swapped Successfully!",
                        sender=("Frrutts Support","frrutts@gmail.com"),
                        recipients=[user.user_email]
                    )    

                    msg.html = f"""<body style='font-family: Arial, sans-serif; text-align:center;'>
                        <h1>Hi {user.user_lname.title}, your box swap is confirmed! </h1>
                        <p>You've successfully swapped to our <strong> {sub.box.box_name} </strong> — more fruits, more freshness, more smiles!</p>

                        <p><strong>What's next?</strong></p>
                        <ul style="list-style-type: none; text-align: left; margin-left: 20px;">
                            <li> Your new plan will start from {sub.sub_nextdeliverydate}</li>
                            <li> We'll pack your upgraded box with farm-fresh goodness.</li>
                            <li> Get ready for an even more delicious experience!</li>
                        </ul>
                        <br/>

                        <p>If you want to make further changes, you can manage your subscription anytime in your 
                        <a href="https://frrutts.com/account">account</a>.</p>

                        <p>Thanks for choosing Frrutts — here's to bigger, juicier boxes! </p>
                        <p>Cheers,</p>
                        <p><strong>The Frrutts Team</strong></p>
                        <span><strong> Contact us:</strong> <a href="mailto:frrutts@gmail.com">support@frrutts.com</a></span>
                    </body> """
                    threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
                    
                    flash('Box swapped successfully',category='feedback')
                    return redirect(url_for('view_subscription'))
            else:
                flash('You do not have an active subscription',category='error')
                return redirect(url_for('user_profile'))
        else:
            flash('Please select a box',category='warning')
            return redirect(url_for('swap_box',id=id))

    return render_template('userprofile/swap_box.html',user=user,boxes=boxes,title=title,fruitboxes=fruitboxes)


PAYSTACK_SECRET_KEY = "sk_test_f1d30d38d492ebd83fb3e9da8ed0b128ebef2a6c"
def billing_logic():
    today = datetime.now().date()
    due_subscriptions = Subscriptions.query.filter(Subscriptions.sub_status == 'active',Subscriptions.sub_nextdeliverydate <= today).all()
    for sub in due_subscriptions:
        payload = {
            "email": sub.user.email,
            "amount": int(sub.box.box_price * 100),  # Paystack requires amount in kobo
            "authorization_code": sub.sub_authorization_code
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post("https://api.paystack.co/transaction/charge_authorization", json=payload, headers=headers)
        res_json = response.json()
        if res_json.get('status') == True and res_json['data']['status'] == 'success':
            # Payment was successful, update subscription and create order
            new_order = Orders(
                order_user_id = sub.sub_userid,
                order_box_id = sub.sub_boxid,
                order_pay_status = 'paid',
                order_delivery_status = 'pending',
                order_plan_id = sub.sub_planid,
            )
            db.session.add(new_order)

             # ✅ Create payment record
            new_payment = Payments(

                pay_subid = sub.sub_id,
                pay_userid = sub.sub_userid,
                pay_amount = sub.box.box_price,
                pay_status = 'successful',
                pay_transactionref = res_json['data']['reference'],
                pay_actual = res_json['data']['amount'] / 100,
                pay_data = json.dumps(res_json),
                pay_attemptedat = datetime.now()
            )
            db.session.add(new_payment)

            # Update next delivery date based on plan frequency
            if sub.plan.plan_frequency == 'weekly':
                sub.sub_nextdeliverydate += timedelta(weeks=1)
            elif sub.plan.plan_frequency == 'biweekly':
                sub.sub_nextdeliverydate += timedelta(weeks=2)
            elif sub.plan.plan_frequency == 'monthly':
                sub.sub_nextdeliverydate += timedelta(days=30)

            db.session.commit()
        else:
            # Handle failed payment (e.g., log it, notify user, etc.)
            print(f"Payment failed for subscription ID {sub.sub_id}. Reason: {res_json.get('message')}")

# Schedule the billing_logic function to run daily at midnight
def schedule_billing():
    schedule.every().day.at("00:00").do(billing_logic)
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def start_scheduler():
    scheduler_thread = threading.Thread(target=schedule_billing)
    scheduler_thread.daemon = True  # Ensure thread exits when main program does
    scheduler_thread.start()       

# Hook scheduler to Flask app
@app.before_request
def activate_scheduler():
    start_scheduler()