import os
import datetime
from app import app
import peewee as pw
from flask import url_for
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
    def followers(self):
        from models.relationship import Relationship
        # Return list of current_user's approved followers
        return User.select().join(Relationship, on=(Relationship.follower_id == User.id)).where(Relationship.following_id == self.id, Relationship.is_approved == True)

    @hybrid_property
    def unapproved_followers(self):
        from models.relationship import Relationship
        # Return list of current_user's unapproved followers
        return User.select().join(Relationship, on=(Relationship.follower_id == User.id)).where(Relationship.following_id == self.id, Relationship.is_approved == False)

    @hybrid_property
    def following(self):
        from models.relationship import Relationship
        # Return list of users that current_user is following (approved)
        return User.select().join(Relationship, on=(Relationship.following_id == User.id)).where(Relationship.follower_id == self.id, Relationship.is_approved == True)

    def is_approved(self, user_id):
        from models.relationship import Relationship
        # Return boolean if relationship between current_user and approved user is approved
        return Relationship.select(Relationship.is_approved).join(User, on=(User.id == Relationship.following_id)).where(Relationship.follower_id == user_id, Relationship.following_id == self.id).first().is_approved

    @hybrid_property
    def has_requests(self):
        from models.relationship import Relationship
        # Returns list of pending follow request for current_user
        return Relationship.select().join(User, on=(User.id == Relationship.following_id)).where(Relationship.is_approved == False, Relationship.following_id == self.id)

    @hybrid_property
    def profile_image_url(self):
        if self.profile_image_path:
            return app.config["S3_LOCATION"] + 'users/' + str(self.id) + '/images/' + self.profile_image_path
        else:
            # Return url to placeholder avatar if no image
            return (url_for('static', filename='images/avatar.png'))

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
