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

import urllib

try:
    import simplejson as json
except ImportError:
    import json


class Note(object):
    def __init__(self, note_id, note_type, note_lang, note_text):
        self.id = note_id
        self.type = note_type
        self.lang = note_lang
        self.text = note_text

    def __repr__(self):
        return "<Note id:%s lang:%s>" % (self.id, self.lang)

class Term(object):
    def __init__(self, service, term_id, string, no_term_string=None, 
            index=None, order=None, relation_type_id=None):
        self.id = term_id
        self.service = service
        self.string = string
        self.index = index
        self.order = order
        self.no_term_string = no_term_string
        self.relation_type_id = relation_type_id

        self._notes = []

    @property
    def notes(self):
        if not self._notes:
            data = self.service.open("fetchNotes", self.id)
            if not data:
                return []
            for note in data["result"].values():
                # don't need string, we are calling from the term
                del(note["string"])
                del(note["term_id"])
                self._notes.append(Note(**note))

        return self._notes

    def fetch(self, what):
        try:
            data = self.service.open(what, self.id)
        except Exception, error:
            print error
            data = None

        if not data:
            return []
        return self.service.get_results(data)

    def down(self):
        return self.fetch("fetchDown")

    def up(self):
        return self.fetch("fetchUp")

    def alt(self):
        return self.fetch("fetchAlt")

    def related(self):
        return self.fetch("fetchRelated")

    def similar(self):
        return self.service.similar(self.string)

    def __repr__(self):
        return "<Term id:%s string:%s>" % (self.id, repr(self.string))


class Info(object):
    """
    Info about the service
    """
    def __init__(self, service):
        result_keys = ('author', 'keywords', 'lang', 'scope', 'title', 'uri')
        resume_keys = ('status', 'version', 'web_service_version')

        self.error = None

        try:
            data = service.open("fetchVocabularyData")
        except Exception, error:
            self.status = "unavailable"
            self.error = error
            return

        for key in resume_keys:
            setattr(self, key, data['resume'].get(key, None))

        for key in result_keys:
            setattr(self, key, data['result'].get(key, None))

    def __repr__(self):
        return "<Info status:%s>" % self.status


class Service(object):
    """
    This class represent the webservice
    usefull methods are: search, similar, info
    """

    def __init__(self, host):
        self.host = host

    def open(self, task, arg=None):
        """
        Execute a task with an optional argument
        """
        url = self.host + 'services.php?task=%s&output=json' % task
        if arg:
            url += '&arg=%s' % arg
        data = urllib.urlopen(url).read()
        # Damn, if it's an error
        # returns xml =/
        if '<error>' in data:
            return None
        data = json.loads(data)
        if data["resume"]["cant_result"] == 0:
            return None
        return data

    def fetch(self, _type, word):
        data = self.open(_type, word)
        if not data:
            return []
        return self.get_results(data)

    def search(self, word):
        word = urllib.quote(word.encode("utf8", "replace"))
        return self.fetch("search", word)

    def similar(self, word):
        word = urllib.quote(word.encode("utf8", "replace"))
        try:
            data = self.open("fetchSimilar", word)["result"]["string"]
        except Exception:
            return None
        return data

    def get_results(self, data):
        results = []
        for result in data["result"].values():
            result.update({"service":self})
            results.append(Term(**result))
        return results

    def info(self):
        """
        Return the service information
        """
        return Info(self)


if __name__ == '__main__':
    service = Service("http://tematres.filo.uba.ar/vocab/")
    info = service.info()
    print info
    print "[similar perros]",  service.similar("perros")
    print "[search per]"
    for term in service.search("per"):
        print "term:", term.string
        print "related:", " :: ".join([t.string for t in term.related()])
