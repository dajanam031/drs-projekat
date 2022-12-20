from flask import Blueprint
import flask
from database.models import User, Session, engine
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
            success = {'message' : 'You are logged in'}, 200
            return success
        else:
            err = {'message' : 'Incorrect password'}, 400 
            return err
    else:
        err = {'message' : 'User with this email does not exists.'}, 400
        return err 
