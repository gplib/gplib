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

from django.core.management.base import BaseCommand
from gplib.apps.couchflow.models import WFItem, Config

class Command(BaseCommand):
    help = 'Update Database Items'

    def handle(self, *args, **options):
        version = Config.get_or_create("version")
        db_version = version.values.get('db', 0)

        if db_version == 0:
            self.update_0()
            self.create_edit_workflows()
            version.values['db'] = 1
            version.save()
            print "Run it again to update to next db version"
        elif db_version == 1:
            self.update_1()
            version.values['db'] = 2
            version.save()
        elif db_version == 2:
            print 'DB already up to date, db version', db_version
        else:
            print 'Invalid Database Version', db_version


    def update_0(self):
        """
        add support to repeteable fields with subfields
        """
        db = WFItem.get_db()

        docs = list(db.view('couchflow/item_names',
                                    include_docs=True).all())
        docs += list(db.view('couchflow/items_cloned',
                                    include_docs=True).all())

        doc_key_values = {'indicator1': '', 'indicator2':'',
                            'subfields':{}, 'exec_value':[]}

        print 'Updating %s items' % len(docs),
        update_docs = []
        for rdoc in docs:
            doc = rdoc['value']
            if 'fields_properties' not in doc:
                print 'have not fields_properties', doc['_id']
                continue

            for _id, prop in doc['fields_properties'].iteritems():
                prop['doc_type'] = 'Fields'
                new_field = {'doc_type': 'Field'}

                for key, value in doc_key_values.iteritems():
                    new_field[key] = prop.get(key, value)
                    if key in prop:
                        del(prop[key])
                prop['list'] = [new_field]
            update_docs.append(doc)

        db.bulk_save(update_docs)
        print '                        [DONE]'
        print 'Successfully Updated db'

    def update_1(self):
        """
        change exec_value of fields that are not list as a list
        """
        db = WFItem.get_db()

        docs = list(db.view('couchflow/items_cloned',
                                    include_docs=True).all())

        print 'Updating %s items' % len(docs),
        invalid = 0
        update_docs = []
        for rdoc in docs:
            doc = rdoc['value']
            if 'fields_properties' not in doc:
                print 'have not fields_properties', doc['_id']
                continue

            for _id, prop in doc['fields_properties'].iteritems():
                for field in prop['list']:
                    if not 'exec_value' in field or not field['exec_value']:
                        field['exec_value'] = []
                        invalid += 1

                    if type(field['exec_value']) is not list:
                        field['exec_value'] = [field['exec_value']]
                        invalid += 1

            update_docs.append(doc)

        db.bulk_save(update_docs)
        print '                        [DONE]'
        print 'updated %s invalid fields' % invalid
        print 'Successfully Updated db'


    def create_edit_workflows(self):
        """
        create edit workflows
        """
        from gplib.apps.couchflow import webconf, models
        print 'Creating new Edition Workflows',
        items = models.WFItem.view("couchflow/item_names",
            include_docs=True).all()
        [webconf.create_default_edit_workflow(x) for x in items]
        print '                        [DONE]'
