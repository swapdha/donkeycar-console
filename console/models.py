from django.db import models
from datetime import datetime

class remarks(models.Model):
    remark = models.CharField(max_length=500)


class Jobs(models.Model):
    tubs = models.CharField(max_length=200)
    state = models.CharField(max_length=50)
    job_number = models.IntegerField(default=0)
    date = models.DateTimeField(default=datetime.now, blank=True)
    size = models.CharField(max_length=20, default="N/A")
    instance_max = models.IntegerField(default=15)
    request_time = models.IntegerField(default=2)
    request_state = models.CharField(max_length=200, default="Pending")
    availability_zone = models.CharField(max_length=200, default="...")
    tarfile_size = models.CharField(max_length=20, default="N/A")
    log_url = models.CharField(max_length=20, default="N/A")
    commands_log_url = models.CharField(max_length=20, default="N/A")
    duration = models.CharField(max_length=20, default="N/A")
    instance = models.CharField(max_length=200, default="...")
    Comments = models.ManyToManyField(remarks)
    request_id = models.CharField(max_length=200, default="0")
    instance_id = models.CharField(max_length=200, default="0")
    price = models.CharField(max_length=30, default="N/A")

class local_directory(models.Model):
    name = models.CharField(max_length=256)

class credentials(models.Model):
    aws_access_key_id = models.CharField(max_length=256)
    aws_secret_access_key = models.CharField(max_length=256)

class controller(models.Model):
    training = models.CharField(max_length=10,blank=True)



class github(models.Model):
    name = models.CharField(max_length=200, default="https://github.com/wroscoe/donkey")
    extension = models.CharField(max_length=10, blank=True)

