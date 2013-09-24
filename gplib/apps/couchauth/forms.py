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

from couchdbkit.ext.django.schema import *
from couchdbkit.ext.django.forms  import DocumentForm
from django.forms import CharField, FileField, ValidationError
from django.forms import PasswordInput, Textarea, Select
from models import User, Group

DOCUMENT_TYPES = ['DNI', 'LE', 'LC']

class UserForm(DocumentForm):
    class Meta:
        document = User
        exclude = ('last_login', 'date_joined', 'groups')

    username = CharField() # required
    password = CharField(widget=PasswordInput(), required=False)
    photo = FileField(required=False)
    comment = CharField(widget=Textarea(attrs={'cols': 20, 'rows': 3}),
        required=False)
    document_type = CharField(widget=Select(choices=map(None, DOCUMENT_TYPES,
        DOCUMENT_TYPES)), required=False)
    tematres_host = CharField(widget=Select(choices=[]), required=False)

    def clean_password(self):
        if self.instance and self.instance._id is None:
            if not self.cleaned_data['password']:
                raise ValidationError("Este campo es obligatorio.")
        return self.cleaned_data['password']

    def clean_username(self):
        self.instance.username = self.cleaned_data['username']
        if not self.instance.check_username():
            raise ValidationError("Este nombre de usuario ya esta en uso")
        return self.cleaned_data['username']

    def clean_email(self):
        self.instance.email = self.cleaned_data['email']
        if not self.instance.check_email():
            raise ValidationError(u"Esta direcci\xf3n de email ya esta en uso")
        return self.cleaned_data['email']

# translations
UserForm.base_fields['first_name'].label = 'Nombre'
UserForm.base_fields['last_name'].label = 'Apellido'
UserForm.base_fields['username'].label = 'Nombre de usuario'
UserForm.base_fields['is_staff'].label = 'Staff?'
UserForm.base_fields['is_superuser'].label = 'Superusuario?'
UserForm.base_fields['is_active'].label = 'Activo?'
UserForm.base_fields['document_type'].label = 'Tipo de documento'
UserForm.base_fields['document_number'].label = u'N\xfamero de documento'
UserForm.base_fields['address'].label = u'Direcci\xf3n'
UserForm.base_fields['phone_number'].label = u'Tel\xe9fono'
UserForm.base_fields['cellphone_number'].label = u'Tel\xe9fono celular'
UserForm.base_fields['photo'].label = 'Foto'
UserForm.base_fields['tematres_host'].label = 'Servidor Tematres'

class GroupForm(DocumentForm):
    class Meta:
        document = Group
        exclude = ('users')


GroupForm.base_fields['name'].label = 'Nombre'
GroupForm.base_fields['max_loan_days'].label = 'Dias de prestamo'
