from flask import Blueprint
import flask
from database.models import User,Card, Session, engine
from werkzeug.security import check_password_hash, generate_password_hash
from web3.auto import w3
import random
import json

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

    return updateUserInSession(new_user)

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = flask.request.json
    email = data['email']
    password = data['password']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email == email).first()
    if user:
        if check_password_hash(user.password, password):
            return updateUserInSession(user)
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
  
    return updateUserInSession(user_to_update) # pamtile su se izmene samo u bazi
    
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
    return updateUserInSession(user_to_verify)

@user_blueprint.route('/sendMoneyToAnotherUser', methods=['POST'])
def sendMoneyToAnotherUser():
    data = flask.request.json
    sender_email = data['sender_email']
    reciever_email = data['reciever_email']
    amount = data['amount']

    localSession = Session(bind=engine)

    reciever = localSession.query(User).filter(User.email==reciever_email).first()
    sender = localSession.query(User).filter(User.email==sender_email).first()

    if sender_email == reciever_email:
        err = {'message' : 'Nedozvoljeno iniciranje transakcije samom sebi.'}, 400
        return err
    elif not reciever:
        err = {'message' : 'Korisnik sa unetim emailom ne postoji. Pokusajte ponovo.'}, 400
        return err
    elif reciever.verified == False:
        err = {'message' : 'Korisnik sa unetim emailom nema otvoren crypto racun. Transakcija otkazana.'}, 400
        return err
    elif sender.balance < float(amount):
        err = {'message' : 'Nemate dovoljno sredstava. Transakcija otkazana.'}, 400
        return err
    else:

        # TODO: zapamtiti transakciju u bazi, treba da sadrzi hash string (keccak256 fja) u kom se nalaze
        # sender, reciever, iznos, random int

        # transaction = {'sender' : sender_email, 'reciever' : reciever_email,
        #                 'amount' : amount, 'randint' : random.randint(1, 10000)}
        # json_string = json.dumps(transaction)

        # hash = w3.keccak(text=json_string)
        
        reciever.balance += float(amount)
        sender.balance -= float(amount)
        
        localSession.commit()

        return updateUserInSession(sender)

@user_blueprint.route('/refreshBalance', methods=['POST'])
def refreshBalance():
    data = flask.request.json
    email = data['email']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email==email).first()

    return updateUserInSession(user)
    
@user_blueprint.route('/transferMoneyToMyAcc', methods=['POST'])
def transferMoneyToMyAcc():
    data = flask.request.json
    email = data['email']
    amount = data['amount']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email==email).first()

    user.balance += float(amount)

    localSession.commit()

    success = {'message' : 'Prenos novca je uspesno izvrsen. Novo stanje mozete proveriti u PREGLED STANJA.'}

    return success

@user_blueprint.route('/getCard', methods=['POST'])
def getCard():
    data = flask.request.json
    email = data['email']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email==email).first()
    card = localSession.query(Card).filter(Card.user_id==user.id).first()

    resp = {'cardNumber' : card.cardnumber, 'expiryDate' : card.expirydate}

    return resp

################## POMOCNE FUNKCIJE #####################

def updateUserInSession(user):
    success = {'firstname' : user.firstname,'lastname': user.lastname,'address': user.address,'city':user.city,
        'country':user.country,'phoneNum':user.phoneNumber,'email':user.email,'password':user.password,
        'balance' : user.balance, 'verified' : user.verified}, 200
    return success
    




