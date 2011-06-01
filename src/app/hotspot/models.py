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
    radsecret = models.CharField(max_length=20)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return self.name
    

    
class Client(models.Model):
    
    login = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=20)
    groups = models.ManyToManyField('Group',blank=True, null=True)
    registered = models.DateTimeField(blank=True, null=True)
    expire = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
    virtual = models.BooleanField(default=False)
    vclient = models.ForeignKey('VirtualClient',blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['login']
        
    def __unicode__(self):
        return self.login
    
    def group(self,zone):
        if not self.virtual:
            gr=self.groups.filter(zone=zone)
        else:
            gr=self.vclient.groups.filter(zone=zone)
        if gr.count()>0:
            return gr[0]
        else:
            return False
        
    def time_limit(self,zone):
        if self.group(zone):
            return self.group(zone).time_limit or 0
        else:
            return 0
    
    def speed_limit(self,zone):
        if self.group(zone):
            return self.group(zone).speed_limit or 0
        else:
            return 0
    
    def time_used(self,zone):
        return 0
                
    def remain(self,zone):
        if not self.time_limit(zone):
            return 0
        else:
            return self.time_limit(zone)*3600-self.time_used(zone)        
        
    @classmethod
    def get_or_create(cls,login,vclient):
        try:
            client = cls.objects.get(login=login)
        except cls.DoesNotExist:
            client = cls(login=login,active=True,registered=datetime.now(),virtual=True,vclient=vclient)
            client.save()
        return client
        


class Group(models.Model):

    zone = models.ForeignKey(Zone)
    name = models.CharField(max_length=40, unique=True)
    time_limit = models.PositiveIntegerField(default=0)     # in hours
    traffic_limit = models.PositiveIntegerField(default=0)  # in megabytes
    speed_limit = models.PositiveIntegerField(default=0)    # in kilobits     
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return self.name



class VirtualClient(models.Model):
    
    login = models.CharField(max_length=20, unique=True)
    groups = models.ManyToManyField('Group',blank=True, null=True)
    
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
    duration = models.IntegerField(default=0) 
    bytes_in = models.PositiveIntegerField(default=0)
    bytes_out = models.PositiveIntegerField(default=0)
    closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['started']
        
    def __unicode__(self):
        return "%s %s" % (self.ap.name, self.client.login)
    
    #@property
    #def duration(self):
    #    return (self.updated - self.started).seconds
    
    @property
    def hours(self):
        return self.duration/3600
    
    
    
    