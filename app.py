from datetime import datetime, timedelta, timezone
from flask import Flask, session,url_for,render_template,request,redirect,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from sqlalchemy import Date
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "abc"  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ubbbankindia@gmail.com'
app.config['MAIL_PASSWORD'] = 'paoabicdofxqkubi'  # Replace with your actual application-specific password


UPLOAD_FOLDER = 'sts'  # Define the folder where you want to save the files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

SESSION_TIMEOUT = timedelta(minutes=5)

class User(db.Model):
    cust_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    postalcode = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    initial_dep = db.Column(db.String(80), nullable=False)
    def __init__(self,first_name,last_name,phone,email,address,street,postalcode,city,gender,country,date_of_birth,initial_dep):
        self.first_name=first_name
        self.last_name=last_name
        self.phone=phone
        self.email =email
        self.address=address
        self.street = street
        self.postalcode = postalcode
        self.city = city
        self.gender = gender
        self .country = country
        self.date_of_birth = date_of_birth
        self.initial_dep = initial_dep
class admin(db.Model):
    emp_id = db.Column(db.Integer, primary_key=True)
    password=db.Column(db.String(10),nullable=False)
class AC(db.Model):
    ac_no = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, nullable=False)
    fist_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    def __init__(self,fist_name,last_name,phone,cust_id):
        self.fist_name=fist_name
        self.last_name=last_name
        self.phone=phone
        self.cust_id=cust_id


@app.before_request
def check_session_timeout():
    last_activity = session.get('_last_activity')
    if last_activity is not None:
        if datetime.now(timezone.utc) - last_activity > SESSION_TIMEOUT:
            session.clear()
    session['_last_activity'] = datetime.now(timezone.utc)


@app.route('/',methods=["POST","GET"])
def welcome():
    if request.method == "POST":
        a = admin.query.all()
        for item in a:
            emp_id = item.emp_id
            password2 = item.password
        u_name = request.form["username"]
        password1 = request.form["password"]
        if u_name == str(emp_id) and password2 == password1:
            session['username'] = u_name
            return render_template("stafficon1.html")
        else:
            flash("incorrect password")
            flash("enter correct password")
            return render_template("welcome.html")
    return render_template("welcome.html")
@app.route('/create',methods=["POST","GET"])
def create():
    if session.get('username'):
        session['_last_activity'] = datetime.now(timezone.utc)  
        if request.method == "POST":
            first_name = request.form["fname"]
            last_name = request.form["lname"]
            mobile = request.form["phone"]
            email = request.form["email"]
            address = request.form["address"]
            street = request.form["street"]
            postalcode = request.form["postalcode"]
            city = request.form["city"]
            gender = request.form["gender"]
            country = request.form["country"]
            dob = request.form["dob"]
            date_of_birth = datetime.strptime(dob, "%Y-%m-%d").date()
            initial_dep = request.form["deposit"]
            print(dob)
            add_cus = User(first_name,last_name,mobile,email,address,street,postalcode,city,gender,country,date_of_birth,initial_dep)
            db.session.add(add_cus)
            db.session.commit()
            specific_users = User.query.filter_by(email=request.form["email"]).all()
            for item in specific_users:
                cust_id = item.cust_id
            acc_num=AC(fist_name=request.form["fname"],last_name=request.form["lname"],phone=request.form["phone"],cust_id=cust_id)
            db.session.add(acc_num)
            db.session.commit()
            specific_users = AC.query.filter_by(phone=request.form["phone"]).all()
            for item in specific_users:
                ac_no = item.ac_no
            current_date = datetime.now().strftime("%Y-%m-%d")
            file_name = os.path.join(app.config['UPLOAD_FOLDER'] , f'Customer{cust_id}.txt')
            f = open(file_name, "w")
            f.write("ACCOUNT NO: " + str(ac_no) + "      cust_id: " + str(cust_id) + "      open date: " + current_date + "\n" + current_date + "      DEPOSIT"+"         "+str(initial_dep) + "\n")
            b = "Your account has opened successfully your acountc no is:"+str(ac_no)+"and your initial deposit amount is "+str(initial_dep)
            c = "UBB BANK"
            d = "AC OPENED SUCCESSFULLY"
            return redirect(url_for('sms', a=email, b=b, c=c , d=d))
        return render_template("index.html")
    else:
        return"session timeout"

@app.route('/get_data', methods=["POST", "GET"])
def get_data():
    if request.method == "POST" or "GET":
        ac_no = int(request.form["ac_no"])
        specific_data = db.session.query(AC, User).join(User, AC.cust_id == User.cust_id).filter(AC.ac_no == ac_no).first()
        ac_data = {column.name: getattr(specific_data[0], column.name) for column in AC.__table__.columns}
        user_data = {column.name: getattr(specific_data[1], column.name) for column in User.__table__.columns}
            
        combined_data = {**ac_data, **user_data}
        return jsonify(combined_data)
    return render_template("update.html")



@app.route('/ac_details', methods=["POST","GET"])
def ac_details():
    return render_template("update.html")



@app.route('/update', methods=["POST","GET"])
def update():
    if session.get('username'):
        if request.method == "POST":
            ac_no = int(request.form["ac_no"])
            ac_data = AC.query.filter_by(ac_no=ac_no).first()
            if ac_data:
                # Update AC table
                ac_data.fist_name = request.form.get("first_name", ac_data.fist_name)
                ac_data.last_name = request.form.get("last_name", ac_data.last_name)
                ac_data.phone = request.form.get("phone", ac_data.phone)
                # Update other AC fields as needed

                # Update User table
                user_data = User.query.filter_by(cust_id=ac_data.cust_id).first()
                if user_data:
                    user_data.first_name = request.form.get("first_name", user_data.first_name)
                    user_data.last_name = request.form.get("last_name", user_data.last_name)
                    user_data.phone = request.form.get("phone", user_data.phone)
                    user_data.email = request.form.get("email", user_data.email)
                    user_data.address = request.form.get("address", user_data.address)
                    user_data.street = request.form.get("street", user_data.street)
                    user_data.postalcode = request.form.get("postalcode", user_data.postalcode)
                    user_data.city = request.form.get("city", user_data.city)
                    user_data.gender = request.form.get("gender", user_data.gender)

                    # Update other User fields as needed

                    # Commit changes to the database
                    db.session.commit()
                    return jsonify({"message": "Data updated successfully"})
                else:
                    return jsonify({"error": "User data not found"}), 404
            # else:
            #     return jsonify({"error": "Account not found"}), 404
        return render_template("update1.html")
    else:
        flash("session timeout")
        return redirect(url_for("welcome"))
@app.route('/deposit', methods=["POST", "GET"])
def deposit():
    if request.method == "POST":
        ac_no = int(request.form["ac_no"])
        dep_amt = int(request.form["amount"])
        specific_users = AC.query.filter_by(ac_no=ac_no).all()
        for item in specific_users:
            cust_id = item.cust_id
        record = User.query.get(cust_id)
        a = record.email
        record.initial_dep = int(record.initial_dep)+dep_amt
        db.session.commit()
        c = "UBB BANK"
        b = "Your account number" + str(ac_no) +"has been deposited with" + str(dep_amt) + " your current balance is"+ str(record.initial_dep)
        d = "amount deposited"
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_name = os.path.join(app.config['UPLOAD_FOLDER'] , f'Customer{cust_id}.txt')
        f = open(file_name, "a")
        # f.write(  current_date + "      DEPOSIT"+"                    "+str(dep_amt) )
        f.write("{:<12} DEPOSIT {:<10} ".format(current_date,str(dep_amt)))
        return redirect(url_for('sms', a=a, b=b, c=c,d=d))
    return render_template("deposit.html")
@app.route('/withdraw', methods=["POST", "GET"])
def withdraw():
    if request.method == "POST":
        Acc = int(request.form["ac_no"])
        amt = int(request.form["amount"])
        record = AC.query.get(Acc)
        cus = record.cust_id
        record1 = User.query.get(cus)
        bal = record1.initial_dep
        if amt>int(bal):
            flash("INSUFFICIENT BALANCE")
            return render_template("stafficon1.html")
        else:
            record1.initial_dep = int(record1.initial_dep) - amt
            db.session.commit()
            current_date = datetime.now().strftime("%Y-%m-%d")
            file_name = os.path.join(app.config['UPLOAD_FOLDER'] , f'Customer{cus}.txt')
            f = open(file_name, "a")
            # f.write(  current_date + "      WITHDRAW"+"                   "+str(amt) + "\n")
            f.write("{:<12} WITHDRAW {:<10} ".format(current_date,str(amt)))
            a = record1.email
            c = "UBB BANK"
            b = "Your account number" + str(Acc)+"has been debited with" + str(amt) + " your current balance is"+ str(record1.initial_dep)
            d = "amount debited"
            return redirect(url_for('sms', a=a, b=b, c=c,d=d))
    return render_template("withdraw.html")
@app.route('/transfer', methods=["POST", "GET"])
def transfer():
    if request.method == "POST":
        fac = int(request.form["fac"])
        tac = int(request.form["tac"])
        amt = int(request.form["amt"])
        record = AC.query.get(fac)
        record1 = AC.query.get(tac)
        cus = record.cust_id
        cus1 = record1.cust_id
        fetchac = User.query.get(cus)
        fetchac.initial_dep = int(fetchac.initial_dep)-amt
        db.session.commit()
        fetchac1 = User.query.get(cus1)
        x = fetchac.initial_dep
        msg = Message( "UBB BANK", sender='ubbbankindia@gmail.com', recipients=[fetchac.email])
        msg.body = "Amount "+ str(amt)+" is transfered from your account " +str(fac)+ "to "+ fetchac1.first_name+"("+str(tac)+")"+"avl_bal"+str(x)
        mail.send(msg)
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_name = os.path.join(app.config['UPLOAD_FOLDER'] , f'Customer{cus}.txt')
        f = open(file_name, "a")
        f.write(  current_date + "      TFR TO "+"\n"+str(tac)+fetchac1.first_name+"                   "+str(amt) )
        fetchac1.initial_dep = int(fetchac1.initial_dep)+amt
        db.session.commit()
        x = fetchac1.initial_dep
        msg = Message( "UBB BANK", sender='ubbbankindia@gmail.com', recipients=[fetchac1.email])
        msg.body = "Amount "+ str(amt)+" is received from " +fetchac.first_name+"("+str(fac)+")"+"avl_bal"+str(x)
        mail.send(msg)
        file_name = os.path.join(app.config['UPLOAD_FOLDER'] , f'Customer{cus1}.txt')
        f = open(file_name, "a")
        f.write(  current_date + "      TFR FROM "+"\n"+str(fac)+fetchac.first_name+"                   "+str(amt) )
        flash("AMOUNT TRANSFERED")
        return redirect(url_for("demo"))
    return render_template("transfer.html")
@app.route('/api/getname', methods=['GET'])
def get_name():
    id = int(request.args.get('ac'))
    record = AC.query.get(id)
    if not record:
        a = "A/C NOT FOUND"
        return jsonify({'name': a})
    cid = record.cust_id
    record2 = User.query.get(cid)
    x = record2.first_name + "  "+record2.last_name
    a = x.upper()
    return jsonify({'name': a})
@app.route('/sms', methods=["GET","POST"])
def sms():
    if request.method == "GET":
        a = request.args.get('a')
        b = request.args.get('b')
        c = request.args.get('c')
        d = request.args.get('d')
        msg = Message( c, sender='ubbbankindia@gmail.com', recipients=[a])
        msg.body = b
        mail.send(msg)
        flash(d)
        return redirect(url_for("demo"))
@app.route('/demo', methods=["GET","POST"])
def demo():
    return render_template("stafficon1.html")
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure this works without errors
    app.run(host="0.0.0.0", port=8080, debug=True)  # Listen on all interfaces
