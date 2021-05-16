from flask import Flask,redirect,url_for,render_template,request,session

import pymongo
from pymongo import MongoClient
from flask_pymongo import PyMongo
import bcrypt
import pickle
import pandas as pd
import numpy as np
from flask_mail import Mail,Message

app = Flask("__name__")
app.secret_key = "pop_@#$"

app.config['MONGO_DBNAME'] = 'myFirstDatabase'
app.config['MONGO_URI'] = 'mongodb+srv://predictloan:predictloan@cluster0.s0gd5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'

mongo = PyMongo(app)
@app.route("/")
def main():
    return render_template("main.html")



@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name':request.form['nm']})
        if login_user:
            if bcrypt.hashpw(request.form['ps'].encode('utf-8'), login_user['password']) == login_user['password']:
                return redirect(url_for('u'))
            else:
                s=1
                return render_template("login.html",s=s)
        else:
            s=1
            return render_template("login.html",s=s)
    else:
        return render_template("login.html")



@app.route("/login1",methods=["POST","GET"])
def login1():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name':request.form['nm']})
        if login_user:
            if bcrypt.hashpw(request.form['ps'].encode('utf-8'), login_user['password']) == login_user['password']:
                return redirect(url_for('m'))
            else:
                s=1
                return render_template("login1.html",s=s)
        else:
            s=1
            return render_template("login.html",s=s)
    else:
        return render_template("login1.html")

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['nmm']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pss'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['nmm'], 'password' : hashpass})
            session['username'] = request.form['nmm']
            return redirect(url_for('login'))
        
        return 'That username already exists!'

    return render_template("reg.html")

@app.route("/u")
def u():
    return render_template("u.html")

@app.route("/m",methods=["POST","GET"])
def m():
    if request.method == 'POST' and request.form['s']=="yes":
        cluster=MongoClient("mongodb+srv://predictloan:predictloan@cluster0.s0gd5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db=cluster["myFirstDatabase"]
        collection=db["users"]
        x=collection.find({})
        l=[]
        for data in x:
            l.append(data)
        return render_template("d.html",l=l)
    else:

        return render_template("m.html")

@app.route("/d")
def d():
    
    return render_template("d.html")


@app.route("/f")
def f():    
    return render_template("f.html")
@app.route("/f1")
def f1():
    return render_template("f1.html")
@app.route("/f2")
def f2():
    return render_template("f2.html")

@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login"))


@app.route("/layout")
def layout():
    return render_template("layout.html")
@app.route("/layout1")
def layout1():
    return render_template("layout1.html")
@app.route("/layout2")
def layout2():
    return render_template("layout2.html")

@app.route("/webb")
def webb():
    return render_template("webb.html")
@app.route("/webb1")
def webb1():
    return render_template("webb1.html")
@app.route("/webb2")
def webb2():
    return render_template("webb2.html")

#@app.route("/report")
#def report():
#    return render_template("Report.html")



@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for("user", usr=user))


with open('./model/last.pkl', 'rb') as f:
    model = pickle.load(f)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "predictingloan@gmail.com"
app.config['MAIL_PASSWORD'] = "Loan@123"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

#@app.route('/')
#def index():
#    return render_template('index.html')
@app.route('/report')
def report():
    return (render_template('report.html'))


@app.route('/result',methods=['GET','POST'])
def result():    
       
    emp = int(request.form['emp'])    
    home_ownership = request.form['home']   
    if home_ownership=='MORTGAGE':
        home_ownership_cat=0
    elif home_ownership=='OWN':
        home_ownership_cat=1
    else:
        home_ownership_cat=2 
    
    annual_inc = int(request.form['Annual_Income']) 
    loan_amnt = int(request.form['loan_amount'])
    terma = (request.form['terms'])
    if(terma=='36 months'):
        terms=36
    else:
        terms=60
    
    interest_rate1 = float(request.form['Interest_Number'])
    dti=float(request.form['dti'])
    if ((annual_inc==0 ) or (loan_amnt==0) or (interest_rate1==0)):
        res="Please enter valid data" 
        return render_template("output.html",res=res)

    interest_rate = interest_rate1/1200
    if terms==36:          
        installment = (loan_amnt *interest_rate*((1+interest_rate)**36)) / (((1+interest_rate)**36) - 1)
        term = 0
    else: 
        installment = (loan_amnt *interest_rate*((1+interest_rate)**60)) / (((1+interest_rate)**60) - 1)
        term = 1
            
    final_amount=(installment*terms)-loan_amnt
    #final_amount=int(final_amount)
    #c=np.array([7,45000,17500,17.27,21.31,8747.88,0,1,1,0]).reshape(1,-1)
    #c=np.array([5,30000,12500,17.27,13.16,6248.48,2,1,1,0]).reshape(1,-1)
    
    features=np.array([emp,annual_inc,loan_amnt,interest_rate1,dti,final_amount,home_ownership_cat,term]).reshape(1,-1)
    #features=[7,45000,17500,17.27,21.31,8747.88,0,1,1,0]
    #prediction = model.predict()
    #v=(emp,annual_inc,loan_amnt,interest_rate,dti,final_amount,home_ownership_cat,income,term,interest_payments)
    #bhav=[np.array(list(v))]
    pre = model.predict(features)
    if dti>43:
        res="Dept to income is too high, loan cannot be approved"    
    elif pre == 0:
        res = 'Loan Denied'
    else:
        res = 'Congratulations! Approved!'
    email = request.form['email']
    subject= "Loan status"
    message = Message(subject,sender="predictingloan@gmail.com",recipients=[email])
    
    msg=res
    message.body = msg

    mail.send(message)

    success = "The result of this prediction has been sent to your mail address from predictingloan@gmail.com. "

    return render_template("result.html",success=success)

        
    #return (render_template('result.html',emp=emp,annual_inc=annual_inc,loan_amnt=loan_amnt,interest_rate=interest_rate1,dti=dti,final_amount=final_amount,home_ownership_cat=home_ownership_cat,income=income,term=term,interest_payments=interest_payments))
    #return (render_template('output.html',res=res))
    


if __name__ == "__main__":
    app.run(debug=True)
