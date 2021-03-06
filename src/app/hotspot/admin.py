# -*- coding: utf-8 -*-

'''
Created on 20.04.2011
@author: shamanu4.at.gmail.dot.com
'''

from django.contrib import admin
from hotspot.models import Zone, AccessPoint, Group, Client, VirtualClient, Session, BillExternalType, BillExternal

"""
Zone
"""
class ZoneAdmin(admin.ModelAdmin):
    pass
admin.site.register(Zone, ZoneAdmin)

"""
AccessPoint
"""
class AccessPointAdmin(admin.ModelAdmin):
    pass
admin.site.register(AccessPoint, AccessPointAdmin)

"""
Group
"""
class GroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(Group, GroupAdmin)

"""
Client
"""
class ClientAdmin(admin.ModelAdmin):
    pass
admin.site.register(Client, ClientAdmin)

"""
VirtualClient
"""
class VirtualClientAdmin(admin.ModelAdmin):
    pass
admin.site.register(VirtualClient, VirtualClientAdmin)

"""
Session
"""
class SessionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Session, SessionAdmin)

"""
BillExternalType
"""
class BillExternalTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(BillExternalType, BillExternalTypeAdmin)

"""
BillExternal
"""
class BillExternalAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','enabled','login','password','balance')
admin.site.register(BillExternal, BillExternalAdmin)
