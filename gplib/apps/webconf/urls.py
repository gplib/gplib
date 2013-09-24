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

from django.conf.urls.defaults import *
from gplib.apps.couchflow.urls import couchflow_webconf
from gplib.apps.couchauth.urls import couchauth_webconf


urlpatterns = patterns('',
                       (r'^$', 'gplib.apps.webconf.views.index'),
                       (r'^greenstone/?$', 'gplib.apps.webconf.views.greenstone'),
                       (r'^greenstone/edit?$', 'gplib.apps.webconf.views.greenstone_edit'),
                       (r'^greenstone/test?$', 'gplib.apps.webconf.views.greenstone_test'),
                       # En externaldbs.py
                       (r'externaldbs/$', 'gplib.apps.externaldbs.webconf.index'),
                       (r'externaldbs/show_extra_dbs/$', 'gplib.apps.externaldbs.webconf.show_extra_dbs'),
                       (r'externaldbs/show_extra_queries/$', 'gplib.apps.externaldbs.webconf.show_extra_queries'),
                       (r'externaldbs/create_extra_db/$', 'gplib.apps.externaldbs.webconf.create_extra_db'),
                       (r'externaldbs/create_extra_query/$', 'gplib.apps.externaldbs.webconf.create_extra_query'),
                       (r'externaldbs/edit_extra_db/(?P<db_id>\d+)/$', 'gplib.apps.externaldbs.webconf.edit_extra_db'),
                       (r'externaldbs/edit_extra_query/(?P<query_id>\d+)/$', 'gplib.apps.externaldbs.webconf.edit_extra_query'),
                       (r'externaldbs/drop_extra_query/(?P<query_id>\d+)/$', 'gplib.apps.externaldbs.webconf.drop_extra_query'),
                       (r'externaldbs/drop_extra_db/(?P<db_id>\d+)/$', 'gplib.apps.externaldbs.webconf.drop_extra_db'),
                       (r'externaldbs/post_extra_db/(?P<db_id>\d+)/$', 'gplib.apps.externaldbs.webconf.save_extra_db'),
                       (r'externaldbs/post_extra_db/$', 'gplib.apps.externaldbs.webconf.new_extra_db'),
                       (r'externaldbs/post_extra_query/(?P<query_id>\d+)/$', 'gplib.apps.externaldbs.webconf.save_extra_query'),
                       (r'externaldbs/post_extra_query/$', 'gplib.apps.externaldbs.webconf.new_extra_query'),
                       (r'externaldbs/show_extra_query/(?P<query_id>\d+)/$', 'gplib.apps.externaldbs.webconf.show_extra_query'),

                       # En aclsmanager.py
                       (r'^aclsmanager/$', 'gplib.apps.webconf.aclsmanager.index'),
                       (r'^aclsmanager/show_users/$', 'gplib.apps.webconf.aclsmanager.show_users'),
                       (r'^aclsmanager/show_user/(?P<user_id>\d+)/$', 'gplib.apps.webconf.aclsmanager.show_user'),
                       (r'^aclsmanager/show_groups/$', 'gplib.apps.webconf.aclsmanager.show_groups'),
                       (r'^aclsmanager/show_group/(?P<group_id>\d+)/$', 'gplib.apps.webconf.aclsmanager.show_group'),
                       (r'^aclsmanager/save_group/(?P<group_id>\d+)/$', 'gplib.apps.webconf.aclsmanager.save_group'),
                       (r'^aclsmanager/save_user/(?P<user_id>\d+)/$', 'gplib.apps.webconf.aclsmanager.save_user'),
                       (r'^aclsmanager/save_new_group/$', 'gplib.apps.webconf.aclsmanager.save_new_group'),
                       (r'^aclsmanager/new_group/$', 'gplib.apps.webconf.aclsmanager.new_group'),

                       # En couchauth.py
)

urlpatterns += couchflow_webconf
urlpatterns += couchauth_webconf
