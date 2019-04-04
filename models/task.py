import os
import rq
import redis
from app import app
import peewee as pw
from models.base_model import BaseModel
from models.transaction import Transaction
from models.relationship import Relationship


class Task(BaseModel):
    name = pw.CharField()
    description = pw.CharField()
    redis_job_id = pw.CharField()
    transaction = pw.ForeignKeyField(
        Transaction, backref='transactions', null=True)
    relationship = pw.ForeignKeyField(
        Relationship, backref='relationships', null=True)
    complete = pw.BooleanField(default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.redis_job_id, connection=app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
