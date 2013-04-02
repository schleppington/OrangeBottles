#must define MEDIA_ROOT for FileField 
# still not sure about which fields should be used...Will look into this tomorrow

from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=30)
    email  = models.EmailField(max_length=30)
    password = models.CharField(max_length=30)
    
class Blackmail(models.Model):
    target = Person()
    owner = Person()
    terms = Terms()
    picture = models.Field(upload_to="/usr/OrangeBottles/images/")

class Terms(models.Model):
    blackmail = models.ForeignKey(Blackmail)
    demands = models.TextField()
    deadline = models.DateTimeField()
    timecreated = models.DateTimeField('date published')