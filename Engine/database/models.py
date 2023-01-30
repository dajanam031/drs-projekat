from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Boolean, Column, String, Integer, Float, create_engine
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))# kreirace bazu u folderu database
conn_string = 'sqlite:///' + os.path.join(BASE_DIR, 'crypto.db')
Base = declarative_base()
engine = create_engine(conn_string, echo=True)
Session = sessionmaker()


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
    balance_btc= Column(Float,default=0)
    balance_ltc=Column(Float,default=0)
    balance_doge=Column(Float,default=0)
    balance_eth=Column(Float,default=0)
    verified = Column(Boolean, default=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_hash = Column(String(100), primary_key=True)
    sender = Column(String(50), nullable=False)
    reciever = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default = "dollar")
    state = Column(String(50), nullable=False)


     


    
    
    
