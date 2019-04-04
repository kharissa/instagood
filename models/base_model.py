import datetime
import peewee as pw
from database import db
from peewee_validates import ModelValidator

class BaseModel(pw.Model):
    created_at = pw.DateTimeField(default=datetime.datetime.now)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        validator = type(self).CustomValidator(self)
        validator.validate()

        self.errors = validator.errors

        if self.errors:
            return 0
        else:
            self.updated_at = datetime.datetime.now()
            return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = db
        legacy_table_names = False

    class CustomValidator(ModelValidator):
        pass
