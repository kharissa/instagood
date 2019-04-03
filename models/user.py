import os
import datetime
from app import app
import peewee as pw
from flask_login import UserMixin
from models.base_model import BaseModel
from playhouse.hybrid import hybrid_property
from peewee_validates import ModelValidator, StringField, validate_email

class User(BaseModel, UserMixin):
    name = pw.CharField()
    email = pw.CharField(unique=True)
    username = pw.CharField(unique=True)
    password = pw.CharField()
    profile_image_path = pw.CharField(null=True)
    is_public = pw.BooleanField(default=True)

    @hybrid_property
    def profile_image_url(self):
        return app.config["S3_LOCATION"] + 'users/' + str(self.id) + '/images/' + self.profile_image_path

    def save(self, *args, **kwargs):
        # Ensure all fields are entered and email is valid
        validator = type(self).CustomValidator(self)
        validator.validate()
        self.errors = validator.errors

        # Ensure unique email and username
        validator = ModelValidator(self)
        validator.validate()
        self.errors.update(validator.errors)
        
        if self.errors:
            return 0
        else:
            self.updated_at = datetime.datetime.now()
            return super(BaseModel, self).save(*args, **kwargs)

    class CustomValidator(ModelValidator):
        name = StringField(required=True)
        email = StringField(required=True, validators=[validate_email()])
        username = StringField(required=True)
        password = StringField(required=True)

    class Meta:
        messages = {
            'name.required': 'Enter your name.',
            'email.required': 'Enter your email address.',
            'username.required': 'Create a username.',
            'password.required': 'Create a password.',
            'email.validators': 'Enter a correct email address.'
        }
