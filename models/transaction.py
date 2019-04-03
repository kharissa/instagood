import peewee as pw
from models.user import User
from models.base_model import BaseModel
from models.image import Image

class Transaction(BaseModel):
    user = pw.ForeignKeyField(User, backref='users')
    image = pw.ForeignKeyField(Image, backref='images')
    amount = pw.DecimalField(decimal_places=2)
    braintree_id = pw.CharField()
