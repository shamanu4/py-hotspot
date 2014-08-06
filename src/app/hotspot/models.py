# -*- coding: utf-8 -*-

'''
Created on 20.04.2011
@author: shamanu4.at.gmail.dot.com
'''

from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


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
        from django.db.models import Sum
        from functions import date_formatter        
        used = self.session_set.filter(ap__zone=zone).filter(started__gte=date_formatter()['month']).aggregate(Sum('duration'))
        return used['duration__sum'] or 0
                
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

    def get_pass(self):
        try:
            self.external
        except Exception:
            return self.password
        else:
            return self.external.password

    def check_active(self):
        try:
            self.external
        except Exception:
            return self.active
        else:
            return self.external.enabled and self.external.balance>0

    def check_pass(self,passwrod):
        if self.virtual:
            return True
        return self.get_pass() == passwrod


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
    sid = models.CharField(max_length=20)
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
    
    def hours(self):
        return self.duration/3600


ALLOWED_EXTERNALL_BILL_PROPERTIES = (
        'get_login',
        'get_password',
        'get_balance',
        'get_enabled'
)

class BillExternalType(models.Model):

    type= models.SlugField(max_length=20)
    content_type = models.ForeignKey(ContentType)

    def __unicode__(self):
        if self.valid:
            return self.type
        return u'[invalid] %s' % self.type

    #noinspection PyStatementEffect
    @property
    def valid(self):
        try:
            self.content_type
        except Exception:
            return False
        try:
            self.content_type.model_class().get_login
            self.content_type.model_class().get_password
            self.content_type.model_class().get_balance
            self.content_type.model_class().get_enabled
        except Exception:
            return False
        return True


    def get_property(self,property):
        if not self.valid:
            return '[invalid external billing].%s' % property
        if not property in ALLOWED_EXTERNALL_BILL_PROPERTIES:
            return "%s.[invalid property '%s']" % (self.__unicode__(),property)
        return getattr(self.content_type.model_class(),property)

    def get_login(self):
        return self.get_property('get_login')

    def get_password(self):
        return self.get_property('get_password')

    def get_balance(self):
        return self.get_property('get_balance')

    def get_enabled(self):
        return self.get_property('get_enabled')


class BillExternal(models.Model):

    client = models.OneToOneField(Client,related_name='external')
    billing = models.ForeignKey(BillExternalType)

    @property
    def login(self):
        func = self.billing.get_login()
        return func(self.client)

    @property
    def password(self):
        func = self.billing.get_password()
        return func(self.client)

    @property
    def balance(self):
        func = self.billing.get_balance()
        return func(self.client)

    @property
    def enabled(self):
        func = self.billing.get_enabled()
        return func(self.client)

    def __unicode__(self):
        return self.client.login