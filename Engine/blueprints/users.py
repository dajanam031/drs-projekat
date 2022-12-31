from flask import Blueprint
import flask
from database.models import User,Card, Session, engine
from werkzeug.security import check_password_hash, generate_password_hash

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
    address=address, city=city, country=country, phoneNumber = phoneNum)

    localSession.add(new_user)
    localSession.commit()

    # # provera 
    # users = localSession.query(User).all()
    # for user in users:
    #     print(user.email)

    success = {'message' : 'You are successfully registered'}, 200

    return success

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = flask.request.json
    email = data['email']
    password = data['password']

    localSession = Session(bind=engine)
    user = localSession.query(User).filter(User.email == email).first()
    if user:
        if check_password_hash(user.password, password):
        # TODO: postaviti session za ovog kori8snika
            success = {'firstname' : user.firstname,'lastname': user.lastname,'address': user.address,'city':user.city,
            'country':user.country,'phoneNum':user.phoneNumber,'email':user.email,'password':user.password}, 200
            return success
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

   # existing_email = localSession.query(User).filter(User.email == Email).first()
    #if existing_email:
     #   err = {'message' : 'User with that email already exists.'}, 400
     #   return err

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
  
    success = {'message' : 'You successfully edited your profile'}, 200

    return success
    
@user_blueprint.route('/verification', methods=['POST'])
def verification():
    data = flask.request.json
    cardnumber=data['cardnumber']
    clientname = data['clientname']
    expirydate=data['expirydate']
    securitycode=data['securitycode']

    localSession = Session(bind=engine)
  
    existing_cardnumber = localSession.query(Card).filter(Card.cardnumber == cardnumber).first()
    if existing_cardnumber:
        err = {'message' : 'Card with that number already exists.'}, 400
        return err

    new_card = Card(cardnumber=cardnumber, clientname=clientname, expirydate=expirydate,
    securitycode=securitycode)

    localSession.add(new_card)
    localSession.commit()
    
    success = {'message' : 'You are successfully verificated'}, 200
    return success
    




