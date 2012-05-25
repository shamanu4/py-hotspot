# -*- coding: utf-8 -*-

class MainDBRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'abills':
            return 'abills'
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        if model._meta.app_label == 'abills':
            return False
        return True
