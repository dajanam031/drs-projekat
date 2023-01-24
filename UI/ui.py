from functools import wraps
from flask import Flask, flash, render_template, request, json, redirect, url_for,session
import requests
#import datetime

app = Flask(__name__,template_folder="templates")
app.config['SECRET_KEY'] = '12345'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session['user']['verified']:
            return redirect('/verification')
        return f(*args, **kwargs)
    return decorated_function

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

        if req.status_code == 200:
            session['user']=resp
            return redirect(url_for('index'))
            
        message = resp['message']

        return render_template('signup.html', message=message)

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

        message = resp['message']
        return render_template('login.html', message=message)

@app.route('/profile',methods=['GET','POST'])
@login_required
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
        if req.status_code == 200:
            session['user'] = resp
            return redirect(url_for('index'))

        return render_template('index.html')
    
@app.route('/verification', methods=['GET', 'POST'])
@login_required
def verification():
    if request.method == 'GET':
      return render_template('verification.html')
    else:
        #TODO:
        # izvrsiti provere jel cardNumber u formatu 4242 4242 4242 4242 (nzm mora li)
        # izvrsiti proveru jel securityCode duzine tacno 3 cifre kao i inace kod kartica (isto nzm mora li)
     
        cardnumber=request.form['cardnumber']
        clientname = request.form['clientname']
        #expirydate = datetime.datetime.strptime(expirydate, '%m/%d/%Y')
        #expirydate_iso = expirydate.isoformat()
        expirydate=request.form['expirydate']
        securitycode=request.form['securitycode']

        
        email = session['user']['email']
        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'cardnumber' : cardnumber, 'clientname' : clientname, 'expirydate' : expirydate, 'securitycode' : securitycode,
        'user_email' : email})

        req = requests.post("http://127.0.0.1:5001/engine/verification" , data = data, headers = headers)
        resp = (req.json())
        if req.status_code == 200:
            session['user'] = resp
            return redirect(url_for('index'))
        
        message = resp['message']
        return render_template('verification.html', message=message)

@app.route('/toAnotherUser', methods=['GET', 'POST'])
@login_required
@verified_required
def toAnotherUser():
    if request.method == 'GET':
        return render_template('toAnotherUser.html')
    else:
        reciever_email = request.form['email']
        amount = request.form['amount']
        sender_email = session['user']['email']
        
        if not len(reciever_email.strip()) or not len((str(amount)).strip()):
            flash('Greska! Sva polja moraju biti popunjena')
            return redirect(url_for('toAnotherUser'))
            
        
        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'sender_email' : sender_email, 'reciever_email' : reciever_email, 'amount' : amount})
        req = requests.post("http://127.0.0.1:5001/engine/sendMoneyToAnotherUser", data=data, headers=headers)

        resp = (req.json())
            
        message = resp['message']
        return render_template('toAnotherUser.html', message=message)

@app.route('/balance', methods=['GET'])
@login_required
@verified_required
def balance():
    # da oba korisnika mogu videti azurirano stanje odmah
    email = session['user']['email']

    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    data = json.dumps({'email' : email})
    req = requests.post("http://127.0.0.1:5001/engine/refreshBalance", data=data, headers=headers)

    resp = (req.json())
    session['user'] = resp

    return render_template('balance.html')

@app.route('/toMyAccount', methods=['GET', 'POST'])
@login_required
@verified_required
def toMyAccount():
    if request.method == 'GET':
        email = session['user']['email']

        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'email' : email})
        req = requests.post("http://127.0.0.1:5001/engine/getCard", data=data, headers=headers)
        resp = (req.json())
        cardNum = resp['cardNumber']
        expDate = resp['expiryDate']

        return render_template('toMyAccount.html', cardNum=cardNum, expDate=expDate)
    else:
        amount = request.form['amount']
        email = session['user']['email']
        
        amount_str = str(amount).strip()
        if not len(amount_str): # nista nije uneseno
            flash('Neispravno unet iznos novca. Pokusajte ponovo')
            return redirect(url_for('toMyAccount'))
        
        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'email' : email, 'amount' : amount})
        req = requests.post("http://127.0.0.1:5001/engine/transferMoneyToMyAcc", data=data, headers=headers)

        resp = (req.json())
        mess = resp['message']
        flash(mess)
        return redirect(url_for('toMyAccount'))

@app.route('/thistory', methods=['GET', 'POST'])
@login_required
@verified_required
def transactionsHistory():

        paramsSort = request.args.get('sort_by')
        paramsFilter = request.args
        email = session['user']['email']

        headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({'email' : email, 'paramsSort' : paramsSort, 'paramsFilter' : paramsFilter})
        req = requests.post("http://127.0.0.1:5001/engine/transactionsHistory", data=data, headers=headers)

        transactions = (req.json())

        return render_template('thistory.html', transactions=transactions)
   
@app.route('/transactions')
@login_required
@verified_required
def transactions():
    return render_template('transactions.html') 

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return  redirect(url_for('index'))

app.run(port=5000, debug=True)