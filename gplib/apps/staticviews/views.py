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

import csv
import time

from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from gplib.apps.couchflow.models import WorkFlow, Task, WFItem, FilterWFItems
from gplib.apps.couchflow import models
from gplib.apps.couchflow.webconf import clone_this_wf
from gplib.apps.couchflow.utils import get_field


# [(field, subfield/None, column_title), ...]
CSV_COLUMNS = [
    ("020", "a", "ISBN"),
    ("100", "a", "Autor personal"),
    ("245", "a", "Titulo"),
    #("260", "a", "Publicacion/distribucion: Lugar"),
    ("260", "b", "Publicacion/distribucion: Editor"),
    ("980", "a", "Materia"),
    ("424242", "", "Cantidad"),
]
CSV_FILENAME = 'Solicitud_de_compra_%d_%m_%Y.csv'
AUTHORIZE_GROUP = 'autoriza'
AUTHORIZE_STATE = 'autorizar'
AUTHORIZE_STATE_AFTER = 'indevnull'


def is_bulkable(task):
    for i in task["item_fields"]:
        if task["item_fields"][i] == 'write':
            return False
    return True

def get_task_status(item):
    status = item['fields_properties'].get('99989', None)

    # Damn
    if not status or not status['list'] or not 'exec_value' in status['list'][0]:
        return None

    status = status['list'][0]['exec_value']
    if status:
        status = status[0]

    # TODO: why its 'none' here?
    if status == 'none':
        return None

    return status


def get_item_tasks(items_tasks):
    tasks = []
    items = {}

    items_tasks = list(items_tasks)

    for task in items_tasks:
        if not task or not task['doc']:
            continue
        doc_type = task['doc']['doc_type']

        doc = task['doc']

        if doc_type == 'WFItem':
            items[doc['_id']] = doc
        else:
            tasks.append(doc)

    return (items, tasks)

def get_tasks(user=None, exclude=None, include=None):
    exclude = exclude or []
    include = include or []
    #tasks = Task.view("couchflow/usertask", include_docs=True)

    db = Task.get_db()

    items_tasks = db.view('couchflow/usertask2', include_docs=True)

    if user:
        start = [user._id]
        end = [user._id, {}]
        items, tasks = get_item_tasks(items_tasks[start:end])
    else:
        items, tasks = get_item_tasks(items_tasks)

    tasks_dic = {}
    for task in tasks:
        if task:
            tasks_dic[task['_id']] = task

    if user:
        for group in user.groups:
            start = [group]
            end = [group, {}]

            group_items, group_tasks = get_item_tasks(items_tasks[start:end])

            items.update(group_items)

            for task in group_tasks:
                tasks_dic[task['_id']] = task


    wf_tasks = {}
    for task in tasks_dic.values():
        item = items[task['wfitems_ids'][0]]

        item["id"] = item["_id"]
        task["id"] = task["_id"]
        task["is_bulkable"] = is_bulkable(task)

        status = get_task_status(item)
        if not status:
            continue

        #wf = cache.get(task.workflow_id, None)
        #if not wf:
        #    wf = WorkFlow.get(task.workflow_id)
        #wf_type = wf.workflow_type.split('_', 1)[0]

        wf_type = task['workflow_type'].split('_', 1)[0]

        if exclude and wf_type in exclude:
            continue
        if include and wf_type not in include:
            continue

        nro_pedido = item["order_nbr"]

        if nro_pedido not in wf_tasks:
            wf_tasks[nro_pedido] = []
            wf_tasks[nro_pedido].append(nro_pedido)
        wf_tasks[nro_pedido].append(task)

        #save_tasks.append(task)

    tasks = [task for values in wf_tasks.values() for task in values]
    #db.bulk_save(save_tasks)

    return tasks


def get_status(user=None, exclude=None, include=None):
    exclude = exclude or []
    include = include or []

    db = WorkFlow.get_db()
    workflows = db.view("couchflow/user_wf", include_docs=True)
    if user:
        workflows = workflows[user._id]
    workflows = workflows.all()

    wf_ids = [x['id'] for x in workflows]

    all_items_tasks = db.view("couchflow/flowtask2", include_docs=True,
        keys=wf_ids)
    items_tasks_dict = {}
    for row in all_items_tasks:
        items_tasks_dict.setdefault(row['key'], []).append(row)

    tasks_dic = {}
    for row in workflows:
        wf = row['doc']
        wf_type = wf.get('workflow_type', '').split('_', 1)[0]
        if exclude and wf_type in exclude:
            continue

        if include and wf_type not in include:
            continue

        items_tasks = items_tasks_dict.get(row['id'], [])
        items, tasks = get_item_tasks(items_tasks)

        for task in tasks:
            item = items[task['wfitems_ids'][0]]
            status = get_task_status(item)
            if not status:
                continue

            if wf['nro_pedido'] not in tasks_dic:
                tasks_dic[wf['nro_pedido']] = [wf['nro_pedido']]
            tasks_dic[wf['nro_pedido']].append(task)

    ret_tasks = [task for values in tasks_dic.values() for task in values]
    return ret_tasks


@login_required
def index(request):
    user = request.user
    if not user.is_staff:
        return HttpResponseRedirect("/circulation/user/me")

    filter_wflows(user)
    if user.is_superuser:
        user = None

    tasks = get_tasks(user=user)
    status_tasks = get_status(user=user)

    modules = ['estado', 'pendientes']
    context = {'tasks': tasks, 'modules': modules,
        'status_tasks': status_tasks, 'module_name': 'Inicio'}

    context['can_authorize'] = False

    # "not user" means "is admin" here
    if not user or AUTHORIZE_GROUP in request.user.group_names:
        db = WFItem.get_db()
        items_to_authorize = len(db.view('couchflow/filter_items',
            include_docs=True)[AUTHORIZE_STATE])

        if items_to_authorize:
            context['can_authorize'] = True
            context['items_to_authorize'] = items_to_authorize

    return render_to_response('staticviews/adquisition.html', context,
                        context_instance=RequestContext(request))


def adquisition(request):
    return HttpResponseRedirect("/")

def filter_wflows(user):
    for i in ('libro', 'revista'):
        catalog_items('a catalogar %s' % i, user)
    # TODO
    return
    db = FilterWFItems.get_db()
    wf_tasks = db.view("couchflow/wf_by_first_task_type",
            include_docs=True)["FilterWFItems":"FilterWFItems"]

    tasks = {}
    wflows = []

    wf_tasks = wf_tasks.all()
    for value in wf_tasks:
        if value["doc"]["doc_type"] == "WorkFlow":
            wflows.append(WorkFlow.wrap(value["doc"]))
        elif value["doc"]["doc_type"] == "FilterWFItems":
            task = FilterWFItems.wrap(value["doc"])
            tasks[task._id] = task

    for wf in wflows:
        task = tasks.get(wf.first_task_id, None)
        if not task:
            raise Exception, "Check"
        field = task.item_fields.get("99989", None)
        print "Filter by", field
        if not field:
            print "cant get status field"
            continue
        filter_items = WFItem.view('couchflow/filter_items')
        items_query = filter_items[field]
        selected_items = [item['id'] for item in items_query]

        if not selected_items:
            continue

        clone = clone_this_wf(wf._id, user._id)

        clone.set_enabled()
        try:
            clone.save()
        except Exception, error:
            print error

        tasks = Task.view("couchflow/activetask", include_docs=True)
        tasks = tasks[clone._id]
        task = tasks.one()

        task.wfitems_ids = selected_items
        task.save()
        task.active_conector()

def catalog_items(status, user):
    if status.endswith('libro'):
        wfname = 'procesos_tecnicos'
    elif status.endswith('revista'):
        wfname = 'hemeroteca'
    else:
        raise Exception, 'revista or libro'

    filter_items = WFItem.view('couchflow/filter_items')

    items_query = filter_items[status]

    selected_items = [item['id'] for item in items_query]

    if not selected_items:
        return

    workflows = WorkFlow.view("couchflow/orig_workflows", include_docs=True)
    workflows = workflows[wfname]
    workflow = workflows.one()

    clone = clone_this_wf(workflow._id, user._id)

    clone.set_enabled()
    try:
        clone.save()
    except Exception, error:
        print error

    tasks = Task.view("couchflow/activetask", include_docs=True)
    tasks = tasks[clone._id]
    task = tasks.one()

    task.wfitems_ids = selected_items
    task.save()
    task.active_conector()

    return len(items_query)


@login_required
def tech_process(request):
    user_obj = request.user

    user = None
    if not user_obj.is_superuser:
        user = user_obj

    catalog = {}
    #for i in ('libro', 'revista'):
    #    catalog_items('a catalogar %s' % i, user_obj)
    filter_wflows(user_obj)

    tasks = get_tasks(user=user, include=['procesos', 'hemeroteca'])
    status_tasks = get_status(user=user, include=['procesos', 'hemeroteca'])

    modules = ['pendientes']
    context = {'tasks': tasks, 'modules': modules, 
            'status_tasks': status_tasks, 'catalog': catalog,
                           'module_name': 'Procesos Tecnicos'}
    return render_to_response('staticviews/adquisition.html', context,
                        context_instance=RequestContext(request))



@login_required
def gen_authorize_csv(request):
    if not (request.user.is_superuser or
            AUTHORIZE_GROUP in request.user.group_names):
        return HttpResponseForbidden('403 Forbidden')

    filename = time.strftime(CSV_FILENAME)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    csvfile = csv.writer(response)

    csvfile.writerow([z for (x, y, z) in CSV_COLUMNS])

    db = WFItem.get_db()
    items = db.view('couchflow/filter_items',
        include_docs=True)[AUTHORIZE_STATE]

    def get_field_utf8(*args):
        """thank you python2"""
        retval = (get_field(*args) or [''])[0]
        if type(retval) == unicode:
            return retval.encode("utf-8", "replace")
        return retval

    for item in items:
        csvfile.writerow([get_field_utf8(item['doc'], x, y)
            for (x, y, z) in CSV_COLUMNS])

    return response

@login_required
def authorize_clear(request):
    if request.method != 'POST' or not (request.user.is_superuser or
       AUTHORIZE_GROUP in request.user.group_names):
        return HttpResponseForbidden('403 Forbidden')

    db = WFItem.get_db()
    items = db.view('couchflow/filter_items',
        include_docs=True)[AUTHORIZE_STATE]

    docs = []
    for item in items:
        doc = item['doc']
        try:
            doc["fields_properties"]["99989"]["list"][0]["exec_value"][0] = \
                AUTHORIZE_STATE_AFTER
        except (KeyError, IndexError), e:
            print "Error changing state of document: %s %s" % (type(e), e)
        else:
            docs.append(doc)

    db.save_docs(docs)

    error_items = len(items) - len(docs)
    if error_items:
        # can this ever happen?
        context = {'error': "Error: %s item(s) no se pudieron actualizar" %
            error_items}

        return render_to_response('error.html', context,
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")
