import os
from app import app
import peewee as pw
from models.user import User
from flask_login import UserMixin
from models.base_model import BaseModel
from playhouse.hybrid import hybrid_property


class Image(BaseModel):
    user = pw.ForeignKeyField(User, backref='users')
    image_path = pw.CharField()
    caption = pw.CharField(null=True)

    @hybrid_property
    def url(self):
        return f'{app.config["S3_LOCATION"]}users/{self.user_id}/images/{self.image_path}'
