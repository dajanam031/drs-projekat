from flask import Flask, render_template, request, json, redirect, url_for
import requests

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
            return redirect(url_for('index'))

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
        message = resp['message']
        if req.status_code == 200:
            return redirect(url_for('index'))

        return render_template('index.html', message)

app.run(port=5000, debug=True)