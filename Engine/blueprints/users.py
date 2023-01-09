from operator import or_, and_
from flask import Blueprint, jsonify
import flask
from database.models import User, Card, Transaction, Session, engine
from werkzeug.security import check_password_hash, generate_password_hash
import sha3
import random
import threading
import time

user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/signup', methods=['POST'])
def signup():
    data = flask.request.json
    firstname = data['firstname']
    lastname = data['lastname']
    address = data['address']
    city = data['city']
    country = data['country']
    phoneNum = data['phoneNum']
    email = data['email']
    password = data['password']

    localSession = Session(bind=engine)
    
    existing_email = localSession.query(User).filter(User.email == email).first()
    if existing_email:
        err = {'message' : 'User with that email already exists.'}, 400
        return err

    new_user = User(email=email, firstname=firstname, lastname=lastname,
    password=generate_password_hash(password, method='sha256'),
    address=address, city=city, country=country, phoneNumber = phoneNum, balance = 0)

    localSession.add(new_user)
    localSession.commit()

    return updateUserInSession(new_user, localSession)

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = flask.request.json
    email = data['email']
    password = data['password']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email == email).first()
    if user:
        if check_password_hash(user.password, password):
            return updateUserInSession(user, localSession)
        else:
            err = {'message' : 'Incorrect password'}, 400 
            return err
    else:
        err = {'message' : 'User with this email does not exists.'}, 400
        return err 


@user_blueprint.route('/profile',methods=['POST'])
def profile():
    data=flask.request.json
    firstname = data['firstname']
    lastname = data['lastname']
    address = data['address']
    city = data['city']
    country = data['country']
    phoneNum = data['phoneNum']
    Email = data['email']
    password = data['password']

    localSession = Session(bind=engine)

    # TODO:

    # existing_email = localSession.query(User).filter(User.email == Email).first()
    # if existing_email:
    #    err = {'message' : 'User with that email already exists. Try another one!'}, 400
    #    return err

    user_to_update=localSession.query(User).filter(User.email==Email).first()
    user_to_update.firstname=firstname
    user_to_update.lastname=lastname
    user_to_update.address=address
    user_to_update.city=city
    user_to_update.country=country
    user_to_update.phoneNumber=phoneNum
    user_to_update.email=Email
    user_to_update.password=generate_password_hash(password, method='sha256')
    localSession.commit()
  
    return updateUserInSession(user_to_update, localSession) # pamtile su se izmene samo u bazi
    
@user_blueprint.route('/verification', methods=['POST'])
def verification():
    data = flask.request.json
    cardnumber=data['cardnumber']
    clientname = data['clientname']
    expirydate=data['expirydate']
    securitycode=data['securitycode']
    user_email = data['user_email']

    localSession = Session(bind=engine)

    user_to_verify = localSession.query(User).filter(User.email==user_email).first()
    
    existing_cardnumber = localSession.query(Card).filter(Card.cardnumber == cardnumber).first()
    if existing_cardnumber:
        err = {'message' : 'Card with that number already exists.'}, 400
        return err

    user_to_verify.verified = True

    new_card = Card(cardnumber=cardnumber, clientname=clientname, expirydate=expirydate,
    securitycode=securitycode, user_id = user_to_verify.id)

    user_to_verify.balance += 1

    localSession.add(new_card)
    localSession.commit()
    return updateUserInSession(user_to_verify, localSession)

@user_blueprint.route('/sendMoneyToAnotherUser', methods=['POST'])
def sendMoneyToAnotherUser():
    data = flask.request.json
    sender_email = data['sender_email']
    reciever_email = data['reciever_email']
    amount = data['amount']

    thread = threading.Thread(target=transaction_thread, args=(sender_email, reciever_email, amount))
    thread.start()

    message = {'message' : 'Transaction validation has started ....'}, 400
    
    return  message

@user_blueprint.route('/refreshBalance', methods=['POST'])
def refreshBalance():
    data = flask.request.json
    email = data['email']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email==email).first()

    return updateUserInSession(user, localSession)
    
@user_blueprint.route('/transferMoneyToMyAcc', methods=['POST'])
def transferMoneyToMyAcc():
    data = flask.request.json
    email = data['email']
    amount = data['amount']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email==email).first()

    user.balance += float(amount)

    localSession.commit()
    localSession.close()

    success = {'message' : 'Prenos novca je uspesno izvrsen. Novo stanje mozete proveriti u PREGLED STANJA.'}

    return success

@user_blueprint.route('/getCard', methods=['POST'])
def getCard():
    data = flask.request.json
    email = data['email']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email==email).first()
    card = localSession.query(Card).filter(Card.user_id==user.id).first()
    localSession.close()

    resp = {'cardNumber' : card.cardnumber, 'expiryDate' : card.expirydate}

    return resp

@user_blueprint.route('/transactionsHistory', methods=['POST'])
def transactionsHistory():
    data = flask.request.json
    email = data['email']
    paramsSort = data['paramsSort']
    paramsFilter = data['paramsFilter']

    if not paramsSort and not paramsFilter: # bez parametara, samo se vracaju transakcije
        return getTransactions(email)
    elif paramsSort:
        return sortTransactions(email, paramsSort) 
    elif paramsFilter:
        return filterTransactions(paramsFilter, email)
    else:
        resp = []
        return resp


############################################ POMOCNE FUNKCIJE #########################################################

def updateUserInSession(user, session):
    success = {'firstname' : user.firstname,'lastname': user.lastname,'address': user.address,'city':user.city,
        'country':user.country,'phoneNum':user.phoneNumber,'email':user.email,'password':user.password,
        'balance' : user.balance, 'verified' : user.verified}, 200
    session.close()
    return success

def printTransaction(transactions):
    # možda napraviti drugaciji ispis
    resp = []
    for tr in transactions:
        transaction = "SENDER: " + tr.sender + " , " + "RECIEVER: " + tr.reciever + " , " + "AMOUNT: " + str(tr.amount) + "$" + " , " + tr.state
        resp.append(transaction)
    return jsonify(resp)

def getTransactions(email):
    localSession = Session(bind=engine)
    transactions = (
            localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def transaction_thread(sender_email, reciever_email, amount):
    # obrada transakcije, simulirano odredjeno vreme
    
    localSession = Session(bind=engine)

    hashString = (sender_email + reciever_email + str(amount) + str(random.randint(0,1000))).encode('ascii')
    keccak256 = sha3.keccak_256()
    keccak256.update(hashString)

    new_transaction = Transaction(transaction_hash=keccak256.hexdigest(), 
    sender=sender_email, reciever=reciever_email, amount=amount, state="U OBRADI")
    localSession.add(new_transaction) 
    localSession.commit()

    time.sleep(15)
    
    reciever = localSession.query(User).filter(User.email==reciever_email).first()
    sender = localSession.query(User).filter(User.email==sender_email).first()

    if sender_email == reciever_email:
        new_transaction.state = "ODBIJENO"
    elif not reciever:
        new_transaction.state = "ODBIJENO"
    elif reciever.verified == False:
        new_transaction.state = "ODBIJENO"
    elif sender.balance < float(amount):
        new_transaction.state = "ODBIJENO"
    else:
        new_transaction.state = "OBRADJENO"
        reciever.balance += float(amount)
        sender.balance -= float(amount)
    
    localSession.commit()
    localSession.close()


############################################### FUNKCIJE SORTIRANJA ####################################################

def sortTransactions(email, paramsSort):
    if paramsSort == 'amountAsc': 
        return sortbyAmountAsc(email)
    elif paramsSort == 'amountDesc': 
        return sortbyAmountDesc(email)
    elif paramsSort == 'senderAZ':
        return sortbySenderAZ(email)
    elif paramsSort == 'senderZA':
        return sortbySenderZA(email)
    elif paramsSort == 'recieverAZ':
        return sortbyRecieverAZ(email)
    elif paramsSort == 'recieverZA':
        return sortbyRecieverZA(email)

def sortbyAmountAsc(email):
    localSession = Session(bind=engine)
    transactions = (
            localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .order_by(Transaction.amount)
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def sortbyAmountDesc(email):
    localSession = Session(bind=engine)
    transactions = (
            localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .order_by(Transaction.amount.desc())
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def sortbySenderAZ(email):
    localSession = Session(bind=engine)
    transactions = (
            localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .order_by(Transaction.sender)
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def sortbySenderZA(email):
    localSession = Session(bind=engine)
    transactions = (
            localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .order_by(Transaction.sender.desc())
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def sortbyRecieverZA(email):
    localSession = Session(bind=engine)
    transactions = (
            localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .order_by(Transaction.reciever.desc())
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def sortbyRecieverAZ(email):
    localSession = Session(bind=engine)
    transactions = (
            localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .order_by(Transaction.reciever)
            .all()
        )
    localSession.close()
    return printTransaction(transactions)


######################################################################################################################

#################################### FUNKCIJE FILTRIRANJA ############################################################

def filterTransactions(paramsFilter, email):
    amountFilter = paramsFilter['amount'].strip()
    senderFilter = paramsFilter['sender'].strip()
    recieverFilter = paramsFilter['reciever'].strip()

    if len(amountFilter) and len(senderFilter) and len(recieverFilter):
        return filterByAllParams(senderFilter, recieverFilter, amountFilter, email)
    
    elif len(amountFilter) and len(senderFilter) and not len(recieverFilter):
        return filterByAmountAndSender(amountFilter, senderFilter, email)
    
    elif len(amountFilter) and not len(senderFilter) and len(recieverFilter):
        return filterByAmountAndReciever(amountFilter, recieverFilter, email)
        
    elif not len(amountFilter) and len(senderFilter) and len(recieverFilter):
        return filterBySenderAndReciever(senderFilter, recieverFilter, email)
        
    elif len(amountFilter) and not len(senderFilter) and not len(recieverFilter):
        return filterByAmount(amountFilter, email)
        
    elif not len(amountFilter) and len(senderFilter) and not len(recieverFilter):
        return filterBySender(senderFilter, email)
        
    elif not len(amountFilter) and not len(senderFilter) and len(recieverFilter):
        return filterByReciever(recieverFilter, email)
    else:
        return getTransactions(email)
        

def filterByAllParams(senderFilter, recieverFilter, amountFilter, email):
    # filtriranje po svim parametrima
    localSession = Session(bind=engine)
    transactions = (
        localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .filter(Transaction.sender.like(f'%{senderFilter}%'), Transaction.reciever.like(f'%{recieverFilter}%'), Transaction.amount == amountFilter)
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def filterByAmountAndSender(amountFilter, senderFilter, email):
    # filtriranje po kolicini novca i posiljaocu
    localSession = Session(bind=engine)
    transactions = (
        localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .filter(Transaction.sender.like(f'%{senderFilter}%'), Transaction.amount == amountFilter)
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def filterByAmountAndReciever(amountFilter, recieverFilter, email):
    # filtriranje po kolicini novca i primaocu
    localSession = Session(bind=engine)
    transactions = (
        localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .filter(Transaction.reciever.like(f'%{recieverFilter}%'), Transaction.amount == amountFilter)
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def filterBySenderAndReciever(senderFilter, recieverFilter, email):
    # filtriranje po primaocu i posiljaocu
    localSession = Session(bind=engine)
    transactions = (
        localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .filter(Transaction.sender.like(f'%{senderFilter}%'), Transaction.reciever.like(f'%{recieverFilter}%'))
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def filterByAmount(amountFilter, email):
    # filtriranje samo po kolicini novca
    localSession = Session(bind=engine)
    transactions = (
        localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .filter(Transaction.amount == amountFilter)
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def filterBySender(senderFilter, email):
    # filtriranje po posiljaocu
    localSession = Session(bind=engine)
    transactions = (
        localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .filter(Transaction.sender.like(f'%{senderFilter}%'))
            .all()
        )
    localSession.close()
    return printTransaction(transactions)

def filterByReciever(recieverFilter, email):
    # filtriranje po primaocu
    localSession = Session(bind=engine)
    transactions = (
        localSession.query(Transaction)
            .filter(or_(Transaction.sender == email, Transaction.reciever == email))
            .filter(Transaction.reciever.like(f'%{recieverFilter}%'))
            .all()
        )
    localSession.close()
    return printTransaction(transactions)
######################################################################################################################
    




