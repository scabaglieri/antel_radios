import sqlalchemy as db
import pymysql

engine = db.create_engine("mysql+pymysql://externo:Db-flask@localhost:3306/test_db")

conn = engine.connect() 
