# -*- coding: utf-8 -*-
# Este archivo es parte de GPLib - http://gplib.org/
#
# GPlib es software libre desarrollado en la Facultad de Filosofía y Letras de
# la Universidad de Buenos Aires y liberado bajo los términos de la licencia
# GPLIB FILO www.gplib.org/licencia bajo los términos de GPL de  GNU.  Usted
# puede redistribuirlo y/o modificarlo bajo los términos de la licencia GPLIB
# FILO de GNU General  Public License como esta publicado en la Free Software
# Foundation, tanto en la versión 3 de la licencia,  o cualquiera de las
# versiones futuras Gplib es distribuido con el objetivo de que sea útil, pero
# SIN NINGUNA GARANTÍA DE FUNCIONAMIENTO; ni siquiera la garantía implícita de
# que sirva para un propósito particular.  Cuando implemente este sistema
# sugerimos el registro en www.gplib.org/registro, con el fin de fomentar una
# comunidad de usuarios de GPLib.  Ver la GNU General Public License para más
# detalles.http://www.gnu.org/licenses/>
#
#
# Este arquivo é parte do GPLib http://gplib.org/
#
# GPLib é sofware livre desenviolvido na Faculdade de Filosofia e Letras da
# Universidade de Buenos Aires e liberado sob os termos da licença GPLib FILO
# www.gplib.org/licencia/ sob os termos de GPL de GNU.  Você pode redistribuí-lo
# e/ou modificá-lo sob os termos da licença pública geral GNU como publicado na
# Free Software Foundation , tanto na   versão 3 da licença ou  quaisquer
# versões futuras.  GPLib é distribuído com o objetivo de que seja útil, mas SEM
# QUALQUER GARANTIA DE PERFORMANCE; nem a garantia implícita de que servem a uma
# finalidade específica.  Quando  você implementar este sistema sugerimos o
# registro em www.gplib.org/registro/, a fim de promover uma comunidade de
# usuarios do GPLib.  Veja a GNU General Public License para mais detalles.
# http://www.gnu.org/licenses/
#
#
# This file is part of GPLib - http://gplib.org/
#
# GPLib is free software developed by Facultad de Filosofia y Letras Universidad
# de Buenos Aires and distributed under the scope of GPLIB FILO
# www.gplib.org/license and the GPL Public License GNU.  You can redistribute it
# and/or modify it under the terms of the GPLIB FILO GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License,
# or  (at your option) any later version.
#
# GPLib is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  After roll your  own version of GPLIB you may register
# at www.gplib.org/register to buld a comunity of users and developers.  See the
# GNU General Public License for more details.

from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.db import connections, transaction
from gplib.apps.webconf.externaldbs import  get_dbs_dic
import md5


from gplib.apps.couchauth.libs import create_couch_user

class DbBackend(object):
    """
    En settings.py tenes estas variables  para cambiar:
    DATABASE_AUTH_NAME = "login" # base de datos de la  variable DATABASES
    DATABASE_AUTH_QUERY_TABLE = 'users' # tabla a acceder
    DATABASE_AUTH_QUERY_USER = 'name'  # Campo usuario
    DATABASE_AUTH_QUERY_PASSWORD = 'pass' # Campo password
    """


    def authenticate(self, username=None, password=None):
        if password:
            sql_line = "SELECT %s, %s FROM %s WHERE %s='%s'" 
            sql_line = sql_line % ( settings.DATABASE_AUTH_QUERY_USER,
                                    settings.DATABASE_AUTH_QUERY_PASSWORD,
                                    settings.DATABASE_AUTH_QUERY_TABLE,
                                    settings.DATABASE_AUTH_QUERY_USER,
                                    username,)
            settings.DATABASES = get_dbs_dic()
            if 'login' not in settings.DATABASES:
                return None
            cursor = connections[settings.DATABASE_AUTH_NAME].cursor()
            cursor.execute(sql_line)
            row = cursor.fetchone()
            if row:
                db_user, db_pass = row
                pass_hash = md5.new(password)
                pass_hash = pass_hash.hexdigest()
                if pass_hash == db_pass:
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user = User(username=username)
                        user.save()
                    create_couch_user(username, password)
                    return  user
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

