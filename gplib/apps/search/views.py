# -*- coding: utf8 -*-
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

try:
    from collections import OrderedDict
except ImportError:
    from utils import OrderedDict

from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
#from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from couchdbkit.ext.django.loading import get_db
from restkit.errors import RequestFailed

from utils import search, sanitize_lucene, greenstone_query
from gplib.apps.couchflow.models import WFItem, Config
from gplib.apps.couchflow.utils import get_urn, get_field

import re

GREENSTONE_NEWSEARCH_PLACEHOLDER = '[[greenstone]]'

@csrf_exempt
@login_required
def index(request, filtered=None):
    user = request.user
    context = {"user": user, "in_search": True, "filtered": filtered}
    if request.method == "POST" and 'query' in request.POST:
        context['query'] = request.POST['query']

    if filtered:
        return render_to_response('search/search_filtered.html', context)
    else:
        return render_to_response('search/index.html', context)

def make_query(search_config, qfilter, reference, item_type):
    """
    Returns a query for couchdb-lucene
    using search_config values
    """
    if reference:
        reference = 'true'
    else:
        reference = 'false'

    querys = []
    for _id, item in search_config.values.iteritems():
        if item_type and _id != item_type:
            continue
        start = 'item_type:%s AND reference:%s' % (item['type'], reference)
        iquery = []

        for field in item['fields']:
            if field['filter']:
                q = '~ AND '.join(qfilter.split(' '))
                q = q.strip(" AND ") + "~"
                q = "(%s)" % q

                iquery.append('%s:%s' % (field['field'], q))
                iquery.append('OR')

        if iquery:
            querys.append('(%s AND (%s))' % (start, ' '.join(iquery[:-1])))

    full_query = ' OR '.join(querys)
    full_query = full_query.replace('AND ()', '')
    full_query = full_query.replace('  ', ' ')

    #full_query = '(item_type:libro AND reference:false AND 245_a:%s)' % qfilter
    #print "FQ: ", full_query
    #print
    #print "Q:", qfilter
    #print
    return full_query


@csrf_exempt
@login_required
def data(request):
    """
    Returns data for datatables
    """
    user = request.user

    secho = int(request.POST.get('sEcho', 0)) + 1
    return_dict = {"aaData": [], "iTotalRecords":0,
            "iTotalDisplayRecords":0, "sEcho": secho}
    query = None
    sort = None
    sort_reverse = False
    qfilter = ''
    basic_greenstone = True
    search_config = Config.get_or_create("search")

    if 'raw_query' in request.POST:
        query, sort_raw, query_greenstone = \
            request.POST['raw_query'].split("||", 2)
        if sort_raw:
            sort = sort_raw[1:]
            sort_reverse = (sort_raw[0] == '\\')

        # make_advanced_query() doesn't handle greenstone filtering.
        # Instead, it leaves a placeholder that is replaced here.
        # This is to leave all the querying to the second request
        # (this one), and only lucene query building to the first.

        query = query.replace(GREENSTONE_NEWSEARCH_PLACEHOLDER,
            "(%s)" % (' OR '.join(["urn:%s" % x['nodeID'] for x in
            greenstone_query("", "", query_greenstone)])))
        basic_greenstone = False

    elif 'filter' in request.POST:
        qfilter = sanitize_lucene(request.POST['filter'])
        qfilter = request.POST['filter']
        reference = request.POST.get('reference', 0)
        filter_item_type = request.POST.get('item_type', None)

        query = make_query(search_config, qfilter, reference, filter_item_type)
    elif 'filtered' in request.POST:
        qfilter = sanitize_lucene(request.POST['filtered'])
        reference = request.POST.get('reference', 0)
        filter_item_type = request.POST.get('item_type', None)

        query = make_query(search_config, qfilter, reference, filter_item_type)

    if not query:
        print "search failed: query = %s" % query
        return HttpResponse(simplejson.dumps(return_dict),\
                    mimetype='application/javascript')

    show_config = {}

    # Result Display Configuration
    for item in search_config.values.values():
        item_type = item['type']

        fields = OrderedDict()
        for field in item['fields']:
            if field['show']:
                more = field.get('more', False)
                existence = field.get('exist', False)
                fields[field['field']] = (field['name'], more, existence)

        show_config[item_type] = fields

    try:
        docs = search('search/by_field', q=query,
                include_fields="022_a,020_a,urn,_id,existence",
                                  limit=133742)
        docs = list(docs)
    except RequestFailed:
        print "search failed: request failed"
        return HttpResponse(simplejson.dumps(return_dict),\
                    mimetype='application/javascript')

    db = get_db('couchflow')

    # group uniq docs by urn
    uniq_docs = {}

    if basic_greenstone:
        greenstone_urns = [x['nodeID'] for x in greenstone_query("", "", qfilter)]
        greenstone_docs = db.view("couchflow/by_urn", keys=greenstone_urns)

        for doc in greenstone_docs:
            urn = doc['key']
            uniq_docs.setdefault(urn, {'count':0, 'id': None, "existences": []})
            uniq_docs[urn]['id'] = doc['id']
            #uniq_docs[urn]['count'] += 1
            uniq_docs[urn]['greenstone'] = True

    for doc in docs:
        try:
            urn = doc['fields']['urn']
        except KeyError:
            urn = None

        if urn is None or urn == 'undefined':
            print "Item should have urn", doc['id']
            continue

        # TODO: check if should be a list
        if type(urn) is list:
            urn = urn[0]

        uniq_docs.setdefault(urn, {'count':0, 'id': None, "existences": []})
        if doc['fields']['existence'] != "false":
            uniq_docs[urn]['existences'].append(doc['id'])
            uniq_docs[urn]['count'] += 1
        else:
            uniq_docs[urn]['id'] = doc['id']

    columns = []

    start = int(request.POST['iDisplayStart'])
    length = int(request.POST['iDisplayLength'])

    #sort_col = int(request.POST['iSortCol_0'])
    #sort_dir = request.POST['sSortDir_0']

    count = len([u for u in uniq_docs.values() if u["id"]])

    sorted_uniq_docs = uniq_docs.values()
    if basic_greenstone:
        sorted_uniq_docs.sort(key=lambda x: 'greenstone' not in x)

    keys = [doc['id'] for doc in sorted_uniq_docs[start:start+length]]
    keys_exist = [doc['existences']\
            for doc in sorted_uniq_docs[start:start+length]]
    keys_exist = [item for sublist in keys_exist for item in sublist]

    def _get_field(field, doc):
        subfield = ""
        if '_' in field:
            field, subfield = field.split('_')

        #field_value = doc.fields_properties.get(field, None)
        try:
            field_value = doc["fields_properties"][field]
        except KeyError:
            field_value = ""

        if field_value and len(field_value['list']):
            field_value = field_value['list'][0]
            if subfield:
                field_value = field_value['subfields'].get(subfield, "")

            if field_value and 'exec_value' in field_value and field_value['exec_value']:
                exec_val = field_value['exec_value'][0]
                if not isinstance(exec_val, basestring):
                    if exec_val == None:
                        exec_val = ""
                    exec_val = str(exec_val)
                return exec_val
        return ""

    # get existences
    existences = {}
    for doc in db.view('_all_docs', keys=keys_exist, include_docs=True):
        existences[doc["doc"]["_id"]] = doc["doc"]

    for doc in db.view('_all_docs', keys=keys, include_docs=True):
        #doc = WFItem.wrap(doc['doc'])
        if not "doc" in doc:
            continue
        doc = doc["doc"]

        show_item_config = show_config.get(doc['item_type'], None)
        if not show_item_config:
            print 'Search config missing for', doc['item_type']
            continue

        try:
            img_name = doc['fields_properties']['5000']['list'][0]['exec_value'][0]
        except Exception, error:
            print 'Image not found', error
            img_name = 'none.png'

        img_path = "/couchflow/get_attach/couchflow/%s/%s" % (doc['_id'], img_name)
        row = [doc['_id'], '<img style="width:80px" src="%s"/>' % img_path]

        data = ''
        for field, (name, more, existence) in show_item_config.iteritems():
            if existence: continue
            field_value = _get_field(field, doc)
            if not field_value:
                continue
            row_value = '%s: %s' % (name, field_value)

            row_value = row_value.replace('/', '').replace(',', '')
            more_class = ' class="search_more"' if more else ''
            data += '<div%s>%s</div>' % (more_class, row_value)

        doc_urn = get_urn(doc)
        if not doc_urn:
            print "Invalid Item, need a urn", doc["_id"]
            continue

        if not doc['reference']:
            data += 'Disponibles: %s<br>' % uniq_docs[doc_urn]['count']

        if uniq_docs[doc_urn]["existences"]:
            data += "<br><h3 class='search_more'>Ejemplares</h3>"
        # Add Existences
        for e in uniq_docs[doc_urn]["existences"]:
            if existences.get(e, False):
                data += "<div id='%s' class='existence search_more'>" % e
                for field, (name, more, exist_conf) in\
                        show_item_config.iteritems():
                    if exist_conf:
                        field_value = _get_field(field, existences[e])
                        if not field_value:
                            field_value = ""

                        row_value = '%s: %s' % (name, field_value)
                        row_value = row_value.replace('/', '').replace(',', '')
                        more_class = ' class="search_more"' if more else ''
                        data += '<div%s>%s</div>' % (more_class, row_value)
                data += "</div>"

        row.append(data)
        row.append('')

        sort_value = None
        if sort:
            sort_value = _get_field(sort, doc)

        columns.append((sort_value, row))

    if sort:
        # sorting is done locally since the lucene returned order isn't kept
        columns.sort(key=lambda x: x[0], reverse=sort_reverse)
    columns = [x[1] for x in columns]

    return_dict = {"sEcho": secho, "iTotalRecords": count,
                   "iTotalDisplayRecords": count,
                   "aaData": columns}
    return HttpResponse(simplejson.dumps(return_dict),\
                    mimetype='application/javascript')



def save_config(request, wf_items):
    """
    Parse request.POST, get field/subfields
    items and save config
    """
    search_config = Config.get_or_create("search")
    if request.method == "POST":
        for wf_item in wf_items:
            item_id = wf_item._id
            item_type = wf_item.item_type

            item_conf = {'type': item_type, 'fields': []}
            fields_conf = item_conf['fields']

            for field in request.POST.getlist(item_id + "_field"):
                index, field_id = field.split('_', 1)

                field_conf = {}

                f_show = request.POST.get("%s_%s_show" % (item_id, index))
                f_filter = request.POST.get("%s_%s_filter" % (item_id, index))
                f_more = request.POST.get("%s_%s_more" % (item_id, index))
                f_adv = request.POST.get("%s_%s_advanced" % (item_id, index))
                f_advdef = request.POST.get("%s_%s_advdef" % (item_id, index))
                f_exist = request.POST.get("%s_%s_exist" % (item_id, index))
                f_name = request.POST.get("%s_%s_name" % (item_id, index))

                if '_' in field_id:
                    main_id, sub_id = field_id.split('_', 1)
                    type = wf_item.fields_properties[main_id].list[0]\
                        .subfields[sub_id].type
                else:
                    type = wf_item.fields_properties[field_id].type

                field_conf['show'] = f_show == "on"
                field_conf['filter'] = f_filter == "on"
                field_conf['more'] = f_more == "on"
                field_conf['advanced'] = f_adv == "on"
                field_conf['advdef'] = f_advdef == "on"
                field_conf['exist'] = f_exist == "on"
                field_conf['name'] = f_name
                field_conf['field'] = field_id
                field_conf['type'] = type

                fields_conf.append(field_conf)

            search_config.values[item_id] = item_conf
        search_config.save()

@login_required
def get_fields(request):
    """
    Returns a json with selected fields in config
    """
    search_config = Config.get_or_create("search")

    items = {}

    for _id, item in search_config.values.iteritems():
        items[_id] = item['fields']
        for field in item['fields']:
            field['field'] = "#index#_" + field['field']

            if not field['filter']:
                del(field['filter'])
            if not field['show']:
                del(field['show'])
            if 'more' in field and not field['more']:
                del(field['more'])
            if 'advanced' in field and not field['advanced']:
                del(field['advanced'])
            if 'advdef' in field and not field['advdef']:
                del(field['advdef'])
            if 'exist' in field and not field['exist']:
                del(field['exist'])

    return HttpResponse(simplejson.dumps(items),
                    mimetype='application/javascript')

@csrf_exempt
@login_required
def admin(request):
    user = request.user
    context = {"user": user}

    wf_items = list(WFItem.view("couchflow/items", include_docs=True))
    save_config(request, wf_items)

    settings = Config.get_or_create("search_settings")
    default_type = settings.values.get('default_type', '')

    if request.method == "POST":
        post_default_type = request.POST.get('default_type', '')
        if post_default_type != default_type:
            settings.values['default_type'] = post_default_type.lower()
            settings.save()
            default_type = post_default_type

    items = []
    for item in wf_items:
        fields = {}
        for _id, ifields in item.fields_properties.iteritems():
            # Just marc fields
            if int(ifields['id']) > 1000:
                continue

            field_name = ifields['id']

            if ifields['list'][0].subfields:
                default_field = {'id': ifields['id'], 'name':
                            ifields['field_name'],
                            'subfields': {}}

                subfields = fields.setdefault(field_name,
                                default_field)["subfields"]

                for subfield in ifields['list'][0].subfields.values():
                    sfield_name = '%s_%s' % (ifields['id'],
                                        subfield.field_name)
                    sfield = subfields.setdefault(sfield_name, {})
                    sfield['name'] = subfield.field_name

                fields[field_name]['subfields'] = sorted(subfields.items())
            else:
                fields.setdefault(field_name ,{})['id'] = field_name
                fields[field_name]['name'] = ifields.field_name

        items.append((item.name, item._id, sorted(fields.items())))

    context['items'] = items
    context['default_type'] = default_type.lower()

    return render_to_response('search/admin.html', context)

# i seriously couldn't think anything better to send fields
# with no order number to the end
VERY_BIG_NUMBER = 2**32-1

@csrf_exempt
@login_required
def newsearch(request):
    newsearch_fields = []
    preselected_fields = []
    search_config = Config.get_or_create("search")
    for _id, item in search_config.values.iteritems():
        for field in item['fields']:
            if field.get('advanced', False):
                nsf_entry = (field['field'], field['name'], item['type'],
                    field.get('type', 'string'))
                newsearch_fields.append(nsf_entry)
                if field.get('advdef', False):
                    preselected_fields.append((nsf_entry, '', 'AND'))

    newsearch_fields.append(("_ft", "Fulltext (greenstone)",
        "_ft", "_ft"))

    settings = Config.get_or_create("search_settings")
    default_type = settings.values.get('default_type', '').lower()

    newsearch_fields_dict = dict([(x[0], x) for x in newsearch_fields])

    context = {"user": request.user, "in_search": True,
        "fields_select_options": newsearch_fields,
        "selected_type": default_type}

    if request.method == "POST":
        context['postdata'] = request.POST
        context['selected_type'] = request.POST.get('item_type',
            default_type).lower()
        context['fields_select'] = request.POST.getlist('fields_select')
        context['fields_select'].sort(key=lambda x: request.POST.get(
            "order_%s" % x, VERY_BIG_NUMBER))

        def get_post_value(field):
            if newsearch_fields_dict.get(field, [None])[-1] == 'date':
                return [request.POST.get(field + x, '')
                    for x in ("_from", "_to")]
            else:
                return request.POST.get(field, '')

        context['selected_fields'] = \
            [(newsearch_fields_dict.get(field, [None] * 4),
              get_post_value(field),
              request.POST.get("operator_%s" % field, 'AND'))
            for field in context['fields_select']
            if field in newsearch_fields_dict]
        context['raw_query'] = make_advanced_query(request, newsearch_fields)

    if not context.get('selected_fields', []):
        context['selected_fields'] = preselected_fields
        context['fields_select'] = [x[0][0] for x in preselected_fields]

    context['item_types'] = ['revista', 'libro']

    return render_to_response('search/newsearch.html', context)

def make_advanced_query(request, newsearch_fields):
    query = []
    query_greenstone = ''

    item_type = sanitize_lucene(request.POST.get('item_type'))
    if item_type:
        query.append("item_type:%s" % item_type)

    searchfields_by_type = {}
    for field_id, field_name, field_item_type, field_type in newsearch_fields:
        searchfields_by_type.setdefault(field_item_type, [])
        searchfields_by_type[field_item_type].append((field_id, field_name,
            field_type))

    if '_ft' in searchfields_by_type:
        ft_field_list = searchfields_by_type.pop('_ft')
        for key in searchfields_by_type:
            searchfields_by_type[key] += ft_field_list

    def transform_field_query(field, value):
        matches = list(re.finditer("(AND|OR|NOT)", value))

        def transform_section(section):
            section = sanitize_lucene(section.strip())
            if section:
                section = '~ AND '.join(section.split(' '))
                section = section.strip(" AND ") + "~"
                return '%s:(%s)' % (field, section)
            else:
                return ''

        output = []
        last_end = 0

        for match in matches:
            output.append(transform_section(value[last_end:match.start()]))
            output.append(match.group(1))
            last_end = match.end()

        output.append(transform_section(value[last_end:]))

        return ' '.join(output)

    fields_query = []
    for field_item_type, field_list in searchfields_by_type.iteritems():
        if item_type and field_item_type != item_type:
            continue

        field_list.sort(key=lambda x: request.POST.get("order_%s" % x[0],
            VERY_BIG_NUMBER))

        this_type_query = []
        first = True
        for field_id, field_name, field_type in field_list:
            value = request.POST.get(field_id, None)
            op = request.POST.get("operator_%s" % field_id, 'AND')

            if field_type == 'date':
                value = tuple([sanitize_lucene(request.POST.get(
                    field_id + x, None), '-') for x in ("_from", "_to")])

            if value:
                if field_type == 'date':
                    q = '%s<date>:[%s TO %s]' % ((field_id,) + value)
                elif field_type == '_ft':
                    q = GREENSTONE_NEWSEARCH_PLACEHOLDER
                    query_greenstone = value
                else:
                    q = transform_field_query(field_id, value)

                if not first:
                    if op not in ('AND', 'OR', 'NOT'):
                        op = 'AND'
                    if op == 'NOT':
                        op = 'AND NOT'
                else:
                    if op != 'NOT':
                        op = ''

                this_type_query.append("%s (%s)" % (op, q))
                first = False

        if field_item_type is None:
            fields_query.append("(%s)" % " ".join(this_type_query))
        else:
            if this_type_query:
                fields_query.append("(item_type:%s AND (%s))" % (
                    field_item_type, " ".join(this_type_query)))

    query.append(' OR '.join(fields_query))

    full_query = ' AND '.join(query)
    #print full_query

    sort = ''
    if request.POST.get("sort", ''):
        sort = ('\\' if (request.POST.get("ascdesc", "asc") == 'desc')
            else '/') + request.POST.get("sort")
    #print sort
    return "%s||%s||%s" % (full_query, sort, query_greenstone)

@csrf_exempt
@login_required
def reference_complete(request):
    """
    Returns data for reference complete
    """

    query = request.GET.get("term")
    qfilter = sanitize_lucene(query)
    search_config = Config.get_or_create("search")
    # autoridades
    query = make_query(search_config, qfilter, True, "05a721a33096563ec44d8da885fa1a30")

    show_config = {}

    result = []

    # Result Display Configuration
    for item in search_config.values.values():
        item_type = item['type']

        fields = OrderedDict()
        for field in item['fields']:
            if field['show']:
                more = field.get('more', False)
                fields[field['field']] = (field['name'], more)

        show_config[item_type] = fields

    try:
        docs = search('search/by_field', q=query,
                include_fields="022_a,020_a,urn,_id",
                                  limit=133742)
        docs = list(docs)
    except RequestFailed:
        print "Fail!"
        print "QQ", query

    # group uniq docs by urn
    uniq_docs = {}

    for doc in docs:
        try:
            urn = doc['fields']['urn']
        except KeyError:
            print "Item should have urn"
            continue

        # TODO: check if should be a list
        if type(urn) is list:
            urn = urn[0]

        uniq_docs.setdefault(urn, {'count':0, 'id': None})
        uniq_docs[urn]['id'] = doc['id']
        uniq_docs[urn]['count'] += 1

    db = get_db('couchflow')
    keys = [doc['id'] for doc in uniq_docs.values()]

    def _get_field(field, doc):
        subfield = ""
        if '_' in field:
            field, subfield = field.split('_')

        #field_value = doc.fields_properties.get(field, None)
        try:
            field_value = doc["fields_properties"][field]
        except KeyError:
            field_value = ""

        if field_value and len(field_value['list']):
            field_value = field_value['list'][0]
            if subfield:
                field_value = field_value['subfields'].get(subfield, "")

            if field_value and 'exec_value' in field_value and field_value['exec_value']:
                exec_val = field_value['exec_value'][0]
                if not isinstance(exec_val, basestring):
                    if exec_val == None:
                        exec_val = ""
                    exec_val = str(exec_val)
                return exec_val
        return ""

    for doc in db.view('_all_docs', keys=keys, include_docs=True):
        #doc = WFItem.wrap(doc['doc'])
        doc = doc["doc"]

        show_item_config = show_config.get(doc['item_type'], None)
        if not show_item_config:
            print 'Unknown', doc['item_type']
            continue

        field = _get_field('700_a', doc)
        result.append({'label': field})
        #data = ''
        #for field, (name, more) in show_item_config.iteritems():
        #    row_value = '%s: %s' % (name, _get_field(field, doc))

        #    row_value = row_value.replace('/', '').replace(',', '')
        #    data += '<div>%s</div>' %  row_value

        #doc_urn = get_urn(doc)
        #if not doc_urn:
        #    print "Invalid Item, need a urn", doc["_id"]
        #    continue

        #result.append(data)

    return HttpResponse(simplejson.dumps(result),\
                    mimetype='application/javascript')
