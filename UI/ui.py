from flask import Flask, render_template, request, json, redirect, url_for,session
import requests
#import datetime

app = Flask(__name__,template_folder="templates")
app.config['SECRET_KEY'] = '12345'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        city = request.form['city']
        country = request.form['country']
        phoneNum = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'firstname' : firstname, 'lastname' : lastname, 'address' : address, 'city' : city,
        'country' : country, 'phoneNum' : phoneNum,  'email' : email, 'password': password})


        req = requests.post("http://127.0.0.1:5001/engine/signup", data = data, headers = headers)
        resp = (req.json())
        message = resp['message']
        if req.status_code == 200:
            return redirect(url_for('verification'))

        return render_template('index.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']

        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'email' : email, 'password' : password})
        req = requests.post("http://127.0.0.1:5001/engine/login", data=data, headers=headers)

        resp = (req.json())

        
        if req.status_code == 200:
            session['user']=resp
            return redirect(url_for('index'))
        if req.status_code==400:
            message = resp['message']
        return render_template('index.html', message=message)

@app.route('/profile',methods=['GET','POST'])
def profile():
    if request.method=='GET':
        return render_template('profile.html')
    else:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        address = request.form['address']
        city = request.form['city']
        country = request.form['country']
        phoneNum = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'firstname' : firstname, 'lastname' : lastname, 'address' : address, 'city' : city,
        'country' : country, 'phoneNum' : phoneNum,  'email' : email, 'password': password})
        req = requests.post("http://127.0.0.1:5001/engine/profile", data = data, headers = headers)
        resp=(req.json())
        message = resp['message']
        if req.status_code == 200:
            return redirect(url_for('index'))

        return render_template('index.html', message=message)
    
@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'GET':
      return render_template('verification.html')
    else:
        cardnumber=request.form['cardnumber']
        clientname = request.form['clientname']
        #expirydate = datetime.datetime.strptime(expirydate, '%m/%d/%Y')
        #expirydate_iso = expirydate.isoformat()
        expirydate=request.form['expirydate']
        securitycode=request.form['securitycode']

        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'cardnumber' : cardnumber, 'clientname' : clientname, 'expirydate' : expirydate, 'securitycode' : securitycode})

        req = requests.post("http://127.0.0.1:5001/engine/verification" , data = data, headers = headers)
        resp = (req.json())
        message = resp['message']
        if req.status_code == 200:
            return redirect(url_for('index'))

        return render_template('index.html', message=message)

@app.route('/logout')
def logout():
    session.clear()
    return  redirect(url_for('index'))

app.run(port=5000, debug=True)