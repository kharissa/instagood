from models.base_model import BaseModel
import peewee as pw
import datetime
import os
from peewee_validates import ModelValidator, StringField, validate_email
from flask_login import UserMixin

class User(BaseModel, UserMixin):
    name = pw.CharField()
    email = pw.CharField(unique=True)
    username = pw.CharField(unique=True)
    password = pw.CharField()

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

