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

from datetime import datetime

from couchdbkit import schema
from couchdbkit import Document, DocumentSchema
from couchdbkit.ext.django.loading import get_db
from hashlib import sha1


def encrypt_value(value):
    return sha1(value).hexdigest()


class Group(Document):
    _db = get_db("couchauth")
    name = schema.StringProperty()
    users = schema.ListProperty()
    max_loan_days = schema.IntegerProperty()
    get_id = property(lambda self: self['_id'])

    def add_user(self, user_id):
        if user_id not in self.users:
            self.users.append(user_id)
            self.save()
        return True

    def del_user(self, user_id):
        if user_id in self.users:
            del(self.users[self.users.index(user_id)])
            self.save()
        return True

    def update_users(self, users):
        for user_id in self.users:
            if user_id not in users:
                user = User.get(user_id)
                user.del_group(self._id)
        for user_id in users:
            user = User.get(user_id)
            user.add_group(self._id)

    def id(self):
        return self._id

class Penalty(DocumentSchema):
    """
    A document schema representing a User Penalty
    """

    id = schema.IntegerProperty()
    type = schema.StringProperty(choices=('fault', 'suspend'))
    start = schema.DateProperty()
    end = schema.DateProperty()
    cause = schema.StringProperty()


class User(Document):
    _db = get_db("couchauth")
    get_id = property(lambda self: self['_id'])

    first_name = schema.StringProperty(required=False)
    last_name = schema.StringProperty(required=False)
    email = schema.StringProperty(required=False)

    document_type = schema.StringProperty(required=False)
    document_number = schema.IntegerProperty(required=False)
    address = schema.StringProperty(required=False)
    phone_number = schema.StringProperty(required=False)
    cellphone_number = schema.StringProperty(required=False)
    comment = schema.StringProperty(required=False)

    username = schema.StringProperty()
    password = schema.StringProperty()

    groups = schema.ListProperty()

    is_staff = schema.BooleanProperty()
    is_superuser = schema.BooleanProperty(default=False)
    is_active = schema.BooleanProperty(default=True)

    last_login = schema.DateTimeProperty(required=False)
    date_joined = schema.DateTimeProperty(default=datetime.utcnow)

    penalties = schema.SchemaListProperty(Penalty)

    tematres_host = schema.StringProperty(required=False)

    def del_group(self, group_id):
        group = Group.get(group_id)
        group.del_user(self._id)
        if group_id in self.groups:
            del(self.groups[self.groups.index(group_id)])
            self.save()

    def add_group(self, group_id):
        group = Group.get(group_id)
        group.add_user(self._id)
        if group_id not in self.groups:
            self.groups.append(group_id)
            self.save()

    def update_groups(self, groups):
        for group_id in self.groups:
            if group_id not in groups:
                self.del_group(group_id)
        for group_id in groups:
            self.add_group(group_id)

    def id(self):
        return self._id

    def set_password(self, password_string):
        self.password = encrypt_value(password_string)
        return True

    def check_password(self, password_string):
        if self.password == encrypt_value(password_string):
            return True
        return False

    @classmethod
    def get_user(cls, username, is_active=True):
        param = {"key": username}

        user = cls.view('couchauth/username',
                     include_docs=True, 
                     **param).first()
        if user and user.is_active:
            return user
        return None

    @classmethod
    def get_user_with_groups(cls, username):
        db = cls.get_db()
        rows = list(db.view('couchauth/user_and_groups', include_docs=True,
            startkey=[username, 0], endkey=[username, 1]).all())

        if rows:
            user = cls.wrap(rows[0]['doc'])
            user.group_names = [x['doc']['name'] for x in rows[1:]]
            return user

    @classmethod
    def get_user_by_email(cls, email, is_active=True):
        param = {"key": email}

        user = cls.view('couchauth/get_by_email',
                     include_docs=True, **param).first()
        if user and user.is_active:
            return user
        return None

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return "<User: %s>" %self.username

    def is_anonymous(self):
        return False

    def save(self):
        if not self.check_username():
            raise Exception('This username is already in use.')
        if not self.check_email():
            raise Exception('This email address is already in use.')
        return super(self.__class__, self).save()

    def check_username(self):
        user = User.get_user(self.username, is_active=None)
        if user is None:
            return True
        return user._id == self._id

    def check_email(self):
        if not self.email:
            return True

        user = User.get_user_by_email(self.email, is_active=None)
        if user is None:
            return True

        return user._id == self._id

    def _get_id(self):
        return self.username
    id = property(_get_id)

    def is_authenticated(self):
        return True
