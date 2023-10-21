from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

import os
from dotenv import load_dotenv

load_dotenv()

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host =  os.getenv("DB_HOST")
db_port =  os.getenv("DB_PORT")

DATABASE_URL = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/mypfinance-backend'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name =  Column(String)  
    age = Column(Integer, nullable=True)