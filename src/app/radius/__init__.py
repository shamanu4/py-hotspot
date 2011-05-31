# -*- coding: utf-8 -*-

from pyrad import dictionary, packet, server

"""
from radius import  AuthServer
from pyrad import dictionary
from pyrad import server
srv = AuthServer(dict = dictionary.Dictionary( "app/radius/dicts/dictionary" ))
srv.hosts['192.168.39.211'] =  server.RemoteHost('192.168.39.211','hotsp1','hotsp1.it-tim.net')
srv.BindToAddress('192.168.33.152')
srv.Run()
"""
class AuthServer(server.Server):
    
    def get_pap_pass(self, pkt): 
        packet_password = packet.AuthPacket(
                            secret = pkt.secret,
                            authenticator = pkt.authenticator
                            ).PwDecrypt( pkt.get('User-Password')[0] )    
        return packet_password          

    
    def _AuthCheck(self,username,password,mac):
        from hotspot.models import Client, VirtualClient
        try:
            client = Client.objects.get(login=username, password=password, virtual=False, active=True)
        except Client.DoesNotExist:
            try:
                client = VirtualClient.objects.get(login=username)
            except VirtualClient.DoesNotExist:
                client = None
            else:
                client = Client.get_or_create(login="ARP_%s" % mac, group=client.group)
        if client and client.active:
            return (True,client.remain,client.group.speed_limit)
        else:
            return (False,0,0)
                    
    
    def _HandleAuthPacket(self, pkt):
        import random
        server.Server._HandleAuthPacket(self, pkt)

        print "Received an authentication request"
        print "Attributes: "
        for attr in pkt.keys():
            print "%s: %s" % (attr, pkt[attr])
        print
        
        username = pkt.get('User-Name')[0]
        password = self.get_pap_pass(pkt)
        mac = pkt.get('Calling-Station-Id')[0]
        print "username: %s" % username
        print "password: %s" % password
        print "mac: %s" % mac                
        print
        reply=self.CreateReplyPacket(pkt)
        
        auth = self._AuthCheck(username, password, mac)
        if auth[0]:
            print "Auth OK"
            reply.code=packet.AccessAccept
            reply.AddAttribute('Acct-Interim-Interval',60)
            if auth[1]:
                reply.AddAttribute('Session-Timeout',auth[1])
            if auth[2]:
                reply.AddAttribute('Mikrotik-Rate-Limit','%sk/%sk %sk/%sk %sk/%sk 10/10' % (auth[2],auth[2],auth[2]*4,auth[2]*4,auth[2]*2,auth[2]*2))                     
        else:
            print "Auth FAIL"        
            reply.code=packet.AccessReject        
        print "Sending auth reply"
        print "Attributes: "
        for attr in reply.keys():
            print "%s: %s" % (attr, reply[attr])
        print
        self.SendReplyPacket(pkt.fd, reply)
    
    def _HandleAcctPacket(self, pkt):
        server.Server._HandleAcctPacket(self, pkt)

        print "Received an accounting request"
        print "Attributes: "
        for attr in pkt.keys():
            print "%s: %s" % (attr, pkt[attr])
        print
        # @todo: handle session
        reply=self.CreateReplyPacket(pkt)
        self.SendReplyPacket(pkt.fd, reply)
        