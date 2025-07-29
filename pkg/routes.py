from flask import Flask,render_template,redirect,flash,request,session
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf
from pkg.forms import RegisterForm,FruitSizeForm,DeliveryDetailsForm,LoginForm
from pkg.models import db,User,Plan,Box
 





@app.route('/')
def index():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
    return render_template('index.html',user_firstname=user_firstname)



@app.route('/subscription/')
def subscription():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
    return render_template('subscription.html',user_firstname=user_firstname)




@app.route('/ourmission/')
def ourmission():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
    return render_template('ourMission.html',user_firstname=user_firstname)

@app.route('/market/')
def market():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
    return render_template('market.html',user_firstname=user_firstname)

@app.route('/fruitvegcontent/')
def fruitvegcontent():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
    return render_template('fruitvegcontent.html',user_firstname=user_firstname)

@app.route('/VegBoxes/')
def VegBoxes():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
    return render_template('VegBoxes.html',user_firstname=user_firstname)

@app.route('/adminDashboard/')
def adminDashboard():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
    return render_template('adminDashboard.html',user_firstname=user_firstname)



@app.route('/accountdetailspage/')
def accountdetailspage():

    return render_template('account_details_page.html')





@app.route('/register/',methods=['GET','POST'])
def register():
    data = RegisterForm()
    if request.method == "POST" and data.validate():

        #CHECK IF THE EMAIL HAS BEEN USED BY ANOTHER USER
        confirm_email = User.query.filter(User.user_email == data.email.data).first()
        if confirm_email:

            flash('Email aready exists',category='danger')

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

        flash('An account has been created for you, please login.',category='feedback')
        return redirect('/login/')

    return render_template('register.html',data=data)




@app.route('/vegboxesSales/',methods=['GET','POST'])
def vegboxesSales():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname
   
    if request.method == 'POST' :
        #GET THE USER'S CHOICE
        box_size = request.form.get('size')
        box_type = request.form.get('box_type')

        if box_type and box_size:

            #INSTANTIATE AN OBJECT OF THE BOX MODEL
            box = Box(
                box_name = box_type,
                box_size = box_size
            )
            db.session.add(box)
            db.session.commit()
            return redirect('/selectplan/')
        else:
    
            flash('Please select a choice',category='warning')
            return redirect('/selectplan/')
    else:    
        return render_template('vegboxesSales.html',user_firstname=user_firstname)



@app.route('/fruitVegBoxes/',methods=['GET','POST'])
def vegBoxes():

    if request.method== 'POST':
        selected_sizes = request.form.get('fruit_veg_size')
        if selected_sizes == None:
            flash('Please select a choice',category='warning')
            return redirect('/fruitVegBoxes/')
        else:
            return redirect('/selectplan/')


    return render_template('fruitVegBoxes.html')



@app.route('/selectplan/',methods=['GET','POST'])
def selectplan():

    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname

    if request.method=='POST':
  

        #GET THE PLAN CHOSEN BY THE USER
        selected_plan = request.form.get('plan')

        if selected_plan == None:
            flash('please select a plan', category='warning')
            return redirect('/selectplan/')
        else:
             
            user_plan = Plan(
                plan_frequency = selected_plan
            )
            db.session.add(user_plan)
            db.session.commit()

            return redirect('/deliverydetails/')
    return render_template('selectplan.html',user_firstname=user_firstname)



@app.route('/deliverydetails/',methods=['GET','POST'])
def deliverydetails():
    #PERSONALIZATION SECTION OF THE APP, TO MAKE THE USER'S DISPLAY PICTURE APPEAR ON EVERY ROUTE
    user_session_id = session.get('user_online')
    user = User.query.get(user_session_id)
    user_firstname = user.user_fname

    delivery_details = DeliveryDetailsForm()
    if request.method == 'POST' and delivery_details.validate():
        #GET THE DETAILS OF THE USER
        user_address = delivery_details.address.data
        user_phone = delivery_details.phone_number.data

        #UPDATE THE USER TABLE
        user_session_id = session.get('user_online')
        user = User.query.get(user_session_id)
        user.user_address = user_address
        user.user_phone = user_phone

        db.session.commit()

        flash('Details addes successfully',category='success')
        return redirect('/')
 
    return render_template('delivery_details.html',delivery_details=delivery_details,user_firstname=user_firstname)



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
        session.pop('user_online',None)
    return redirect('/login/')


@app.route('/profile/')
def update_profile():
    return render_template('profile.html')