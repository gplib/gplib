#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2009 Christopher Lenz
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""Utility for loading a snapshot of a CouchDB database from a multipart MIME
file.
"""

import sys
import glob
from base64 import b64encode

try:
    import simplejson as json
except ImportError:
    import json

from optparse import make_option
from gplib.libs.multipart import read_multipart
from couchdbkit.ext.django.loading import get_db

from django.core.management.base import BaseCommand


def load_db(fileobj, dbname, ignore_errors=False):
    db = get_db(dbname)

    for headers, is_multipart, payload in read_multipart(fileobj):
        docid = headers['content-id']

        if is_multipart: # doc has attachments
            for headers, _, payload in payload:
                if 'content-id' not in headers:
                    doc = json.loads(payload)
                    doc['_attachments'] = {}
                else:
                    doc['_attachments'][headers['content-id']] = {
                        'data': b64encode(payload),
                        'content_type': headers['content-type'],
                        'length': len(payload)
                    }

        else: # no attachments, just the JSON
            doc = json.loads(payload)

        del doc['_rev']
        print>>sys.stderr, 'Loading document %r' % docid
        try:
            db[docid] = doc
        except Exception, e:
            if not ignore_errors:
                raise
            print>>sys.stderr, 'Error: %s' % e

class Command(BaseCommand):
    help = 'Dump databases to dir'
    option_list = BaseCommand.option_list + (
        make_option('--dbs_dir',
            default=None,
            help='dbs_dir'),
    )

    def handle(self, *args, **options):
        dbs = options["dbs_dir"]

        for dbname in glob.glob("%s/*" % dbs):
            with open(dbname) as fileobj:
                load_db(fileobj, args[0])
            sys.stdout.write('Successfully updated "%s"\n' % dbname)
