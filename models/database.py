from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import redis
import os

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    # password=os.getenv("REDIS_PASSWORD"),
    db=os.getenv("REDIS_DATABASE"),
    charset="utf-8",
    decode_responses=True,)

engine = create_engine(f'mysql+pymysql://{os.getenv("MYSQL_USER")}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}')
db = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
