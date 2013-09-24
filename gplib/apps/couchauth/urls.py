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

couchauth_webconf = patterns('',
                       (r'^couchauth/$', 'gplib.apps.couchauth.webconf.index'),
                       (r'^couchauth/show_users/$', 'gplib.apps.couchauth.webconf.show_users'),
                       (r'^couchauth/edit_user/(?P<user_id>\w+)/$', 'gplib.apps.couchauth.webconf.edit_or_create_user'),
                       (r'^couchauth/new_user/$', 'gplib.apps.couchauth.webconf.edit_or_create_user'),
                       (r'^couchauth/show_groups/$', 'gplib.apps.couchauth.webconf.show_groups'),
                       (r'^couchauth/show_group/(?P<group_id>\w+)/$', 'gplib.apps.couchauth.webconf.show_group'),
                       (r'^couchauth/save_group/(?P<group_id>\w+)/$', 'gplib.apps.couchauth.webconf.save_group'),
                       (r'^couchauth/save_user/(?P<user_id>\w+)$', 'gplib.apps.couchauth.webconf.save_user'),
                       (r'^couchauth/delete_user/(?P<user_id>\w+)$', 'gplib.apps.couchauth.webconf.delete_user'),
                       (r'^couchauth/save_user/$', 'gplib.apps.couchauth.webconf.save_user'),
                       (r'^couchauth/save_users/$', 'gplib.apps.couchauth.webconf.save_users'),
                       (r'^couchauth/save_new_group/$', 'gplib.apps.couchauth.webconf.save_new_group'),
                       (r'^couchauth/new_group/$', 'gplib.apps.couchauth.webconf.new_group'),
                             )
