import os
from app import app
import peewee as pw
from models.base_model import BaseModel
from models.transaction import Transaction
import redis
import rq
from database import db


class Task(BaseModel):
    name = pw.CharField()
    description = pw.CharField()
    redis_job_id = pw.CharField()
    transaction = pw.ForeignKeyField(Transaction, backref='transactions')
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