import peewee as pw
from models.base_model import BaseModel
from models.user import User


class Relationship(BaseModel):
    follower = pw.ForeignKeyField(User, backref='followers')
    following = pw.ForeignKeyField(User, backref='followings')
    is_approved = pw.BooleanField(default="False")

