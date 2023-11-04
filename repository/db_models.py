from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, validates
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, func


import os
from dotenv import load_dotenv
load_dotenv()

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host =  os.getenv("DB_HOST")
db_port =  os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

DATABASE_URL = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

class User(Base):

    __tablename__ = "user"

    uid = Column(String, primary_key=True, index=True)
    wallets = relationship("Wallet", back_populates="user")
    categories = relationship("Category", back_populates="user")
    username = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name =  Column(String)  
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, onupdate=func.now())

class Wallet(Base):

    __tablename__ = 'wallet'

    uid = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('user.uid'))
    user = relationship("User", back_populates="wallets")
    balance = Column(DECIMAL)
    currency = Column(String)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, onupdate=func.now())

class Category(Base):

    __tablename__ = "category"

    uid = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('user.uid'))
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    name = Column(String)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, onupdate=func.now())


class Transaction(Base):

    __tablename__ = "transaction"

    uid = Column(String, primary_key=True, index=True)
    category_id = Column(String, ForeignKey('category.uid'))
    category = relationship("Category", back_populates="transactions")
    description = Column(String)
    amount = Column(DECIMAL)
    type = Column(String)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, onupdate=func.now())

    @validates("amount")
    def validate_amount(self, key, value):
        if value is not None:
            return round(value, 2) # rounding to the same decimal places
        return value