from flask import Blueprint, render_template
import flask

user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/signup', methods=['POST'])
def signup():
    data = flask.request.json
    firstname = data['firstname']
    lastname = data['lastname']
    address = data['address']
    city = data['city']
    country = data['city']
    phoneNum = data['phoneNum']
    email = data['email']
    password = data['password']

    # print(data)
    # TODO : provera da li mejl postoji
    # err = {'message' : 'User with that email already exists.'}, 400

    # TODO: dodati korisnika u bazu
    success = {'message' : 'You are successfully registered'}, 200

    return success

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = flask.request.json
    email = data['email']
    password = data['password']

    print(data)
    # TODO: provera da li mejl postoji u bazi 
    # TODO: provera poklapaju li se lozinke
    # TODO: postaviti session za ovog kori8snika

    success = {'message' : 'You are logged in'}, 200

    return success
