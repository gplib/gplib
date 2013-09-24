#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2009 Christopher Lenz
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""Utility for dumping a snapshot of a CouchDB database to a multipart MIME
file.
"""

from base64 import b64decode
from optparse import OptionParser
import sys
import os

import json
from couchdbkit.ext.django.loading import get_db
from gplib.libs.multipart import write_multipart

from optparse import make_option
from django.core.management.base import BaseCommand


def dump_db(db, boundary=None, output=sys.stdout):
    envelope = write_multipart(output, boundary=boundary)
    for ddoc in db.view("_all_docs"):
        docid = ddoc["key"]

        doc = db.get(docid, attachments=True)
        print >> sys.stderr, 'Dumping document %r' % doc["_id"]
        attachments = doc.pop('_attachments', {})
        jsondoc = json.dumps(doc, allow_nan=False, ensure_ascii=False)

        if attachments:
            parts = envelope.open({
                'Content-ID': doc["_id"],
                'ETag': '"%s"' % doc["_rev"]
            })
            parts.add('application/json', jsondoc)

            for name, info in attachments.items():
                content_type = info.get('content_type')
                if content_type is None: # CouchDB < 0.8
                    content_type = info.get('content-type')
                parts.add(content_type, b64decode(info['data']), {
                    'Content-ID': name
                })
            parts.close()

        else:
            envelope.add('application/json', jsondoc, {
                'Content-ID': doc["_id"],
                'ETag': '"%s"' % doc["_rev"]
            })

    envelope.close()


def main():
    parser = OptionParser(usage='%prog [options] dbname')
    parser.set_defaults()
    options, args = parser.parse_args()

    if len(args) != 1:
        return parser.error('incorrect number of arguments')

    dump_db(args[0])

class Command(BaseCommand):
    help = 'Dump databases to dir'
    option_list = BaseCommand.option_list + (
        make_option('--dbs_dir',
            default=None,
            help='dbs_dir'),
    )

    def handle(self, *args, **options):
        dbs = ('couchauth', 'couchflow', 'couchsearch',
               'circulation', 'couchsessions', 'config')
        dbs_dir = options["dbs_dir"]

        uris = []
        for dbname in dbs:
            db = get_db(dbname)
            uriname = db.uri.rsplit("/", 1)[1]
            if uriname in uris:
                continue
            uris.append(uriname)
            with open(os.path.join(dbs_dir, uriname + ".json"), "w") as fileobj:
                dump_db(db, output=fileobj)
            sys.stdout.write('Successfully dumped "%s"\n' % uriname)
