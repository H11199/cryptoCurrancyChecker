from json import dumps

from flask import Flask, render_template, request, url_for, session, redirect, flash
from pip._vendor import certifi
from pymongo import MongoClient
import bcrypt
import requests
import os
from flask_mail import Mail, Message
app = Flask(__name__)
client = MongoClient("mongodb+srv://admin-himanshu:test123@cluster0.kzvdw.mongodb.net/CurrencyChecker?retryWrites=true&w=majority",tlsCAFile=certifi.where())
db = client.get_database('CurrencyChecker')

users = db.UserInfo

url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)
createdData = []
print(createdData)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)
@app.route('/',methods=['POST', "GET"])
def register():
    if request.method == 'POST':

        existing_user = users.find_one({'name':request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass, 'email':request.form['email'], 'lastname':request.form['lastname'], 'data':[{'currency':"default", 'current':0, 'status':'none', 'imgLink':'nill'}]})
            session['username'] = request.form['username']
            session['email'] = request.form['email']
            return redirect(url_for('dashboard'))
        else:
            flash("user already exists")

    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login():
    loginUser = users.find_one({"name": request.form['username']})

    if loginUser:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), loginUser["password"]) == loginUser["password"]:
            session['username'] = request.form['username']

            return redirect(url_for('dashboard'))
        return render_template("login.html")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('a',None)
    session.pop('s',None)
    session.pop('filenameSpiral',None)
    session.pop('filenameWave',None)
    return redirect(url_for('register'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    name = session['username']
    myquery = {"name":session["username"]}
    currentUser = list(users.find(myquery))
    print(currentUser)
    currentUserPost = currentUser[0]["data"]
    for i in range(len(currentUser[0]["data"])):
        createdData.append({"currency":currentUserPost[i]["currency"], "current":currentUserPost[i]["current"], 'imageLink':currentUserPost[i]["imgLink"]})
    return render_template("dashboard.html", name=name, createdData=createdData)

@app.route('/dashboard/create', methods=['POST','GET'])
def create():
    if request.method == 'POST':

        current = request.form['current']
        currency = request.form['currency']
        isthere = False
        imgLink = ""
        for i in range(len(response.json())):
            respi = response.json()[i]
            if(respi['name'] == currency):
                isthere = True
                imgLink = respi["image"]
                break

        if isthere:
            filter = {'name': session['username']}
            doc = {'currency':currency, 'current':current, 'status':"created", 'imgLink':imgLink}
            users.update(filter, {"$push":{'data':doc}},)
            return redirect(url_for('dashboard'))
        else:
            flash("Currency name doesn't match")

    return render_template("createPost.html")



if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
