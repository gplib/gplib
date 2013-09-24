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

import sys
from django.core.management.base import BaseCommand

from optparse import make_option

from gplib import settings
from couchdbkit.client import Server
from couchdbkit.ext.django.loading import get_db

class Command(BaseCommand):
    help = 'Replicate parts or all the database'

    option_list = BaseCommand.option_list + (
        make_option('--server',
            default=None,
            help='Server to connect to, defaults to the couchflow one'),
        make_option('--couchflow',
            action='store_true',
            default=False,
            help='Include couchflow documents only in this pass'),
        make_option('--no-couchflow',
            action='store_true',
            default=False,
            help='Include non-couchflow documents only in this pass'),
        make_option('--no-clones',
            action='store_true',
            default=False,
            help='Filter out clones from this pass'),
        make_option('--create-target',
            action='store_true',
            default=False,
            help='Create target database if it doesn\'t exist yet'),
    )

    def handle(self, *args, **options):
        if len(args) != 2:
            print "Usage: split_dbs [params] source target"
            return False

        if options['server']:
            server = Server(options['server'])
            print "Using user specified server"
        else:
            server = get_db("couchflow").server
            print "Using default couchflow server (override with --server)"
        print "Server uri:", server.uri

        params = {}
        qparams = {}

        if options['couchflow']:
            print "Couchflow pass"
            qparams['couchflow'] = '1'
        if options['no_couchflow']:
            print "No couchflow pass"
            qparams['couchflow'] = '0'
        if options['no_clones']:
            print "Filter out clones"
            qparams['no_clones'] = '1'

        if 'couchflow' in qparams or 'no_clones' in qparams:
            print "Using filter"
            params['filter'] = 'filters/couchflow'
            params['query_params'] = qparams

        if options['create_target']:
            params['create_target'] = True

        print "Starting replication"
        print "Check %s/_utils/status.html for status" % server.uri
        server.replicate(*args, **params)
        print "Done"

