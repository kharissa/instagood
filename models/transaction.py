import os
from app import app
import peewee as pw
from models.user import User
from flask_login import UserMixin
from models.base_model import BaseModel
from models.image import Image
from playhouse.hybrid import hybrid_property


class Transaction(BaseModel):
    user = pw.ForeignKeyField(User, backref='users')
    image = pw.ForeignKeyField(Image, backref='images')
    amount = pw.DecimalField(decimal_places=2)
    braintree_id = pw.CharField()
