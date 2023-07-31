import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus as urlquote
from dotenv import load_dotenv

load_dotenv()

MYSQL_ADDRESS = os.getenv("MYSQL_ADDRESS")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# url='mysql+mysqlconnector://<username>:%s@<ip>:<port>/<db_name>?charset=utf8'%urlquote(db_passw)
# mysql://dt_admin:dt2016@localhost:3308/dreamteam_db
engine = create_engine(
    f"mysql+pymysql://{MYSQL_USERNAME}:%s@{MYSQL_ADDRESS}/{MYSQL_DATABASE}"
    % urlquote(MYSQL_PASSWORD),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
