# -*- coding: utf-8 -*-

from pyrad import dictionary, packet, server

class AuthServer(server.Server):
    
    def get_pap_pass(self, pkt): 
        packet_password = packet.AuthPacket(
                            secret = pkt.secret,
                            authenticator = pkt.authenticator
                            ).PwDecrypt( pkt.get('User-Password')[0] )    
        return packet_password          

    
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
        print "username: %s" % username
        print "password: %s" % password
        print
        # @todo: make auth
        reply=self.CreateReplyPacket(pkt)
        if random.random() > 0.5:
            print "Auth OK"
            reply.code=packet.AccessAccept
        else:
            print "Auth FAIL"        
            reply.code=packet.AccessReject        
        reply.AddAttribute('Acct-Interim-Interval',60)
        reply.AddAttribute('Session-Timeout',120)
        reply.AddAttribute('Mikrotik-Rate-Limit','64k/64k 256k/256k 128k/128k 10/10')             
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
        