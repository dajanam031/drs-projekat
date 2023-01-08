from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, Float, create_engine
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))# kreirace bazu u folderu database
conn_string = 'sqlite:///' + os.path.join(BASE_DIR, 'crypto.db')
Base = declarative_base()
engine = create_engine(conn_string, echo=True)
Session = sessionmaker()

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer(), primary_key=True)
    cardnumber=Column(String(50), nullable=False, unique=True)
    clientname = Column(String(50), nullable=False)
    expirydate = Column(String(50), nullable=False)
    securitycode = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='card')

class User(Base):
    __tablename__  = 'users'
    id = Column(Integer(), primary_key=True)
    email = Column(String(50), nullable=False, unique=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    phoneNumber = Column(String(50), nullable=False)
    balance =  Column(Float, nullable=False)
    verified = Column(Boolean, default=False)
    card = relationship('Card', back_populates='user')

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_hash = Column(String(100), primary_key=True)
    sender = Column(String(50), nullable=False)
    reciever = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)


     


    
    
    
