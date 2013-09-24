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

from django.utils import simplejson
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from couchdbkit import ResourceConflict
from couchdbkit.resource import ResourceNotFound

from models import MultipleInstances, WFItem, Field, Fields, SubField
from models import get_conector, get_task, UntilConector
from models import SimpleMergeConector, SyncConector, ParallelSplit
from models import WorkFlow, Task, Conector, SequenceConector, ExclusiveChoice
from models import Config, DecisionTask

from forms import CloneItemsForm
from forms import WorkFlowForm, ProcessTaskForm
from forms import ConectorChoiceForm, TaskChoiceForm
from forms import DynamicDataTaskForm, WFItemsLoaderForm, WFItemForm
from forms import DecisionTaskForm, FilterWFItemsForm, MarcImportForm

from gplib.apps.couchauth.models import User, Group

import os.path

@login_required
def index(request):
    workflows = WorkFlow.view("couchflow/all", include_docs=True)
    context = {'workflows': workflows}
    return render_to_response('webconf/couchflow/index.html', context,
                              context_instance=RequestContext(request))


def clone_task(task_id, prev_conector_id, workflow):
    org_task = get_task(task_id)

    prev_task_id = org_task._id

    task = org_task.really_clone()
    task.is_clone = True

    task.workflow_id = workflow._id
    task.workflow_type = workflow.workflow_type
    task.workflow_nro = workflow.nro_pedido

    task.prev_conector_id = prev_conector_id
    task.old_id = prev_task_id
    task.save()

    prv_task = {prev_task_id: task._id}
    if task.conector_id:
        next_conector = get_conector(task.conector_id)
        if next_conector.doc_type != "SyncConector" and \
               next_conector.doc_type != "SimpleMergeConector":
            task.conector_id = clone_branch(task.conector_id, workflow,\
                                            prev_replace_tasks=prv_task)
        else:
            if next_conector._id in workflow.merge_conectors:
                task.conector_id = workflow.merge_conectors[next_conector._id]
                conector = get_conector(task.conector_id)
                index_prev_task = conector.previous_tasks.index(prev_task_id)
                conector.previous_tasks[index_prev_task] = task._id
                conector.save()
            else:

                old_id = task.conector_id
                task.conector_id = clone_branch(task.conector_id, workflow,\
                                                prev_replace_tasks=prv_task)
                workflow.merge_conectors[old_id] = task.conector_id
                workflow.save()
        task.save()
    return task._id


def clone_this_wf(workflow_id, user_id):
    workflow_org = WorkFlow.get(workflow_id)
    first_conector = workflow_org.get_first_conector()

    workflow = workflow_org.really_clone()

    workflow.user_id = user_id
    workflow.is_clone = True
    workflow.enabled = True

    nro_pedido = WorkFlow.view('couchflow/max_pedido', limit=1, descending=True)
    nro_pedido = nro_pedido.one()

    if not nro_pedido:
        nro_pedido = 41
    else:
        nro_pedido = int(nro_pedido['key'])

    nro_pedido += 1
    workflow.nro_pedido = nro_pedido
    workflow.save()
    new_conector_id = clone_branch(first_conector._id, workflow)
    workflow.conectors = {new_conector_id: True}
    workflow.tasks = {}

    conectors = Conector.view("couchflow/flowconector", include_docs=True)
    conectors = conectors[workflow._id]
    for conector in conectors:
        workflow.conectors[conector._id] = True

    # TODO: move to flowtask2
    tasks = Task.view("couchflow/flowtask", include_docs=True)
    tasks = tasks[workflow._id]
    for task in tasks:
        if task.active:
            task.user_id = user_id
            task.save()
        workflow.tasks[task._id] = True

    #TODO: check this
    #del(workflow._doc['_rev'])
    try:
        workflow.save()
    except ResourceConflict:
        pass

    return workflow


@login_required
def clone_workflow(request, workflow_id):
    workflow = clone_this_wf(workflow_id, request.user._id)
    url_redirect = "/webconf/couchflow/enable_disable/%s/" % workflow._id
    return HttpResponseRedirect(url_redirect)


def clone_branch(conector_id, workflow, prev_replace_tasks=None):
    if not prev_replace_tasks:
        prev_replace_tasks = {}

    conector = get_conector(conector_id)

    first_conector = conector.really_clone()
    first_conector.is_clone = True
    first_conector.workflow_id = workflow._id

    for i in prev_replace_tasks:
        if i in first_conector.previous_tasks:
            p_task_index = first_conector.previous_tasks.index(i)
            first_conector.previous_tasks[p_task_index] = prev_replace_tasks[i]
        else:
            first_conector.previous_tasks.append(prev_replace_tasks[i])

    first_conector.save()
    if len(prev_replace_tasks) > 0:
        first_conector.name = "primero"

    next_tasks = []
    if first_conector.doc_type != "UntilConector":
        for task_id in first_conector.next_tasks:
            n_task_id = clone_task(task_id, first_conector._id, workflow)
            next_tasks.append(n_task_id)
    else:
        t_id = first_conector.next_tasks[0]
        t_id = clone_task(t_id, first_conector._id, workflow)
        next_tasks.append(t_id)
        if len(first_conector.next_tasks) > 1:
            t_id = first_conector.next_tasks[1]
            t_task = Task.view("couchflow/taskoldid", include_docs=True)
            t_task = t_task[t_id]
            t_task = t_task.all()[0]
            next_tasks.append(t_task._id)

    first_conector.next_tasks = next_tasks
    first_conector.save()

    return first_conector._id


@login_required
def delete_task(request, task_id):
    task = get_task(task_id)
    if task.prev_conector_id:
        conector = get_conector(task.prev_conector_id)
        conector.next_tasks.remove(task._id)
        conector.save()

    if task.conector_id:
        conector = get_conector(task.conector_id)
        if conector:
            for i in conector.next_tasks:
                next_task = get_task(i)
                next_task.prev_conector_id = None
                next_task.save()
            conector.delete()

    task.delete()
    response_dict = {}
    response_dict['response'] = True
    response_dict['status'] = "Tarea eliminada"
    return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')


@login_required
def connect_nodes(request, conector_id, task_id, conn_type):
    conector = get_conector(conector_id)
    task = get_task(task_id)
    response_dict = {}
    if conn_type == "prev":
        if task.conector_id == None:
            if conector.add_previous_task(task):
                task.conector_id = conector._id
                task.save()
                conector.save()
                response_dict['response'] = True
                response_dict['status'] = "Conexion realizada"
                return HttpResponse(simplejson.dumps(response_dict),\
                                    mimetype='application/javascript')
            response_dict['response'] = False
            response_dict['status'] = "El conector no acepta la conexion"
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
        response_dict['response'] = False
        response_dict['status'] = "La tarea ya tiene asignada un conector"
        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')
    elif conn_type == "next":
        if task.prev_conector_id == None:
            if conector.add_next_task(task):

                task.prev_conector_id = conector._id
                task.save()
                task.put_step()
                conector.save()
                next_conector = get_conector(task.conector_id)
                next_conector.step = task.step + 1
                next_conector.save()
                response_dict['response'] = True
                response_dict['status'] = "Conexion realizada"
                return HttpResponse(simplejson.dumps(response_dict),\
                                    mimetype='application/javascript')
            response_dict['response'] = False
            response_dict['status'] = "El conector no acepta la conexion"
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
        else:
            prev_conector = get_conector(task.prev_conector_id)
            if prev_conector.doc_type == "SyncConector" or \
                   prev_conector.doc_type == "SimpleMergeConector":
                for p_id in conector.previous_tasks:
                    p_task = get_task(p_id)
                    if prev_conector.add_previous_task(p_task):
                        p_task.conector_id = prev_conector._id
                        p_task.save()
                conector.delete()
                response_dict['response'] = True
                rstat = "El conector acepto la conexion de dos tareas previas"
                response_dict['status'] = rstat
                return HttpResponse(simplejson.dumps(response_dict),\
                                    mimetype='application/javascript')
            elif conector.doc_type == "UntilConector":
                conector.add_next_task(task)
                conector.save()
                response_dict['response'] = True
                response_dict['status'] = "Conexion realizada"
                return HttpResponse(simplejson.dumps(response_dict),\
                                    mimetype='application/javascript')

        response_dict['response'] = False
        response_dict['status'] = "La tarea ya tiene asignada un conector"
        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')
    else:
        response_dict['response'] = False
        response_dict['status'] = "Elija entre prev y next"
        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')


@login_required
def change_conector_type(request, conector_id, conector_type):
    conector = get_conector(conector_id)
    response_dict = {}
    if  conector_type == 'SequenceConector' or conector_type == 'ExclusiveChoice'\
       or conector_type == 'ParallelSplit' or conector_type == 'MultipleInstances'\
       or conector_type == 'UntilConector' or conector_type == 'SyncConector' or \
       conector_type == 'SimpleMergeConector':
        if conector.doc_type != conector_type:
            conector.doc_type = conector_type
            conector.save()
            response_dict['response'] = True
            response_dict['status'] = "El Conector se edito correctamente"
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
    response_dict['response'] = False
    response_dict['status'] = """Elija solamente entre SequenceConector,
    ExclusiveChoice, ParallelSplit, MultipleInstances, UntilConector,
    SyncConector, SimpleMergeConector"""
    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')


@login_required
def disconnect_nodes(request, conector_id, task_id):
    conector = get_conector(conector_id)
    task = get_task(task_id)
    if task and conector:
        if task.conector_id == conector._id:
            if task._id in conector.previous_tasks:
                conector.previous_tasks.remove(task._id)
                conector.save()
                task.conector_id = None
                task.save()
        elif task.prev_conector_id == conector._id:
            if task._id in conector.next_tasks:
                task.prev_conector_id = None
                task.save()
                conector.next_tasks.remove(task._id)
                conector.save()
        elif conector.doc_type == "UntilConector":
            if task._id in conector.next_tasks:
                if conector.back_task_id == task._id:
                    conector.back_task_id = None
                conector.next_tasks.remove(task._id)
                conector.save()
            else:
                response_dict = {}
                response_dict['response'] = False
                response_dict['status'] = "No existe la relacion"
                return HttpResponse(simplejson.dumps(response_dict),\
                                    mimetype='application/javascript')
        else:
            response_dict = {}
            response_dict['response'] = False
            response_dict['status'] = "No existe la relacion"
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
        response_dict = {}
        response_dict['response'] = True
        response_dict['status'] = "Se desconctaron satisfactoriamente"
        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')

    response_dict = {}
    response_dict['response'] = False
    if not task:
        response_dict['status'] = "La tarea no existe"
    if not conector:
        response_dict['status'] = "El conector no  existe"

    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')


@login_required
def enable_disable(request, workflow_id):
    workflow = WorkFlow.get(workflow_id)
    workflow.set_enabled()
    workflow.save()
    return HttpResponseRedirect('/webconf/couchflow/')



@login_required
def new_workflow(request):
    form = WorkFlowForm()
    form_url = "/webconf/couchflow/save_workflow/"
    form_title = "Crear WorkFlow"
    context = {'form': form,
               'form_title': form_title,
               'form_url': form_url,
               }
    return render_to_response('webconf/couchflow/couchflow_form.html',
                              context,
                              context_instance=RequestContext(request)
                              )

@login_required
def select_item(request, workflow_id, item_type):
    workflow = WorkFlow.get(workflow_id)
    response_dict = {}
    if not workflow.item_type:
        workflow.item_type = item_type
        workflow.save()
        response_dict['response'] = True
        response_dict['status'] = "Item cargado correctamente"
        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')
    response_dict['response'] = False
    response_dict['status'] = "El formulario no es correcto"
    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')


@login_required
def wf_item(request, workflow_id=False):
    workflow = WorkFlow.get(workflow_id)
    item = workflow.get_item()
    return HttpResponseRedirect('/webconf/couchflow/edit_item/%s/' % item._id)


@login_required
def item_form(request, item_id=False):
    if item_id:
        item = WFItem.get(item_id)
        form = WFItemForm(instance=item)
        form_url = "/webconf/couchflow/save_item/%s/" % item._id
    else:
        form = WFItemForm()
        form_url = "/webconf/couchflow/save_item/"

    form_title = "Crear WorkFlow"
    context = {'form': form,
               'form_title': form_title,
               'form_url': form_url,
               'is_popup': True,
               }
    if item_id:
        context['item'] = item
    return render_to_response('webconf/couchflow/item_form.html',
                              context,
                              context_instance=RequestContext(request)
                              )


def parse_request_fields(request):
    """
    returns a dict with all fields and subfields
    from request.POST for dynamic form buildier. ex:
     u'1': {'fields': {u'default': u'',
                   u'id': u'005',
                   u'nombre': u'b',
                   u'repeat': u'true',
                   u'type': u'string'},
        'subfields': {u'0': {u'sfdefault': u'a',
                             u'sfname': u'a',
                             u'sfrepeat': u'false',
                             u'sftype': u'string'}}}}
    """
    fields = {}
    for fname, value in request.POST.iteritems():
        dashes = fname.count('_')
        if dashes == 1:
            name, key = fname.split('_')
            # its not ours
            if not key.isdigit():
                continue

            if key not in fields:
                fields[key] = {'fields': {name: value}, 'subfields': {}}
            else:
                fields[key]['fields'][name] = value

    for fname, value in request.POST.iteritems():
        dashes = fname.count('_')
        if dashes == 2:
            name, key, subkey = fname.split('_')

            # its not ours
            if not key.isdigit() or not subkey.isdigit():
                continue

            if subkey not in fields[key]['subfields']:
                fields[key]['subfields'][subkey] = {name: value}
            else:
                fields[key]['subfields'][subkey][name] = value
    return fields


@login_required
def save_item(request, item_id=False):
    response_dict = {}
    if request.method == 'POST':
        form = WFItemForm(request.POST)
        if form.is_valid():
            if not item_id:
                wf_item = form.save()
                wf_item.item_type = wf_item.name.lower().replace(" ", "_")
            else:
                wf_item = WFItem.get(item_id)
                wf_item.name = form.cleaned_data['name']
                wf_item.loanable = form.cleaned_data['loanable']
                wf_item.reference = form.cleaned_data['reference']

            fields = parse_request_fields(request)

            wf_item.fields_properties = {}

            for val in fields.values():
                val_fields = val['fields']
                field_default = val_fields['default']
                repeat = False
                if val_fields['repeat'] == "false":
                    repeat = True
                field_repeat = repeat

                field_type = val_fields['type']
                field_name = val_fields['name']
                field_id = val_fields['id']

                val_subfields = val['subfields']

                field = Field()
                for sf in val_subfields.values():
                    sub_field = SubField()
                    sub_field.field_name = sf['sfname']
                    sub_field.type = sf['sftype']
                    sub_field.description = sf['sfdesc']
                    sub_field.default_value = ''
                    repeat = False
                    if sf['sfrepeat'] == "false":
                        repeat = True
                    sub_field.repeat = repeat

                    field.subfields[sf['sfname']] = sub_field

                fields = Fields()
                fields.list.append(field)
                fields.field_name = field_name
                fields.type = field_type
                fields.id = field_id
                fields.repeat = field_repeat
                fields.default_value = field_default

                wf_item.fields_properties[field_id] = fields

            wf_item.save()

            if not item_id:
                create_default_edit_workflow(wf_item)

            response_dict['response'] = True

            response_dict['name'] = wf_item.name
            response_dict['item_type'] = wf_item.item_type
            response_dict['status'] = "Item cargado correctamente"
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')

    response_dict['response'] = False
    response_dict['status'] = "El formulario no es correcto"
    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')

def create_default_edit_workflow(item):
    """
    name is an item type name - must have spaces replaced with underscores
    """

    workflow = WorkFlow()
    workflow.workflow_type = workflow.name = "%s_editor" % item.item_type
    workflow.item_type = item.item_type
    workflow.steps = 1
    workflow.save()

    decisiontask = DecisionTask()
    decisiontask.name = 'Editar item'
    decisiontask.step = 1
    decisiontask.active = True
    decisiontask.node_type = "start"
    #decisiontask.end = True
    decisiontask.item_type = item.item_type
    decisiontask.group_by_urn = True

    for item_name in item.fields_properties:
        decisiontask.item_fields[item_name] = "write"

    decisiontask.save()

    conector = SequenceConector()
    conector.previous_tasks.append(decisiontask._id)
    conector.workflow_id = workflow._id
    conector.end = True
    conector.step = 2
    conector.save()

    first_conector = SequenceConector()
    first_conector.next_tasks.append(decisiontask._id)
    first_conector.workflow_id = workflow._id
    first_conector.start = True
    first_conector.save()
    first_conector.put_step()

    decisiontask.conector_id = conector._id
    decisiontask.workflow_id = workflow._id
    decisiontask.prev_conector_id = first_conector._id

    workflow.conectors[conector._id] = False # TODO: is this ok?
    workflow.conectors[first_conector._id] = True
    workflow.tasks[decisiontask._id] = True
    workflow.first_task_type = decisiontask.doc_type
    workflow.first_task_id = decisiontask._id

    workflow.save()
    decisiontask.save()


@login_required
def edit_conector(request, conector_id):
    form = ConectorChoiceForm(request.POST)
    response_dict = {}
    if form.is_valid():
        conector = get_conector(conector_id)
        conector_type = form.cleaned_data['conector_type']
        con_types = ['SequenceConector', 'ExclusiveChoice', 'ParallelSplit',
                     'MultipleInstances', 'UntilConector', 'SyncConector',
                     'SimpleMergeConector', 'EndConector']
        merger_types = ['SimpleMergeConector', 'SyncConector']
        spliter_types = ['ParallelSplit', 'ExclusiveChoice']
        if conector_type in con_types:
            if conector_type == "EndConector":
                conector.doc_type = "SequenceConector"
                for i in conector.next_tasks:
                    task = get_task(i)
                    if task.prev_conector_id == conector._id:
                        task.prev_conector_id = None
                        task.save()
                conector.next_tasks = []
                conector.end = True
            elif (conector.doc_type in merger_types) and\
                (conector_type not in merger_types):
                    if len(conector.previous_tasks) > 1:
                        task = get_task(conector.previous_tasks[1])
                        new_conector = SequenceConector()
                        new_conector.previous_tasks.append(task._id)
                        new_conector.name = "Conector nuevo de " + task.name
                        new_conector.save()
                        task.conector_id = new_conector._id
                        task.save()
                        conector.previous_tasks.remove(task._id)
            else:
                if (conector.doc_type == "ExclusiveChoice" or\
                    conector.doc_type == "ParallelSplit") and\
                    (conector_type != "ExclusiveChoice" and\
                     conector_type != "ParallelSplit") and\
                     len(conector.next_tasks) > 1:
                    task = get_task(conector.next_tasks[1])
                    if task.prev_conector_id == conector._id:
                        task.prev_conector_id = None
                        task.save()
                    conector.next_tasks.remove(conector.next_tasks[1])

                conector.end = False
            conector.doc_type = conector_type
            conector.save()
            response_dict['response'] = True
            response_dict['status'] = "Conector editado correctamente"
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
    response_dict['response'] = False
    response_dict['status'] = "Error al editar el Conector"
    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')


@login_required
def create_task(request, workflow_id):
    try:
        workflow = WorkFlow.get(workflow_id)
    except ResourceNotFound:
        response_dict = {}
        response_dict['response'] = False
        response_dict['status'] = "No existe el workflow"
        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')
    if request.method == 'POST':
        if request.POST['task_type'] == "DecisionTask":
            form = DecisionTaskForm(request.POST)
        elif request.POST['task_type'] == "DynamicDataTask":
            form = DynamicDataTaskForm(request.POST)
        elif request.POST['task_type'] == "ItemsLoader":
            form = WFItemsLoaderForm(request.POST)
        elif request.POST['task_type'] == "ProcessTask":
            form = ProcessTaskForm(request.POST)
        elif request.POST['task_type'] == "FilterWFItems":
            form = FilterWFItemsForm(request.POST)
        elif request.POST['task_type'] == "MarcImport":
            form = MarcImportForm(request.POST)
        elif request.POST['task_type'] == "CloneItems":
            form = CloneItemsForm(request.POST)

        if form.is_valid():
            task = form.save()
            if workflow.item_type:
                item = workflow.get_item()
                if task.doc_type == "WFItemsLoader":
                    if 'multiple' in request.POST:
                        task.multiple = True
                # TODO: why it's not visible by default
                if task.doc_type in ("MarcImport", "DecisionTask"):
                    task.visible = True

                for item_name in item.fields_properties:
                    if item_name in request.POST:
                        task.item_fields[item_name] = request.POST[item_name]
                task.item_type = workflow.item_type
            task.save()
            if 'user_owner' in request.POST:
                try:
                    user = User.get(request.POST['user_owner'])
                    task.user_id = user._id
                except ResourceNotFound:
                    task.user_id = None
            if 'group_owner' in request.POST:
                try:
                    group = Group.get(request.POST['group_owner'])
                    task.group_id = group._id
                except:
                    task.group_id = None

            conector_type = request.POST['conector_type']
            if conector_type == 'SequenceConector':
                conector = SequenceConector()
            elif conector_type == 'ExclusiveChoice':
                conector = ExclusiveChoice()
            elif conector_type == 'ParallelSplit':
                conector = ParallelSplit()
            elif conector_type == 'MultipleInstances':
                conector = MultipleInstances()
            elif conector_type == 'UntilConector':
                conector = UntilConector()
            elif conector_type == 'SyncConector':
                conector = SyncConector()
            elif conector_type == 'SimpleMergeConector':
                conector = SimpleMergeConector()
            elif conector_type == 'EndConector':
                conector = SequenceConector()
                conector.end = True
                task.end = True
                task.node_type = "end"
            else:
                response_dict = {}
                response_dict['response'] = False
                response_dict['status'] = "No existe ese tipo de conector"
                return HttpResponse(simplejson.dumps(response_dict),\
                                    mimetype='application/javascript')

            conector.name = "Conector " + task.name + " " + conector.doc_type
            conector.previous_tasks.append(task._id)
            conector.workflow_id = workflow._id
            conector.save()
            task.conector_id = conector._id
            task.workflow_id = workflow._id
            task.save()
            workflow.conectors[conector._id] = False
            workflow.tasks[task._id] = False
            if workflow.steps == 0:
                first_conector = SequenceConector()
                first_conector.next_tasks.append(task._id)
                first_conector.workflow_id = workflow._id
                first_conector.start = True
                first_conector.save()
                first_conector.put_step()
                conector.step = 2
                conector.save()
                workflow.steps = 1
                workflow.conectors[first_conector._id] = True
                workflow.tasks[task._id] = True
                task.prev_conector_id = first_conector._id
                task.step = 1
                task.active = True
                task.node_type = "start"
                task.save()
                # set firt task type in workflow document
                workflow.first_task_type = task.doc_type
                workflow.first_task_id = task._id

            workflow.save()
            response_dict = {}
            if task.doc_type == "DynamicDataTask":
                task.extra_fields = {}
                for word in request.POST:
                    if word[-8:] == "_default" and \
                           word[:-7] + "type" in request.POST:
                        word_default = request.POST[word]
                        word_type = word[:-7] + "type"
                        word_type = request.POST[word_type]
                        task.extra_fields[word[:-8]] = \
                                {"type": word_type, "exec_value": [],
                                        "default_value": word_default}
                task.save()
                if conector.doc_type == "MultipleInstances":
                    form_url = "/webconf/couchflow/multiple_instances/%s/"
                    form_url = form_url % conector._id
                    response_dict['multiple_instances'] = form_url

            response_dict['response'] = True
            response_dict['status'] = "Tarea creada correctamente"
            response_dict['task_id'] = task._id
            response_dict['conector_id'] = conector._id
            response_dict['conector_type'] = conector.doc_type
            response_dict['node_type'] = task.node_type
            response_dict['task_name'] = task.name
            response_dict['task_description'] = task.description
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')

    response_dict = {}
    response_dict['response'] = False
    response_dict['status'] = "Form no valido"
    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')


@login_required
def edit_form_task(request, task_id):
    task = get_task(task_id)
    workflow = WorkFlow.get(task.workflow_id)
    item = task.get_item()
    if task.doc_type == "DecisionTask":
        form_task = DecisionTaskForm(instance=task)
        html_file = 'webconf/couchflow/js_dec_task_form.html'
    elif task.doc_type == "DynamicDataTask":
        form_task = DynamicDataTaskForm(instance=task)
        html_file = 'webconf/couchflow/js_dyn_task_form.html'
    elif task.doc_type == "WFItemsLoader":
        form_task = WFItemsLoaderForm(instance=task)
        html_file = 'webconf/couchflow/js_item_loader_form.html'
    elif task.doc_type == "ProcessTask":
        form_task = ProcessTaskForm(instance=task)
        html_file = 'webconf/couchflow/js_process_form.html'
    elif task.doc_type == "FilterWFItems":
        form_task = FilterWFItemsForm(instance=task)
        html_file = 'webconf/couchflow/js_filteritem_form.html'
    elif task.doc_type == "MarcImport":
        form_task = MarcImportForm(instance=task)
        html_file = 'webconf/couchflow/js_item_loader_form.html'
    elif task.doc_type == "CloneItems":
        form_task = CloneItemsForm(instance=task)
        html_file = 'webconf/couchflow/js_clone_items_form.html'

    users = User.view("couchauth/all_users")
    groups = Group.view("couchauth/all_groups")
    form_url = "/webconf/couchflow/change_task/%s/" % task_id
    context = {'form': form_task,
               'form_url': form_url,
               'workflow': workflow,
               'task': task,
               'users': users,
               'groups': groups,
               'item': item,
                   }
    return render_to_response(html_file, context,
                              context_instance=RequestContext(request)
                              )


@login_required
def change_task(request, task_id):
    task = get_task(task_id)
    if request.method == 'POST':
        if request.POST['task_type'] == "DecisionTask":
            form = DecisionTaskForm(request.POST)
        elif request.POST['task_type'] == "DynamicDataTask":
            form = DynamicDataTaskForm(request.POST)
        elif request.POST['task_type'] == "ItemsLoader":
            form = WFItemsLoaderForm(request.POST)
        elif request.POST['task_type'] == "ProcessTask":
            form = ProcessTaskForm(request.POST)
        elif request.POST['task_type'] == "FilterWFItems":
            form = FilterWFItemsForm(request.POST)
        elif request.POST['task_type'] == "MarcImportForm":
            form = MarcImportForm(request.POST)
        elif request.POST['task_type'] == "CloneItems":
            form = CloneItemsForm(request.POST)

        item = task.get_item()
        for item_name in item.fields_properties:
            if item_name in request.POST:
                task.item_fields[item_name] = request.POST[item_name]

        task.item_required_fields = {}
        for field in request.POST.getlist("required"):
            task.item_required_fields[field] = True

        task.item_tema3_fields = {}
        for field in request.POST.getlist("tema3"):
            task.item_tema3_fields[field] = True

        task.save()
        if form.is_valid():
            if 'user_owner' in request.POST:
                try:
                    user = User.get(request.POST['user_owner'])
                    task.user_id = user._id
                except ResourceNotFound:
                    task.user_id = None
            if 'group_owner' in request.POST:
                try:
                    group = Group.get(request.POST['group_owner'])
                    task.group_id = group._id
                except:
                    task.group_id = None
            task.name = form.cleaned_data['name']

            if "description" in form.cleaned_data:
                task.description = form.cleaned_data['description']

            task.save()
            if task.doc_type == "DecisionTask":
                if task.name != form.cleaned_data['name']:
                    task.sentence = form.cleaned_data['name']
                    task.save()
            elif task.doc_type == "WFItemsLoader":
                if task.name != form.cleaned_data['name']:
                    task.name = form.cleaned_data['name']
                    task.name = form.cleaned_data['comments']
                    task.save()
            elif task.doc_type == "DynamicDataTask":
                task.extra_fields = {}
                for word in request.POST:
                    if word[-8:] == "_default" and \
                           word[:-7] + "type" in request.POST:
                        word_default = request.POST[word]
                        word_type = word[:-7] + "type"
                        word_type = request.POST[word_type]
                        task.extra_fields[word[:-8]] = {"type": word_type,
                                                        "exec_value": [],
                                                        "default_value": word_default}
                task.save()
            response_dict = {}
            response_dict['response'] = True
            response_dict['status'] = "Tarea editada correctamente"
            response_dict['task_id'] = task._id
            response_dict['task_name'] = task.name
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
    response_dict = {}
    response_dict['response'] = False
    response_dict['status'] = "Error de Post"
    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')


@login_required
def create_form_task(request, workflow_id):
    try:
        workflow = WorkFlow.get(workflow_id)
    except ResourceNotFound:
        return HttpResponseRedirect('/webconf/couchflow/')

    conector_form = ConectorChoiceForm()
    task_choice_form = TaskChoiceForm()
    dynamic_form = DynamicDataTaskForm()
    decision_form = DecisionTaskForm()
    marc_import_form = MarcImportForm()

    booksloader_form = WFItemsLoaderForm()

    item = workflow.get_item()
    users = User.view("couchauth/all_users")
    groups = Group.view("couchauth/all_groups")

    form_url ='/webconf/couchflow/create_task/%s/' % workflow._id
    context = {
        'conector_form': conector_form,
        'task_choice_form': task_choice_form,
        'dynamic_form': dynamic_form,
        'decision_form': decision_form,
        'marc_import_form': marc_import_form,
        'workflow': workflow,
        'groups': groups,
        'users': users,
        'item': item,
        'form_url': form_url,
        }

    if workflow.item_type:
        items = WFItem.view("couchflow/item_names", include_docs=True)
        item = items[workflow.item_type]
        item = item.one()
        context['item'] = item

    return render_to_response('webconf/couchflow/full_task_form.html',
                              context,
                              context_instance=RequestContext(request)
                              )

@login_required
def edit_form_conector(request, conector_id):
    form = ConectorChoiceForm()
    form_url = '/webconf/couchflow/edit_conector/%s/' % conector_id
    context = {
        'form': form,
        'form_url': form_url,
        }
    return render_to_response('webconf/couchflow/edit_form_conector.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
def task_pos(request, task_id, pos_x, pos_y):
    task = get_task(task_id)
    task.position['x'] = float(pos_x)
    task.position['y'] = float(pos_y)
    task.save()
    response_dict = {}
    response_dict['response'] =True
    response_dict['status'] = "Changed"
    return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')


@login_required
def new_task(request, workflow_id, conector_id=False):
    try:
        workflow = WorkFlow.get(workflow_id)
    except ResourceNotFound:
        return HttpResponseRedirect('/webconf/couchflow/')
    check_form = TaskChoiceForm(request.POST)
    if check_form.is_valid():
        if check_form.cleaned_data['task_type'] == "DynamicDataTask":
            form = DynamicDataTaskForm()
            task_type = "DynamicDataTask"
            html_file = 'webconf/couchflow/dynamic_task_form.html'
        else:
            form = DecisionTaskForm()
            task_type = "DecisionTask"
            html_file = 'webconf/couchflow/task_form.html'
        form_url = "/webconf/couchflow/save_task/%s/%s/"
        form_url = form_url % (workflow_id, conector_id)
        users = User.view("couchauth/all_users")
        groups = Group.view("couchauth/all_groups")

        form_title = "Nueva Tarea"
        context = {'form': form,
                   'form_title': form_title,
                   'form_url': form_url,
                   'task_type': task_type,
                   'conector_id': conector_id,
                   'workflow': workflow,
                   'groups': groups,
                   'users': users,
                   }
        return render_to_response(html_file,
                                  context,
                                  context_instance=RequestContext(request)
                                  )
    url_redirect = '/webconf/couchflow/select_new_task/%s/%s/'
    url_redirect = url_redirect % (workflow_id, conector_id)
    return HttpResponseRedirect(url_redirect)


@login_required
def show_task(request, task_id):
    task = get_task(task_id)
    if task:
        try:
            workflow = WorkFlow.get(task.workflow_id)
        except ResourceNotFound:
            return HttpResponseRedirect('/webconf/couchflow/')

        if task.doc_type == "DynamicDataTask":
            form = DynamicDataTaskForm(instance=task)
            html_file = 'webconf/couchflow/dynamic_task_form.html'
        elif task.doc_type == "DecisionTask":
            form = DecisionTaskForm(instance=task)
            html_file = 'webconf/couchflow/task_form.html'

        users = User.view("couchauth/all_users")
        groups = Group.view("couchauth/all_groups")
        form_url = "/webconf/couchflow/save_task/%s/" % task_id
        form_title = "Tarea: " + task.name
        context = {'form': form,
                   'workflow': workflow,
                   'form_title': form_title,
                   'form_url': form_url,
                   'task_type': task.doc_type,
                   'task': task,
                   'users': users,
                   'groups': groups,
                   }
        return render_to_response(html_file, context,
                                  context_instance=RequestContext(request)
                                  )


@login_required
def save_task(request, workflow_id=False, conector_id=False, task_id=False):
    if request.method == 'POST':
        if request.POST['task_type'] == "DecisionTask":
            form = DecisionTaskForm(request.POST)
        elif request.POST['task_type'] == "DynamicDataTask":
            form = DynamicDataTaskForm(request.POST)
        elif request.POST['task_type'] == "CloneItems":
            form = CloneItemsForm(request.POST)
        if form.is_valid():
            if not task_id:
                task = form.save()
                task.save()
            else:
                try:
                    task = Task.get(task_id)
                except ResourceNotFound:
                    return HttpResponseRedirect('/webconf/couchflow/')
                task.name = form.cleaned_data['name']
                #task.sentence = form.cleaned_data['sentence']

            if 'user_owner' in request.POST:
                try:
                    user = User.get(request.POST['user_owner'])
                except:
                    user = False
                if user:
                    task.user_id = user._id
                else:
                    task.user_id = None

            if 'group_owner' in request.POST:
                try:
                    group = Group.get(request.POST['group_owner'])
                except:
                    group = False
                if group:
                    task.group_id = group._id
                else:
                    task.group_id = None

            task.save()
            if task_id:
                url_redirect = '/webconf/couchflow/show_workflow/%s/'
                url_redirect = url_redirect % task.workflow_id
                return HttpResponseRedirect(url_redirect)

            if task.doc_type == "DynamicDataTask":
                for word in request.POST:
                    if word[-8:] == "_default" and \
                           word[:-7] + "type" in request.POST:
                        word_default = request.POST[word]
                        word_type = word[:-7] + "type"
                        word_type = request.POST[word_type]
                        task.extra_fields[word[:-8]] = {"type": word_type,
                                                        "exec_value": [],
                                                        "default_value": word_default}
                task.save()
            if workflow_id:
                try:
                    workflow = WorkFlow.get(workflow_id)
                except ResourceNotFound:
                    return HttpResponseRedirect('/webconf/couchflow/')
                task.workflow_id = workflow._id
                task.save()

            conector = None
            if conector_id:
                conector = get_conector(conector_id)

            if not conector:
                url_redirect = '/webconf/couchflow/show_workflow/%s/'
                url_redirect = url_redirect % workflow_id
                return HttpResponseRedirect(url_redirect)

            conector.add_next_task(task)
            #conector.save()
            task.put_step()
            if not conector.previous_tasks:
                conector.to_next_tasks()
            workflow.add_task(task)
            if conector.doc_type == "ExclusiveChoice"  or \
                   conector.doc_type == "ParallelSplit":
                if len(conector.next_tasks) < 2:
                    url_redirect = '/webconf/couchflow/new_task/%s/%s/'
                    url_redirect = url_redirect % (workflow._id, conector._id)
                    return HttpResponseRedirect(url_redirect)
            if conector.doc_type == "UntilConector" and \
               len(conector.next_tasks) <2:
                url_redirect = "/webconf/couchflow/backto_until/%s"
                url_redirect = url_redirect % conector._id
                return HttpResponseRedirect(url_redirect)
    url_redirect = '/webconf/couchflow/show_workflow/%s/' % workflow_id
    return HttpResponseRedirect(url_redirect)


@login_required
def delete_workflow(request, workflow_id):
    try:
        workflow = WorkFlow.get(workflow_id)
    except ResourceNotFound:
        return HttpResponseRedirect('/webconf/couchflow/')
    if workflow:
        workflow.remove_relations()
        workflow.delete()
    return HttpResponseRedirect('/webconf/couchflow/')


@login_required
def show_workflow(request, workflow_id):
    try:
        workflow = WorkFlow.get(workflow_id)
    except ResourceNotFound:
        return HttpResponseRedirect('/webconf/couchflow/')

    if workflow:
        form = WorkFlowForm(instance=workflow)
        form_url = "/webconf/couchflow/save_workflow/%s/" % workflow_id
        form_title = "WorkFlow: " + workflow.name
        context = {'form': form,
                   'workflow': workflow,
                   'form_title': form_title,
                   'form_url': form_url,
                   }

        nodes = {}
        register = ''

        # TODO: this suck!
        try:
            wf_list = workflow.get_docs()
        except Exception:
            wf_list = []

        for n in wf_list:
            if hasattr(n, 'conector_type'):
                if not n.previous_tasks:
                    continue

                register += 'var narrow = jQuery.extend(true, {}, arrow);'
                register += 'narrow["attrs"]["id"] = "%s";\n' % n.get_id
                register += 'narrow["attrs"]["type"] = "connector";\n'

                if len(n.previous_tasks) > 1:
                    prev_ids = ['node_%s' % k for k in  n.previous_tasks]
                    past_id = 'node_%s' % n.next_tasks[0]

                    for prev_id in prev_ids:
                        register += '%s.joint(%s, narrow).'\
                                'registerForever(all);\n' %  (prev_id, past_id)
                else:
                    next_ids = ['node_%s' % k for k in  n.next_tasks]
                    past_id = 'node_%s' % n.previous_tasks[0]


                    if not next_ids:
                        counter = 1
                        if n.doc_type in ('ExclusiveChoice', 'ParallelSplit',
                                                             'UntilConector'):
                            counter = 2
                        elif n.end:
                            counter = 0
                        for i in xrange(1, counter+1):
                            x, y = 60+i*2, -60+i*40
                            register += 'var x = %s.wrapper["attrs"]'\
                                          '["x"]+%s;\n' % (past_id, x)
                            register += 'var y = %s.wrapper["attrs"]'\
                                          '["y"]+%s;\n' % (past_id, y)
                            register += '%s.joint({x:x, y:y}, narrow).'\
                               'registerForever(all);\n' % (past_id)
                    for next_id in next_ids:
                        if n.doc_type in ('ExclusiveChoice', 'ParallelSplit'
                                          'UntilConector') and len(next_ids)<2:
                            register += 'var x = %s.wrapper["attrs"]'\
                                              '["x"]+60;\n'% (past_id)
                            register += 'var y = %s.wrapper["attrs"]'\
                                              '["y"]-10;\n'% (past_id)
                            register += '%s.joint({x:x, y:y}, narrow).'\
                                'registerForever(all);\n' % (past_id)

                        register += '%s.joint(%s, narrow).'\
                                'registerForever(all);\n' % (past_id, next_id)

            else:

                # First Node

                fill = 'white'
                stroke = 'black'
                if  n.node_type == 'start':
                    stroke = 'red'
                elif n.node_type == 'end':
                    stroke = 'blue'

                node_id = 'node_%s' % n.get_id

                node = '''%s=ngw.Node.create({
                      id: "%s",
                      rect: { x: %s, y: %s, width: 200, height: 80 },
                      title: "%s",
                      description: "%s",
                      data: {type: "node", id: "%s", node_type: "%s"},
                      attrs: {
                        stroke: "%s",
                        fill: "%s"
                      }
                   });''' % (node_id, n.get_id, n.position["x"],
                                      n.position["y"],
                                      n.name or "State", (n.description or '').replace("\n", " ") or "",
                                      n.get_id, n.node_type, stroke, fill)
                nodes[node_id] = node

        # TODO: this should be encoded properly
        context['nodes'] = '\n'.join(nodes.values())
        context['nodes'] += '\nall = %s;\n' % str(
                    [str(key) for key in nodes.keys()]).replace("'", '')

        # Arrow
        context['register'] = '''\narrow = {
                startArrow: {type: "none"},
                endArrow: {type: "basic", size: 7},
                attrs: {"stroke-dasharray": "none"},
                data: {}
               };\n'''
        context['register'] += register

        return render_to_response('webconf/couchflow/couchflow_form.html',
                                  context,
                                  context_instance=RequestContext(request)
                                  )


@login_required
def save_workflow(request, workflow_id=False):
    if request.method == 'POST':
        form = WorkFlowForm(request.POST)
        if form.is_valid():
            if not workflow_id:
                workflow = WorkFlow()
            else:
                try:
                    workflow = WorkFlow.get(workflow_id)
                except ResourceNotFound:
                    return HttpResponseRedirect('/webconf/couchflow/')

            workflow.name = form.cleaned_data['name']
            if not workflow_id:
                wf_name = workflow.name.lower().replace(" ", "_")
                workflow.workflow_type = wf_name
            workflow.save()
            url_redirect = '/webconf/couchflow/show_workflow/%s/'
            url_redirect = url_redirect % workflow._id
            return HttpResponseRedirect(url_redirect)
    return HttpResponseRedirect('/webconf/couchflow/')


# TODO: perhaps we could split this to a different app?
@login_required
def menueditor_index(request):
    context = {
        'workflows': WorkFlow.view("couchflow/orig_workflows", include_docs=True),
        'groups': Group.view("couchauth/all_groups")
    }
    return render_to_response('webconf/couchflow/menueditor.html', context,
                              context_instance=RequestContext(request))


@login_required
def menueditor_get_data(request):
    doc = Config.get_or_create("menu")
    return HttpResponse(simplejson.dumps(doc.values.get('menu', {})),
                                mimetype='application/javascript')

@login_required
@csrf_exempt
def menueditor_save(request):
    if request.method == 'POST':
        doc = Config.get_or_create("menu")
        try:
            doc.values['menu'] = simplejson.loads(request.POST['json'])
        except ValueError:
            return HttpResponse("parse error")
        else:
            generate_menu(doc.values['menu'])
        doc.save()
        return HttpResponse("ok")
    return HttpResponse("error")


def generate_menu(menudata):
    # settings.TEMPLATE_DIRS[0] should be a directory like dyntemplates
    template_path = settings.TEMPLATE_DIRS[0]
    menubar = open(os.path.join(template_path, "menubar.html"), "w")
    menujs = open(os.path.join(template_path, "menujs.html"), "w")
    menudivs = open(os.path.join(template_path, "menudivs.html"), "w")

    def group_if(cat):
        groups = cat.get('metadata', {}).get('groups', [])
        if not groups:
            return ('', '')
        else:
            groupchecks = ["'%s' in user.groups" % x for x in groups]
            groupchecks.append("user.is_superuser")
            return ("{%% if %s %%}\n" % (' or '.join(groupchecks)),
                    "{% endif %}\n")

    def get_target_data(item, default_target='#'):
        target = item.get('metadata', {}).get('target', '').encode("utf-8",
            "ignore") or default_target
        data = item.get('data', '').encode("utf-8", "ignore")
        return (target, data)

    ids_map = {}
    for i, cat in enumerate(menudata):
        group_if_open, group_if_close = group_if(cat)
        target, data = get_target_data(cat, '#menu%s' % i)

        menubar.write(group_if_open)
        menubar.write('<li><a id="menulink%s" href="%s">%s</a></li>\n'
            % (i, target, data))
        menubar.write(group_if_close)

        if 'children' in cat:
            menujs.write("$('#menulink%s').fgmenu({content:$('#menu%s')"
                ".html(), flyOut: true});\n" % (i, i))
            ids_map["menu%s" % i] = cat['children']

    def generate_ul(children):
        menudivs.write('<ul>\n')
        for li in children:
            group_if_open, group_if_close = group_if(li)
            target, data = get_target_data(li)

            menudivs.write(group_if_open)
            menudivs.write('<li><a href="%s">%s</a>\n'
                % (target, data))
            if 'children' in li:
                generate_ul(li['children'])
            menudivs.write('</li>\n')
            menudivs.write(group_if_close)
        menudivs.write('</ul>\n')

    for div, children in ids_map.iteritems():
        menudivs.write('<div id="%s" class="hidden">\n' % div)
        generate_ul(children)
        menudivs.write('</div>\n\n')
    menudivs.close()
    menujs.close()
    menubar.close()


@login_required
def edit_task_html(request, task_id):
    task = get_task(task_id)
    if request.method == 'POST' and 'editor' in request.POST:
        task.html_tpl = request.POST['editor']
        task.save()

    context = {
        'task': task,
    }
    return render_to_response("webconf/couchflow/edit_task_html.html",
        context, context_instance=RequestContext(request))

@login_required
def clear_task_html(request):
    if request.method == 'POST' and 'task_id' in request.POST:
        task_id = request.POST['task_id']
        task = get_task(task_id)
        task.html_tpl = ""
        task.save()

        redir_url = "/webconf/couchflow/edit_task_html/%s/" % task_id
        return HttpResponseRedirect(redir_url)

    return HttpResponseForbidden()
