# -*- encoding: utf-8 -*-
__author__ = 'maxim'

from radius import  AuthServer
from pyrad import dictionary
from pyrad import server
from django.core.management.base import BaseCommand, CommandError
from time import sleep


class Command(BaseCommand):

    def handle(self, *args, **options):
        srv = AuthServer(dict = dictionary.Dictionary( "app/radius/dicts/dictionary" ))
        srv.hosts['192.168.39.211'] =  server.RemoteHost('192.168.39.211','hotsp1','hotsp1.it-tim.net')
        srv.hosts['192.168.70.211'] =  server.RemoteHost('192.168.70.211','hotsp2','hotsp2.it-tim.net')
        srv.hosts['10.11.8.30'] =  server.RemoteHost('10.11.8.30','hotsp3','hotsp3.it-tim.net')
        srv.hosts['192.168.33.33'] =  server.RemoteHost('192.168.33.33','thedude','thedude.it-tim.net')
        srv.hosts['192.168.33.152'] =  server.RemoteHost('192.168.33.152','dev','dev.it-tim.net')
        sleep(5)
        srv.BindToAddress('192.168.33.70')
        srv.Run()