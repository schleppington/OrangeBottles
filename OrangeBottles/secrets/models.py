from django.db import models
import os

class Person(models.Model):
    name = models.CharField(max_length=30)
    email  = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=512) 
    salt = models.CharField(max_length=50)   
    def __unicode__(self):
        return self.name
    

class Blackmail(models.Model):
    target = models.ForeignKey(Person, related_name='blackmail_target')
    owner = models.ForeignKey(Person, related_name='blackmail_owner')
    picture = models.ImageField(upload_to="images/")
    deadline = models.DateTimeField()
    timecreated = models.DateTimeField('date published')  
    demandsmet = models.BooleanField(default=False)
    def imgfile(self):
        base, filename = os.path.split(str(self.picture))
        return filename
        
    def __unicode__(self):
        return "Target: " + str(self.target) + " - owner: " + str(self.owner)
    

class Term(models.Model):
    blackmail = models.ForeignKey(Blackmail)
    demand = models.CharField(max_length=400)
    def __unicode__(self):
        return self.demand


class BlackmailFields(models.Model):
    target = models.EmailField(max_length=50, unique=True)
    picture = models.ImageField(upload_to="images/")
    deadline = models.DateTimeField()
    demands = models.CharField(max_length=400)
    def __unicode__(self):
        return "Target: " + str(self.target) + " - owner: " + str(self.owner)
