# -*- coding: utf-8 -*-

from pyrad import dictionary, packet, server

"""
from radius import  AuthServer
from pyrad import dictionary
from pyrad import server
srv = AuthServer(dict = dictionary.Dictionary( "app/radius/dicts/dictionary" ))
srv.hosts['192.168.39.211'] =  server.RemoteHost('192.168.39.211','hotsp1','hotsp1.it-tim.net')
srv.hosts['192.168.39.212'] =  server.RemoteHost('192.168.39.212','hotsp2','hotsp2.it-tim.net')
srv.hosts['192.168.39.213'] =  server.RemoteHost('192.168.39.212','hotsp3','hotsp3.it-tim.net')
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

    
    def _SessionStart(self, ap, client, mac, sid, framed_ip):
        from hotspot.models import Session
        session = Session(ap=ap, client=client, mac=mac, sid=sid, framed_ip=framed_ip)
        session.save()
    
    
    def _AuthCheck(self, point_ip, username, password, mac, sid, framed_ip):
        from hotspot.models import Client, VirtualClient, AccessPoint
        try:
            ap = AccessPoint.objects.get(ip=point_ip)            
        except AccessPoint.DoesNotExist:
            return (False,0,0)
        try:
            client = Client.objects.get(login=username, password=password, virtual=False, active=True)
        except Client.DoesNotExist:
            try:
                vclient = VirtualClient.objects.get(login=username)
            except VirtualClient.DoesNotExist:
                client = None
            else:
                client = Client.get_or_create(login="ARP_%s" % mac, vclient=vclient)
        if client and client.active and client.group(ap.zone) and client.remain(ap.zone)>0:
            self._SessionStart(ap, client, mac, sid, framed_ip)
            return (True,client.remain(ap.zone),client.speed_limit(ap.zone))
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
        point_ip = pkt.get('NAS-IP-Address')[0]
        sid = pkt.get('Acct-Session-Id')[0]
        framed_ip = pkt.get('Framed-IP-Address')[0]
        print "username: %s" % username
        print "password: %s" % password
        print "mac: %s" % mac
        print "sid: %s" % sid
        print "framed_ip: %s" % framed_ip                 
        print
        reply=self.CreateReplyPacket(pkt)        
        auth = self._AuthCheck(point_ip, username, password, mac, sid, framed_ip)
        if auth[0]:
            print "Auth OK"
            reply.code=packet.AccessAccept
            reply.AddAttribute('Acct-Interim-Interval',60)
            if auth[1]:
                reply.AddAttribute('Session-Timeout',auth[1])
            if auth[2]:
                reply.AddAttribute('Mikrotik-Rate-Limit','%sk/%sk' % (auth[2],auth[2]))                   
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
        
        point_ip = pkt.get('NAS-IP-Address')[0]
        sid = (pkt.get('Acct-Session-Id') or [''])[0]        
        bytes_in = (pkt.get('Acct-Input-Octets') or [0])[0]
        bytes_out = (pkt.get('Acct-Input-Octets') or [0])[0]
        duration = (pkt.get('Acct-Session-Time') or [0])[0]
        status = pkt.get('Acct-Status-Type')[0]
        
        print "IN: %s" % bytes_in
        print "OUT: %s" % bytes_out
        print "DURATION: %s" % duration
        print 
        
        from hotspot.models import Session,AccessPoint
        try:
            ap = AccessPoint.objects.get(ip=point_ip)            
        except AccessPoint.DoesNotExist:
            pass
        else:
            try: 
                session = Session.objects.get(ap=ap,sid=sid,closed=False)
            except Session.DoesNotExist:
                pass
            else:
                session.bytes_in=bytes_in
                session.bytes_out=bytes_out
                session.duration=duration
                if status=='Stop':
                    session.closed=True
                session.save()
        
        reply=self.CreateReplyPacket(pkt)
        self.SendReplyPacket(pkt.fd, reply)
        