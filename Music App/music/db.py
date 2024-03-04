from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base


engine = None   #complex application it is used
base = declarative_base()     #class utility to create a model

db = SQLAlchemy()