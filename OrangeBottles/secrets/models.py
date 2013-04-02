#must define MEDIA_ROOT for FileField 
# still not sure about which fields should be used...Will look into this tomorrow

from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=30)
    email  = models.EmailField(max_length=30)
    password = models.CharField(max_length=30)    
    def __unicode__(self):
        return self.name
    

class Blackmail(models.Model):
    target = models.ForeignKey(Person, related_name='blackmail_target')
    owner = models.ForeignKey(Person, related_name='blackmail_owner')
    picture = models.ImageField(upload_to="images/")
    demands = models.TextField()
    deadline = models.DateTimeField()
    timecreated = models.DateTimeField('date published')   
    def __unicode__(self):
        return "Target: " + str(self.target) + " - owner: " + str(self.owner)
    

class Term(models.Model):
    blackmail = models.ForeignKey(Blackmail)
    demand = models.CharField(max_length=400)
    def __unicode__(self):
        return self.demand
        
        


