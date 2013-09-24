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

from datetime import datetime, timedelta

from .models import Session, cleanup_sessions
from django_couchdb_utils.test.utils import DbTester


class SessionTests(DbTester):
    def setUp(self):
        super(self.__class__, self).setUp("gplib.apps.couchsessions")

    def test_store_and_retrieve_session(self):

        # couchdbkit doesn't preserve microseconds
        timestamp = datetime.utcnow().replace(microsecond=0)

        data = {
            'session_key': 'dummy',
            'session_data': 'dummy',
            'expire_date': timestamp,
        }
        session = Session(**data)
        session.save()

        session = Session.get_session(data['session_key'])
        self.assertIsNotNone(session)

        for k, v in data.items():
            self.assertEqual(v, getattr(session, k))

    def test_cleanup_sessions(self):
        '''Created two sessions, one current, one outdated. Make sure the stale
        one is removed, the current is kept.'''
        data = {
            'session_key': 'dummy',
            'session_data': 'dummy',
            'expire_date': datetime.utcnow() - timedelta(minutes=1)
        }
        session = Session(**data)
        session.save()

        data2 = data.copy()
        data2.update({
            'session_key': 'dummy2',
            'expire_date': data['expire_date'] + timedelta(minutes=2)
        })
        session2 = Session(**data2)
        session2.save()

        cleanup_sessions()

        session = Session.get_session(data['session_key'])
        self.assertIsNone(session)

        session2 = Session.get_session(data2['session_key'])
        self.assertIsNotNone(session2)


### XXX older doctest code

BASIC_TESTS = r"""

>>> from django.conf import settings
>>> from django_couchdb_utils.sessions.couchdb import SessionStore as CouchDBSession
>>> from django.contrib.sessions.backends.base import SessionBase

>>> session = CouchDBSession()
>>> session.modified
False
>>> session.get('cat')
>>> session['cat'] = "dog"
>>> session.modified
True
>>> session.pop('cat')
'dog'
>>> session.pop('some key', 'does not exist')
'does not exist'
>>> session.save(must_create=True)
>>> session.exists(session.session_key)
True
>>> session.delete(session.session_key)
>>> session.exists(session.session_key)
False

>>> session['foo'] = 'bar'
>>> session.save(must_create=True)
>>> session.exists(session.session_key)
True
>>> prev_key = session.session_key
>>> session.flush()
>>> session.exists(prev_key)
False
>>> session.session_key == prev_key
False
>>> session.modified, session.accessed
(True, True)
>>> session['a'], session['b'] = 'c', 'd'
>>> session.save()
>>> prev_key = session.session_key
>>> prev_data = session.items()
>>> session.cycle_key()
>>> session.session_key == prev_key
False
>>> session.items() == prev_data
True

>>> session = CouchDBSession(session.session_key)
>>> session.save()
>>> CouchDBSession('1').get('cat')

>>> s = SessionBase()
>>> s._session['some key'] = 'exists' # Pre-populate the session with some data
>>> s.accessed = False   # Reset to pretend this wasn't accessed previously

>>> s.accessed, s.modified
(False, False)

>>> s.pop('non existant key', 'does not exist')
'does not exist'
>>> s.accessed, s.modified
(True, False)

>>> s.setdefault('foo', 'bar')
'bar'
>>> s.setdefault('foo', 'baz')
'bar'

>>> s.accessed = False  # Reset the accessed flag

>>> s.pop('some key')
'exists'
>>> s.accessed, s.modified
(True, True)

>>> s.pop('some key', 'does not exist')
'does not exist'


>>> s.get('update key', None)

# test .update()
>>> s.modified = s.accessed = False   # Reset to pretend this wasn't accessed previously
>>> s.update({'update key':1})
>>> s.accessed, s.modified
(True, True)
>>> s.get('update key', None)
1

# test .has_key()
>>> s.modified = s.accessed = False   # Reset to pretend this wasn't accessed previously
>>> s.has_key('update key')
True
>>> s.accessed, s.modified
(True, False)

# test .values()
>>> s = SessionBase()
>>> s.values()
[]
>>> s.accessed
True
>>> s['x'] = 1
>>> s.values()
[1]

# test .iterkeys()
>>> s.accessed = False
>>> i = s.iterkeys()
>>> hasattr(i,'__iter__')
True
>>> s.accessed
True
>>> list(i)
['x']

# test .itervalues()
>>> s.accessed = False
>>> i = s.itervalues()
>>> hasattr(i,'__iter__')
True
>>> s.accessed
True
>>> list(i)
[1]

# test .iteritems()
>>> s.accessed = False
>>> i = s.iteritems()
>>> hasattr(i,'__iter__')
True
>>> s.accessed
True
>>> list(i)
[('x', 1)]

# test .clear()
>>> s.modified = s.accessed = False
>>> s.items()
[('x', 1)]
>>> s.clear()
>>> s.items()
[]
>>> s.accessed, s.modified
(True, True)

#########################
# Custom session expiry #
#########################

>>> from django.conf import settings
>>> from datetime import datetime, timedelta

>>> td10 = timedelta(seconds=10)

# A normal session has a max age equal to settings
>>> s.get_expiry_age() == settings.SESSION_COOKIE_AGE
True

# So does a custom session with an idle expiration time of 0 (but it'll expire
# at browser close)
>>> s.set_expiry(0)
>>> s.get_expiry_age() == settings.SESSION_COOKIE_AGE
True

# Custom session idle expiration time
>>> s.set_expiry(10)
>>> delta = s.get_expiry_date() - datetime.now()
>>> delta.seconds in (9, 10)
True
>>> age = s.get_expiry_age()
>>> age in (9, 10)
True

# Custom session fixed expiry date (timedelta)
>>> s.set_expiry(td10)
>>> delta = s.get_expiry_date() - datetime.now()
>>> delta.seconds in (9, 10)
True
>>> age = s.get_expiry_age()
>>> age in (9, 10)
True

# Custom session fixed expiry date (fixed datetime)
>>> s.set_expiry(datetime.now() + td10)
>>> delta = s.get_expiry_date() - datetime.now()
>>> delta.seconds in (9, 10)
True
>>> age = s.get_expiry_age()
>>> age in (9, 10)
True

# Set back to default session age
>>> s.set_expiry(None)
>>> s.get_expiry_age() == settings.SESSION_COOKIE_AGE
True

# Allow to set back to default session age even if no alternate has been set
>>> s.set_expiry(None)


# We're changing the setting then reverting back to the original setting at the
# end of these tests.
>>> original_expire_at_browser_close = settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Custom session age
>>> s.set_expiry(10)
>>> s.get_expire_at_browser_close()
False

# Custom expire-at-browser-close
>>> s.set_expiry(0)
>>> s.get_expire_at_browser_close()
True

# Default session age
>>> s.set_expiry(None)
>>> s.get_expire_at_browser_close()
False

>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Custom session age
>>> s.set_expiry(10)
>>> s.get_expire_at_browser_close()
False

# Custom expire-at-browser-close
>>> s.set_expiry(0)
>>> s.get_expire_at_browser_close()
True

# Default session age
>>> s.set_expiry(None)
>>> s.get_expire_at_browser_close()
True

>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = original_expire_at_browser_close
"""

__test__ = {
    'BASIC_TESTS': BASIC_TESTS,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()
