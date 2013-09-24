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
from django.contrib.auth.models import User
import ldap
import logging

from gplib.apps.couchauth.libs import create_couch_user

class LDAPBackend(object):
    """
    Authenticate a user against LDAP.
    Requires python-ldap to be installed.

    Requires the following things to be in settings.py:
    LDAP_DEBUG -- boolean
        Uses logging module for debugging messages.
    LDAP_SERVER_URI -- string, ldap uri.
        default: 'ldap://localhost'
    LDAP_SEARCHDN -- string of the LDAP dn to use for searching
        default: 'dc=localhost'
    LDAP_SCOPE -- one of: ldap.SCOPE_*, used for searching
        see python-ldap docs for the search function
        default = ldap.SCOPE_SUBTREE
    LDAP_SEARCH_FILTER -- formated string, the filter to use for searching for a
        user. Used as: filterstr = LDAP_SEARCH_FILTER % username
        default = 'cn=%s'
    LDAP_UPDATE_FIELDS -- boolean, do we sync the db with ldap on each auth
        default = True

    Required unless LDAP_FULL_NAME is set:
    LDAP_FIRST_NAME -- string, LDAP attribute to get the given name from
    LDAP_LAST_NAME -- string, LDAP attribute to get the last name from

    Optional Settings:
    LDAP_FULL_NAME -- string, LDAP attribute to get name from, splits on ' '
    LDAP_GID -- string, LDAP attribute to get group name/number from
    LDAP_SU_GIDS -- list of strings, group names/numbers that are superusers
    LDAP_STAFF_GIDS -- list of strings, group names/numbers that are staff
    LDAP_EMAIL -- string, LDAP attribute to get email from
    LDAP_DEFAULT_EMAIL_SUFFIX -- string, appened to username if no email found
    LDAP_OPTIONS -- hash, python-ldap global options and their values
    {ldap.OPT_X_TLS_CACERTDIR: '/etc/ldap/ca/'}
    LDAP_ACTIVE_FIELD -- list of strings, LDAP attribute to get active status
        from
    LDAP_ACTIVE -- list of strings, allowed for active from LDAP_ACTIVE_FIELD

    You must pick a method for determining the DN of a user and set the needed
    settings:
        - You can set LDAP_BINDDN and LDAP_BIND_ATTRIBUTE like:
            LDAP_BINDDN = 'ou=people,dc=example,dc=com'
            LDAP_BIND_ATTRIBUTE = 'uid'
          and the user DN would be:
            'uid=%s,ou=people,dc=example,dc=com' % username

        - Look for the DN on the directory, this is what will happen if you do
          not define the LDAP_BINDDN setting. In that case you may need to
          define LDAP_PREBINDDN and LDAP_PREBINDPW if your LDAP server does not
          allow anonymous queries. The search will be performed with the
          LDAP_SEARCH_FILTER setting.

        - Override the _pre_bind() method, which receives the ldap object and
          the username as it's parameters and should return the DN of the user.

    By inheriting this class you can change:
        - How the dn to bind with is produced by overriding _pre_bind()
        - What type of user object to use by overriding: _get_user_by_name(),
          _create_user_object(), and get_user()
    """
    import ldap
    from django.conf import settings
    from django.contrib.auth.models import User



    def __init__(self):
        self.settings = {
              'LDAP_SERVER_URI': 'ldap://localhost',
              'LDAP_SEARCHDN': 'dc=localhost',
              'LDAP_SCOPE': ldap.SCOPE_SUBTREE,
              'LDAP_SEARCH_FILTER': 'cn=%s',
              'LDAP_UPDATE_FIELDS': True,
              'LDAP_PREBINDDN': None,
              'LDAP_PREBINDPW': None,
              'LDAP_BINDDN': None,
              'LDAP_BIND_ATTRIBUTE': None,
              'LDAP_FIRST_NAME': None,
              'LDAP_LAST_NAME': None,
              'LDAP_FULL_NAME': None,
              'LDAP_GID': None,
              'LDAP_SU_GIDS': None,
              'LDAP_STAFF_GIDS': None,
              'LDAP_ACTIVE_FIELD': None,
              'LDAP_ACTIVE': None,
              'LDAP_EMAIL': None,
              'LDAP_DEFAULT_EMAIL_SUFFIX': None,
              'LDAP_OPTIONS': None,
              'LDAP_DEBUG': True,
              }
        # Load settings from settings.py, put them on self.settings
        # overriding the defaults.
        for var in self.settings.iterkeys():
            if hasattr(settings, var):
                self.settings[var] = settings.__getattr__(var)

    def authenticate(self, username=None, password=None):
        # Make sure we have a user and pass
        if not username and password is not None:
            if self.settings['LDAP_DEBUG']:
                assert False
                logging.info('LDAPBackend.authenticate failed: username or password empty: %s %s' % (
                    username, password))
            return None

        if self.settings['LDAP_OPTIONS']:
            for k in self.settings['LDAP_OPTIONS']:
                self.ldap.set_option(k, self.settings.LDAP_OPTIONS[k])

        l = self.ldap.initialize(self.settings['LDAP_SERVER_URI'])

        try:
            bind_string = self._pre_bind(l, username)
        except:
            return None
        if not bind_string:
            if self.settings['LDAP_DEBUG']:
                logging.info('LDAPBackend.authenticate failed: _pre_bind return no bind_string (%s, %s)' % (
                    l, username))
            return None

        try:
            # Try to bind as the provided user. We leave the bind until
            # the end for other ldap.search_s call to work authenticated.
            l.bind_s(bind_string, password)
        except (self.ldap.INVALID_CREDENTIALS,
                self.ldap.UNWILLING_TO_PERFORM), exc:
            # Failed user/pass (or missing password)
            if self.settings['LDAP_DEBUG']:
                logging.info('LDAPBackend.authenticate failed: %s' % exc)
            l.unbind_s()
            return None


        try:
            user = self._get_user_by_name(username)
        except User.DoesNotExist:
            user = self._get_ldap_user(l, username)

        if user is not None:
            if self.settings['LDAP_UPDATE_FIELDS']:
                self._update_user(l, user)

        l.unbind_s()
        if self.settings['LDAP_DEBUG']:
            if user is None:
                logging.info('LDAPBackend.authenticate failed: user is None')
            else:
                logging.info('LDAPBackend.authenticate ok: %s %s' % (user, user.__dict__))

        create_couch_user(username, password)
        return user

    # Functions provided to override to customize to your LDAP configuration.
    def _pre_bind(self, l, username):
        """
        Function that returns the dn to bind against ldap with.
        called as: self._pre_bind(ldapobject, username)
        """
        if not self.settings['LDAP_BINDDN']:
            # When the LDAP_BINDDN setting is blank we try to find the
            # dn binding anonymously or using LDAP_PREBINDDN
            if self.settings['LDAP_PREBINDDN']:
                try:
                    l.simple_bind_s(self.settings['LDAP_PREBINDDN'],
                            self.settings['LDAP_PREBINDPW'])
                except self.ldap.LDAPError, exc:
                    if self.settings['LDAP_DEBUG']:
                        logging.info('LDAPBackend _pre_bind: LDAPError : %s' % exc)
                        logging.info("LDAP_PREBINDDN: "+self.settings['LDAP_PREBINDDN']+" PW "+self.settings['LDAP_PREBINDPW'])
                    return None

            # Now do the actual search
            filter = self.settings['LDAP_SEARCH_FILTER'] % username
            result = l.search_s(self.settings['LDAP_SEARCHDN'],
                        self.settings['LDAP_SCOPE'], filter, attrsonly=1)

            if len(result) != 1:
                if self.settings['LDAP_DEBUG']:
                    logging.info('LDAPBackend _pre_bind: not exactly one result: %s (%s %s %s)' % (
                        result, self.settings['LDAP_SEARCHDN'], self.settings['LDAP_SCOPE'], filter))
                return None
            return result[0][0]
        else:
            # LDAP_BINDDN is set so we use it as a template.
            return "%s=%s,%s" % (self.settings['LDAP_BIND_ATTRIBUTE'], username,
                    self.settings['LDAP_BINDDN'])

    def _get_user_by_name(self, username):
        """
        Returns an object of contrib.auth.models.User that has a matching
        username.
        called as: self._get_user_by_name(username)
        """
        return User.objects.get(username=username)

    def _create_user_object(self, username, password):
        """
        Creates and returns an object of contrib.auth.models.User.
        called as: self._create_user_object(username, password)
        """
        return User(username=username, password=password)

    # Required for an authentication backend
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
    # End of functions to override

    def _get_ldap_user(self, l, username):
        """
        Helper method, makes a user object and call update_user to populate
        """

        # Generate a random password string.
        password = User.objects.make_random_password(10)
        user = self._create_user_object(username, password)
        return user

    def _update_user(self, l, user):
        """
        Helper method, populates a user object with various attributes from
        LDAP.
        """

        username = user.username
        filter = self.settings['LDAP_SEARCH_FILTER'] % username

        # Get results of search and make sure something was found.
        # At this point this shouldn't fail.
        hold = l.search_s(self.settings['LDAP_SEARCHDN'],
                    self.settings['LDAP_SCOPE'], filter)
        if len(hold) < 1:
            raise AssertionError('No results found with: %s' % (filter))

        dn = hold[0][0]
        attrs = hold[0][1]
        firstn = self.settings['LDAP_FIRST_NAME'] or None
        lastn = self.settings['LDAP_LAST_NAME'] or None
        emailf = self.settings['LDAP_EMAIL'] or None

        if firstn:
            if firstn in attrs:
                user.first_name = attrs[firstn][0]
            else:
                raise NameError('Missing attribute: %s in result for %s'
                        % (firstn, dn))
        if lastn:
            if lastn in attrs:
                user.last_name = attrs[lastn][0]
            else:
                raise NameError('Missing attribute: %s in result for %s'
                        % (lastn, dn))
        if not firstn and not lastn and self.settings['LDAP_FULL_NAME']:
            fulln = self.settings['LDAP_FULL_NAME']
            if fulln in attrs:
                    tmp = attrs[fulln][0]
                    user.first_name = tmp.split(' ')[0]
                    user.last_name = ' '.join(tmp.split(' ')[1:])
            else:
                raise NameError('Missing attribute: %s in result for %s'
                        % (fulln, dn))

        if emailf and emailf in attrs:
            user.email = attrs[emailf][0]
        elif self.settings['LDAP_DEFAULT_EMAIL_SUFFIX']:
            user.email = username + self.settings['LDAP_DEFAULT_EMAIL_SUFFIX']


        # Check if we are mapping an ldap id to check if the user is staff or super
        # Other wise the user is created but not give access
        if ('LDAP_GID' in self.settings
                and self.settings['LDAP_GID'] in attrs):
            # Turn off access flags
            user.is_superuser = False
            user.is_staff = False
            check_staff_flag = True
            gids = set(attrs[self.settings['LDAP_GID']])

            # Check to see if we are mapping any super users
            if 'LDAP_SU_GIDS' in self.settings:
                su_gids = set(self.settings['LDAP_SU_GIDS'])
                # If any of the su_gids exist in the gid_data then the user is super
                if (len(gids-su_gids) < len(gids)):
                    user.is_superuser = True
                    user.is_staff = True
                    # No need to check if a staff user
                    check_staff_flag = False

            # Check for staff user?
            if 'LDAP_STAFF_GIDS' in self.settings and check_staff_flag == True:
                # We are checking to see if the user is staff
                staff_gids = set(self.settings['LDAP_STAFF_GIDS'])
                if (len(gids-staff_gids) < len(gids)):
                    user.is_staff = True

        # Check if we need to see if a user is active
        if ('LDAP_ACTIVE_FIELD' in self.settings
            and  self.settings['LDAP_ACTIVE_FIELD']):
            user.is_active = False
            if (self.settings.LDAP_ACTIVE_FIELD in attrs
                and 'LDAP_ACTIVE' in self.settings):
                active_data = set(attrs[self.settings['LDAP_ACTIVE_FIELD']])
                active_flags = set(self.settings.LDAP_ACTIVE)
                # if any of the active flags exist in the active data then
                # the user is active
                if (len(active_data-active_flags) < len(active_data)):
                    user.is_active = True
        else:
            # LDAP_ACTIVE_FIELD not defined, all users are active
            user.is_active = True
        user.save()
