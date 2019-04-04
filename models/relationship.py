import peewee as pw
from models.user import User
from models.base_model import BaseModel


class Relationship(BaseModel):
    follower = pw.ForeignKeyField(User, backref='_followers')
    following = pw.ForeignKeyField(User, backref='_followings')
    is_approved = pw.BooleanField(default="False")



