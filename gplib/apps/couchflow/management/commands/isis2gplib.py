#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# isis2json.py: convert ISIS and ISO-2709 files to JSON
#
# Copyright (C) 2010 BIREME/PAHO/WHO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

try:
    import simplejson as json
except ImportError:
    import json

from optparse import make_option

from gplib.libs.iso2709 import IsoFile

from django.core.management.base import BaseCommand
from gplib.apps.couchflow.models import WFItem, Fields, Field, SubField

#SUBFIELD_DELIMITER = '^'
SUBFIELD_DELIMITER = '\x1f'
INPUT_ENCODING = 'latin1'


def iter_iso_records(iso_file_name, subfields):
    def parse(field):
        content = field.value.decode(INPUT_ENCODING,'replace')

        parts = content.split(SUBFIELD_DELIMITER)
        subs = {}
        main = parts.pop(0)

        if len(main) > 0:
            subs['_'] = main

        for part in parts:
            try:
                prefix = part[0]
                subs[prefix] = part[1:]
            except IndexError, e:
                pass
        return subs

    iso = IsoFile(iso_file_name)
    for record in iso:
        fields = {}
        for field in record.directory:
            field_key = str(int(field.tag)) # remove leading zeroes
            field_occurrences = fields.setdefault(field_key,[])

            if subfields:
                field_occurrences.append(parse(field))
            else:
                field_occurrences.append(
                        field.value.decode(INPUT_ENCODING,'replace'))

        yield fields
    iso.close()

import copy
import uuid

def clone_json(json_data):
    json_data = copy.deepcopy(json_data)

    del(json_data['_id'])
    if '_rev' in json_data:
        del(json_data['_rev'])
    if '_attachments' in json_data:
        del(json['_attachments'])
    json_data["_id"] = uuid.uuid1().hex
    json_data["is_clone"] = True
    return json_data

def get_field(record, field, subfield):
    subfields = []
    for sf in record.get(field, []):
        sf = sf.get(subfield, None)
        if sf:
            subfields.append(sf)
    return subfields


def add_field(key, fields, json_item):
    #key = int(key)
    indicadores = "  "
    field_values = []
    subfield_values = {}

    for v in fields:
        for k in v.keys():
            if k == "_":
                if len(v[k]) == 2 and len(v) > 1:
                    indicadores = v[k]
                   #print "I", indicadores
                elif len(v) == 1:
                    field_values.append(v[k])
                else:
                    #print key, "wtf?: ", v
                    pass
            else:
                subfield_values.setdefault(k, [])
                subfield_values[k].append(v[k])
    #print key, field_values
    #print key, subfield_values

    #['99989']['list'][0]['exec_value'] = ['activo']

    item_field = json_item["fields_properties"].get(key, None)
    if not item_field:
        fields_d = {
            'default_value': " ",
            'doc_type': 'Fields',
            'exec_value': [],
            'type': u'string',
            'list': [
                {'doc_type': 'Field', 'type': u'string',
                'indicator2': " ", 'indicator1': " ", 'subfields':{}
             }],
            'repeat': False,
            'field_name': "",
            'id': key}

        json_item["fields_properties"][key] = fields_d
        item_field = json_item["fields_properties"][key]

    if indicadores:
        item_field["indicator1"] = indicadores[0]
        item_field["indicator2"] = indicadores[1]

    if field_values:
        item_field['list'][0]['exec_value'] = field_values
    elif subfield_values:
        first = item_field['list'][0]
        for subfield_key in subfield_values.keys():
            item_subfield = first["subfields"].get(subfield_key, None)
            if not item_subfield:
                sub_field = {'default_value': u'',
                       'doc_type': 'SubField',
                       'exec_value': [], 'description': u'',
                       'field_name': u'k', 'repeat': False,
                       'type': u'string', 'id': None}
                first["subfields"][subfield_key] = sub_field

            first["subfields"][subfield_key]["exec_value"] = \
                           subfield_values[subfield_key]

    #for value in values:
    #    item_subfield.exec_value.append(value['_'])
    #    #print value['_']


class Command(BaseCommand):
    help = 'Import data from isis'
    option_list = BaseCommand.option_list + (
        make_option('--from',
            default=None,
            help='iso file'),
        make_option('--map',
            default=None,
            help='map file'),
        make_option('--dry-run',
            action='store_true',
            default=False,
            help='Do not add entries to the database'),
        make_option('--fake-isbn',
            action='store_true',
            default=False,
            help='Add a fake 1020_a field'),
        make_option('--per-iter',
            default=400,
            type=int,
            help='Number of entries to add per iteration'),
    )

    def handle(self, *args, **options):
        #filename = args['filename']
        subfields = True
        filename = options['from']
        items = []

        db = WFItem.get_db()
        orig_item = WFItem.view('couchflow/item_names',
            include_docs=True)['libro'].first()

        org_json_item = orig_item.to_json()

        counter = 0

        i = 0
        for record in iter_iso_records(filename, subfields):
            i += 1
            json_item = clone_json(org_json_item)
            json_item["fields_properties"]['99989']['list'][0]['exec_value'] = ['catalogado']

            copies = []
            has_isbn = False
            for key, fields in record.iteritems():
                key = "%03d" % int(key)
                if key == '020':
                    has_isbn = True

                if key == "852":
                    copies = fields
                    continue
                add_field(key, fields, json_item)

            if not has_isbn and options['fake_isbn']:
                json_item["fields_properties"]['1020']['list'][0] \
                    ['subfields']['a']['exec_value'] = [uuid.uuid4().hex]

            items.append(json_item)

            # add existences
            for field in copies:
                json_item = clone_json(json_item)
                add_field("852", [field], json_item)
                add_field("1111", [{"_": "existencia"}], json_item)
                items.append(json_item)

            if len(items) >= options['per_iter']:
                if not options['dry_run']:
                    db.bulk_save(items, use_uuids=False)
                counter += len(items)
                items = []
                print '%s %s items (total %s)' % ('Parsed' if
                    options['dry_run'] else 'Inserted',
                    options['per_iter'], counter)

        if items and not options['dry_run']:
            db.bulk_save(items, use_uuids=False)
        counter += len(items)
        print
        print "Done, %s items" % counter
        print ""
