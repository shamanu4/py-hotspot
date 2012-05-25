# -*- coding: utf-8 -*-

'''
Created on 23.05.2012
@author: shamanu4.at.gmail.dot.com
'''

from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Bill(models.Model):

    deposit = models.FloatField(default=0)
    uid = models.IntegerField(blank=True,null=True)
    company_id =models.IntegerField(blank=True,null=True)


    def __unicode__(self):
        return "%s" % self.deposit

    class Meta:
        db_table = 'bills'


class Company(models.Model):

    bill = models.ForeignKey(Bill,related_name='companies')
    name = models.CharField(max_length=100,unique=True)
    credit = models.FloatField(default=0)
    credit_date = models.DateField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'companies'
        ordering = ['name']


class AbillsUser(models.Model):

    id = models.IntegerField(primary_key=True,db_column='uid')
    login = models.CharField(max_length=20,unique=True,db_column='id')
    disabled = models.BooleanField(db_column='disable')
    company = models.ForeignKey(Company,related_name='clients')
    bin_password = models.CharField(max_length=20,db_column='password')

    def __unicode__(self):
        return self.login

    @property
    def password(self):
        import settings
        try:
            q = self.__class__.objects.raw("SELECT *, DECODE(password,'%s') AS passw FROM users WHERE uid=%s" % (settings.ABILLS_SECRET_KEY,self.pk))
        except Exception:
            return '[invalid password]'
        else:
            return q[0].passw

    @classmethod
    def get_user(cls,login):
        try:
            u =  cls.objects.get(login=login)
        except cls.DoesNotExist:
            return None
        else:
            return u

    @classmethod
    def get_password(cls,client):

        def func(client):
            user = cls.get_user(client.login)
            if user:
                return user.password
            else:
                return '[no abills user found]'

        return func(client)

    @classmethod
    def get_login(cls,client):

        def func(client):
            user = cls.get_user(client.login)
            if user:
                return user.login
            else:
                return '[no abills user found]'

        return func(client)

    @classmethod
    def get_balance(cls,client):

        def func(client):
            user = cls.get_user(client.login)
            if user:
                try:
                    return user.company.bill.deposit+user.company.credit
                except Exception:
                    return '[abills user has no company]'
            else:
                return '[no abills user found]'

        return func(client)

    @classmethod
    def get_enabled(cls,client):

        def func(client):
            user = cls.get_user(client.login)
            if user:
                return not user.disabled
            else:
                return '[no abills user found]'

        return func(client)

    class Meta:
        db_table = 'users'
        ordering = ['login']
