# -*- coding: utf-8 -*-

'''
Created on 20.04.2011
@author: shamanu4.at.gmail.dot.com
'''

from django.db import models
from datetime import datetime, timedelta



class Zone(models.Model):

    name = models.CharField(max_length=40, unique=True)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return self.name



class AccessPoint(models.Model):
    
    ip = models.IPAddressField(unique=True)
    name = models.CharField(max_length=40, unique=True)
    zone = models.ForeignKey(Zone)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return self.name
    


class Group(models.Model):

    name = models.CharField(max_length=40, unique=True)
    time_limit = models.PositiveIntegerField(default=0)     # in hours
    traffic_limit = models.PositiveIntegerField(default=0)  # in megabytes
    speed_limit = models.PositiveIntegerField(default=0)    # in kilobits     
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return self.name


    
class Client(models.Model):
    
    login = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    group = models.ForeignKey(Group)
    registered = models.DateTimeField(blank=True, null=True)
    expire = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
    virtual = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['login']
        
    def __unicode__(self):
        return self.login
    
    @property
    def timelimit(self):
        return self.group.time_limit or 0
    
    @property
    def time_used(self):
        return 0
                
    @property
    def remain(self):
        if not self.timelimit:
            return 0
        else:
            return self.timelimit*3600-self.time_used        
        
    @classmethod
    def get_or_create(cls,login,group):
        from datetime import date
        try:
            client = cls.objects.get(login=login)
        except cls.DoesNotExist:
            client = cls(login=login,group=group,active=True,registered=date.today(),virtual=True)
            client.save()
        return client()
        


class VirtualClient(models.Model):
    
    login = models.CharField(max_length=20, unique=True)
    group = models.ForeignKey(Group)
    
    class Meta:
        ordering = ['login']
        
    def __unicode__(self):
        return self.login
    
    
    
class Session(models.Model):
    
    ap = models.ForeignKey(AccessPoint)
    sid =  models.CharField(max_length=20)
    client = models.ForeignKey(Client)
    framed_ip = models.IPAddressField()
    mac = models.CharField(max_length=18)
    started = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    bytes_in = models.PositiveIntegerField(default=0)
    bytes_out = models.PositiveIntegerField(default=0)
    closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['started']
        
    def __unicode__(self):
        return "%s %s" % (self.ap.name, self.client.login)
    
    @property
    def duration(self):
        return (self.updated - self.started).seconds
    
    @property
    def hours(self):
        return self.duration/3600
    
    
    
    