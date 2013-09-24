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
from django.http import HttpResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from couchdbkit import ResourceConflict
from couchdbkit.resource import ResourceNotFound
from couchdbkit.ext.django.loading import get_db

from models import WorkFlow, Task
from models import get_task, MarcImport
from models import WFItem, FilterWFItems
from models import DecisionTask, DynamicDataTask, WFItemsLoader
from models import Config

from forms import DecisionTaskForm
from forms import ExecMarcImportForm
from forms import ExecWFItemForm, FilterWFItemsForm, ExecWFItemsLoader
from forms import ExecDecisionForm, ExecDynamicForm,  ExecFilterWFItemsForm

from webconf import clone_this_wf
from gplib.apps.webconf.views import check_perms
from gplib import settings

import pymarc

try:
    import barcode
    import barcode.writer
    from barcode.writer import mm2px
except ImportError:
    barcode = None

from cStringIO import StringIO

from utils import get_field, parse_wysiwyg_fields

import time, os

# Private
def get_item_name(item):
    """
    Returns an item name based on title
    """

    item_name = item.get_field("245", "a")
    if not item_name:
        item_name = item.get_field("700", "a")
        if not item_name:
            return "Item"
    return item_name


def save_images(item, images):
    for image in images:
        # XXX: some errors with django memory file =/
        item.put_attachment(image.read(), image.name,
                                  image.content_type)

# TODO: add support to more than one field
def save_task_item(request, item, task):
    '''
    get field and subfield data from the request and save to an item
    '''

    greenstone_conf = Config.get_or_create("greenstone")

    fields_images = []
    for key, field, value, sfields, tema3 in task.write_item_fields():
        id = field['id']

        fields = item.fields_properties[id]
        if fields['type'] == 'int':
            field_value = [int(i) for i in request.POST.getlist(id)]
        elif fields['type'] == 'image':
            #TODO: validate type of file
            images = [i for i in request.FILES.getlist(id)]
            fields_images += images

            field_value = [i.name for i in request.FILES.getlist(id)]
        elif fields['type'] == 'greenstone':
            template = greenstone_conf.values['template']
            expanded_template = template
            tags = {
                '%item_type%': item.item_type,
                '%date%': time.strftime("%Y-%m-%d"),
                '%urn%': item.urn,
            }
            for key, value in tags.iteritems():
                expanded_template = expanded_template.replace(key, value)

            full_path = os.path.join(greenstone_conf.values['upload_path'],
                expanded_template)

            if expanded_template.count("/"):
                try:
                    os.makedirs(os.path.dirname(full_path))
                except OSError:
                    # includes errno.EEXIST
                    pass

            with open(full_path, 'wb') as fp:
                for chunk in request.FILES[id].chunks():
                    fp.write(chunk)

            field_value = expanded_template
        else:
            field_value = request.POST.getlist(id)

        fields.first['exec_value'] = field_value

        for i in [1, 2]:
            attrname = "indicator%s" % i
            value = request.POST.get("%s_%s" % (id, attrname), '')
            fields.first[attrname] = value

        if sfields:
            for sf, value in sfields:
                sfs_data = request.POST.getlist(
                        'sf_'+id+'_'+sf['field_name'])

                try:
                    fields.first['subfields']\
                        [sf['field_name']]['exec_value'] = sfs_data
                except KeyError:
                    pass

    for field in request.POST.getlist("reference_input"):
        fid, sfid, _, value = simplejson.loads(field)
        fields = item.fields_properties[fid]
        if not sfid:
            fields.first['exec_value'] = value
        else:
            fields.first['subfields'][sfid]['exec_value'] = value

    return fields_images


# Public

@login_required
def get_attach(request, db_name, document_id, name):
    """
    returns a file from couchdb
    """
    # TODO: move out of couchflow to somewhere more generic
    try:
        db = get_db(db_name)
        response = db.fetch_attachment(document_id, name, stream=True)
        mimetype = response.resp.headers.get('Content-Type')
    except (KeyError, ResourceNotFound):
        _path = settings.MEDIA_ROOT + '/images/book.jpg'
        response = open(_path)
        mimetype = "image/jpeg"
    return HttpResponse(response, mimetype=mimetype)



@login_required
def export_mrc(request, doc_id):
    item = WFItem.get(doc_id)
    if not item:
        return HttpResponseNotFound()

    data = item.marc_record().as_marc21()
    mimetype = "text/mrc"

    response = HttpResponse(data, mimetype=mimetype)
    response['Content-Disposition'] = 'attachment; filename=record.mrc'
    return response

@login_required
def import_mrc(request, task_id):
    task = get_task(task_id)
    if task.doc_type != 'MarcImport':
        return HttpResponse('False')

    item = task.get_item()
    file_var =  request.FILES['userfile']

    for rec in pymarc.MARCReader(file_var):
        for field in rec.get_fields():
            field_id = field.tag
            subfields = {}
            exec_value = None
            if hasattr(field, 'subfields'):
                # iter over pairs of subfields list
                for sf_name, sf_value in zip(*[iter(field.subfields)]*2):
                    # only import subfields in field
                    try:
                        print field_id, field_id in item.fields_properties
                        ifield = item.fields_properties[field_id].first
                        print sf_name, sf_name in ifield['subfields']
                        # TODO: wtf?
                        ifield['subfields'][sf_name]
                    # TODO: better error handling
                    except Exception, error:
                        print "EE", error
                        continue

                    ifield['subfields'][sf_name]['exec_value'] = [sf_value]

            else:
                exec_value = field.format_field()

            if field_id in item.fields_properties and \
                    'write' == task.item_fields.get(field_id):
                ifield = item.fields_properties[field_id].first
                if exec_value:
                    ifield['exec_value'] = [exec_value]

                if getattr(field, 'indicators', None):
                    ifield.indicator1, ifield.indicator2 = field.indicators

    item.save()
    return HttpResponse('True')

@login_required
def search_references(request, task_id=None):
    items = [(item._id, item.name) for item in
        WFItem.view("couchflow/items", include_docs=True) if item.reference]

    context = {'items': items}

    if not task_id:
        tpl = 'couchflow/search_reference.html'
    else:
        task = Task.get(task_id)
        task_item = task.get_item()
        context['task_item'] = task_item.get_id
        if not task_item.is_clone:
            context['client_side_changes'] = True

        tpl = 'couchflow/search.html'

    return render_to_response(tpl, context,
            context_instance=RequestContext(request))

@login_required
def use_reference(request, item_id, reference_id, client_side_changes=None):
    reference = WFItem.get(reference_id)

    data = {'success': True}

    bad_references = []

    changes = []
    for _id, field in reference.fields_properties.iteritems():
        if int(_id) > 999:
            continue

        first = field.list[0]
        if first.subfields:
            for sub_id, subfield in first.subfields.iteritems():
                if subfield.exec_value:
                    name = "%s / %s" % (field.field_name, subfield.description)
                    changes.append((_id, sub_id, name, subfield.exec_value))
        else:
            if first.exec_value:
               changes.append((_id, None, field.field_name,
                   first.exec_value))

    item = WFItem.get(item_id)
    item.fields_properties[_id] = field

    for _id, sub_id, name, values in changes:

        if _id not in item.fields_properties.keys():
            print "bad ref", _id
            bad_references.append(_id)
            continue

        first = item.fields_properties[_id].list[0]
        if sub_id:
            if sub_id not in first.subfields:
                print "bad ref sub", _id, sub_id
                bad_references.append("%s_%s" % (_id, sub_id))
                continue

            if client_side_changes is None:
                first.subfields[sub_id].exec_value = values
        else:
            if client_side_changes is None:
                try:
                    first.exec_value = values
                except Exception, error:
                    print "Error cant insert"
                    print values, "in"
                    print first

    if bad_references:
        data['success'] = False
        data['message'] = 'Bad References'
        data['data'] = bad_references
    elif client_side_changes is None:
        item.save()
        data['message'] = 'item updated'
    else:
        data['message'] = 'ok'
        data['data'] = changes

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def get_nro_pedido():
    nro_pedido = Task.view('couchflow/max_pedido', limit=1, descending=True)
    nro_pedido = nro_pedido.one()
    if not nro_pedido:
        nro_pedido = 41
    else:
        nro_pedido = int(nro_pedido['key'])

    nro_pedido += 1
    return nro_pedido


@login_required
def exec_url(request, url_name):
    workflow = WorkFlow.view("couchflow/orig_workflows",
        include_docs=True)[url_name].one()

    if not workflow:
        return HttpResponseNotFound()

    workflow = clone_this_wf(workflow._id, request.user._id)

    workflow.nro_pedido = get_nro_pedido()
    workflow.set_enabled()
    try:
        workflow.save()
    except ResourceConflict:
        pass
    task = Task.view("couchflow/activetask",
        include_docs=True)[workflow._id].one()

    return HttpResponseRedirect("/couchflow/execute_task/%s/" % task._id)

@login_required
def edit_item(request, item_id, existence=False):
    item = WFItem.get(item_id)
    if not item:
        return HttpResponseNotFound()

    wf_name = "%s_editor" % item.item_type
    if existence:
        wf_name = "%s_editor_existencia" % item.item_type

    workflow = WorkFlow.view("couchflow/orig_workflows",
        include_docs=True)[wf_name].one()

    if not workflow:
        return HttpResponseNotFound()
    workflow = clone_this_wf(workflow._id, request.user._id)

    workflow.nro_pedido = get_nro_pedido()
    workflow.visible = False
    workflow.set_enabled()
    try:
        workflow.save()
    except ResourceConflict:
        pass

    task = Task.view("couchflow/activetask",
        include_docs=True)[workflow._id].one()
    if not existence:
        task.wfitems_ids = [item_id]
    else:
        task.base_item = item_id
    task.visible = False
    task.save()

    return HttpResponseRedirect("/couchflow/execute_task/%s/" % task._id)

@login_required
def clone_edit_item(request, item_id):
    item = WFItem.get(item_id)
    if not item:
        return HttpResponseNotFound()

    #clone = item.really_clone(save=True)
    #return edit_item(request, clone._id, True)
    return edit_item(request, item_id, True)


@login_required
def bulk_tasks(request):
    if 'aceptar' not in request.POST and \
       'rechazar' not in request.POST:
        return HttpResponseRedirect("/")
    if 'aceptar' in request.POST:
        confirmation = True
    else:
        confirmation = False
    for i in request.POST:
        if i[:5] == 'task_':
            task_id = i.split('_')[1]
            task = get_task(task_id)
            if task.doc_type == 'DecisionTask':
                task.confirmation = confirmation
                task.save()
                task.active_conector()
    return HttpResponseRedirect("/")

@login_required
def back_top(request, task_id):
    task = get_task(task_id)
    if not task:
        return HttpResponseRedirect('/')
    task_tree = task.back_to_top()
    data = []
    for i in task_tree:
        data.append(i.to_json())
    return HttpResponse(data, mimetype='application/json')


@csrf_exempt
@login_required
def get_items(request, task_id):
    return_dict = {'status': 'Error'}
    task = get_task(task_id)
    if task.doc_type == "FilterWFItems":
        start = int(request.POST['iDisplayStart'])
        end = int(request.POST['iDisplayLength'])
        secho = int(request.POST['sEcho'])+1

        #sort_col = int(request.POST['iSortCol_0'])
        #sort_dir = request.POST['sSortDir_0']

        limit = end - start

        orig_items = WFItem.view("couchflow/item_names", include_docs=True)
        orig_item = orig_items[task.item_type]
        orig_item = orig_item.one()

        opts = {'include_docs': True}
        if start:
            opts['skip'] = start
        if limit:
            opts['limit'] = limit

        filter_items = WFItem.view('couchflow/filter_items',**opts)
        val = task.item_fields['99989']
        items_query = filter_items[val]

        count = WFItem.view('couchflow/filter_items')
        count = count[val]
        count = len(count)

        query_list = []

        for i in items_query:
            for orig_value in orig_item.fields_properties:
                if orig_value not in i.fields_properties:
                    i.fields_properties[orig_value] = \
                            orig_item.fields_properties[orig_value]
            i.save()
            blits = [field.first['exec_value'][0] \
                    for field in i.fields_properties.values()]
            blits.insert(0, i._id)

            query_list.append(blits)

        return_dict = {"sEcho": secho, "iTotalRecords": count,
                       "iTotalDisplayRecords": count,
                       "aaData": query_list,}
    return HttpResponse(simplejson.dumps(return_dict),\
                        mimetype='application/javascript')


@login_required
def save_new_item(request, task_id, edit_item_id=None):
    # if edit_item_id is provided, edit it

    response_dict = {}
    if request.method == 'POST':
        task = get_task(task_id)
        workflow = WorkFlow.get(task.workflow_id)

        if edit_item_id:
            item = WFItem.get(edit_item_id)
        else:
            item = task.get_item()

        item_validation_errors = item.check_form(request.POST, task)
        for err in item_validation_errors:
            if err[1] == "int":
                err[1] = "Numero"
        if item_validation_errors:
            response_dict = {}
            response_dict['response'] = False
            status = "No se puede crear el item, campos mal cargados"
            response_dict['status'] = status
            response_dict['errors'] = item_validation_errors
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')

        # TODO: set uid by hand
        # Clone the item
        if not edit_item_id:
            item = item.really_clone(save=True)
            item.is_clone = True

        # set no the item the order number to can keep track of an order
        order_nbr = task.order_nbr
        if not order_nbr:
            order_nbr = task.order_nbr = get_nro_pedido()
        item.order_nbr = order_nbr

        images = save_task_item(request, item, task)
        item.save()

        #response_dict['item_name'] = item.name + ": " + get_item_name(item)
        response_dict['item_name'] = get_item_name(item)

        save_images(item, images)

        if not edit_item_id:
            task.wfitems_ids.append(item._id)
            task.save()

        response_dict['response'] = True
        response_dict['status'] = "Bien"
        response_dict['item_id'] = item._id

        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')

    response_dict['response'] = False
    response_dict['status'] = "Mal"
    return HttpResponse(simplejson.dumps(response_dict),\
                        mimetype='application/javascript')


@login_required
def del_item(request, item_id, task_id):
    response_dict = {}
    item = WFItem.get(item_id)
    task = get_task(task_id)
    if item and task:
        if item_id in task.wfitems_ids:
            task.wfitems_ids.remove(item_id)
            item.delete()
            task.save()
            response_dict['response'] = True
            response_dict['status'] = "Item borrado correctamente"
        else:
            response_dict['response'] = False
            response_dict['status'] = "El item no existe en la tarea"
        return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
    response_dict['response'] = False
    response_dict['status'] = "El item o la tarea no existen"
    return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')


@login_required
def item_create(request, task_id):
    task = get_task(task_id)
    workflow = WorkFlow.get(task.workflow_id)
    form = ExecWFItemForm()

    item_t = task.get_item()
    item = workflow.get_item()

    new_item = True
    form_url = '/couchflow/save_new_item/%s/' % task._id
    context = {'workflow': workflow,
               'task': task,
               'item': item,
               'form': form,
               'new_item': new_item,
               'form_url': form_url,
               'is_popup': True,
               }

    if task.html_tpl:
        context["html_tpl"] = parse_wysiwyg_fields(task)

    return render_to_response('couchflow/item_form.html',
                              context,
                              context_instance=RequestContext(request)
                                  )

@login_required
def item_created_edit(request, task_id, item_id):
    task = get_task(task_id)
    task.wfitems_ids = [item_id]
    item = task.get_item()

    form = ExecWFItemForm()

    form_url = '/couchflow/edit_new_item/%s/%s/' % (task._id, item_id)
    context = {
        'task': task,
        'item': item,
        'form': form,
        'form_url': form_url,
        'is_popup': True,
    }

    if task.html_tpl:
        context["html_tpl"] = parse_wysiwyg_fields(task)

    return render_to_response('couchflow/item_form.html',
        context, context_instance=RequestContext(request))

@login_required
def execute_task(request, task_id):
    task = get_task(task_id)

    html_file = 'couchflow/task.html'
    if not task or not task.active:
        return HttpResponseRedirect('/')

    if task.doc_type == "DecisionTask":
        form = ExecDecisionForm(instance=task)
    elif task.doc_type == "DynamicDataTask":
        form = ExecDynamicForm(instance=task)
        form.add_dynamic_fields(task)
    elif task.doc_type == "WFItemsLoader":
        form = ExecWFItemsLoader(instance=task)
        html_file = 'couchflow/items_loader.html'
    elif task.doc_type == "FilterWFItems":
        form = FilterWFItemsForm(instance=task)
        html_file = 'couchflow/filter_items.html'
        filter_url = "/couchflow/get_items/%s/" % task._id
    elif task.doc_type == "MarcImport":
        form = ExecMarcImportForm(instance=task)
        html_file = 'couchflow/marcimport_form.html'

    form_url = "/couchflow/save_task/%s/%s/"
    form_url = form_url % (task.doc_type, task._id)
    workflow = WorkFlow.get(task.workflow_id)
    item = task.get_item()
    context = {'workflow': workflow,
               'task': task,
               'form': form,
               'form_url': form_url,
               'item': item,
               }

    if task.html_tpl:
        context["html_tpl"] = parse_wysiwyg_fields(task)

    #import IPython
    #embedshell = IPython.Shell.IPShellEmbed(argv=[])
    #embedshell()

    if task.doc_type == 'FilterWFItems':
        context['filter_url'] = filter_url

    return render_to_response(html_file,
                              context,
                              context_instance=RequestContext(request)
                                  )

@login_required
def validate_task(request, task_id):
    if request.method == 'POST':
        task = Task.get(task_id)
        workflow = WorkFlow.get(task.workflow_id)
        item = task.get_item()

        item_validation_errors = item.check_form(request.POST, task)

        for err in item_validation_errors:
            if err[1] == "int":
                err[1] = "Numero"
        response_dict = {}
        response_dict['response'] = (len(item_validation_errors) == 0)
        response_dict['errors'] = item_validation_errors

        return HttpResponse(simplejson.dumps(response_dict),
            mimetype='application/javascript')
    return HttpResponseNotFound()

@login_required
def save_task(request, task_type, task_id):
    try:
        if task_type == "DecisionTask":
            task = DecisionTask.get(task_id)
            form = DecisionTaskForm(request.POST)
        elif task_type == "DynamicDataTask":
            task = DynamicDataTask.get(task_id)
            form = ExecDynamicForm(request.POST)
        elif task_type == "WFItemsLoader":
            task = WFItemsLoader.get(task_id)
            form = ExecWFItemsLoader(request.POST)
        elif task_type == "FilterWFItems":
            task = FilterWFItems.get(task_id)
            form = ExecFilterWFItemsForm(request.POST)
        elif task_type == "MarcImport":
            task = MarcImport.get(task_id)
            form = ExecMarcImportForm(request.POST)
    except ResourceNotFound:
        return  HttpResponseRedirect('/')

    workflow = WorkFlow.get(task.workflow_id)

    if 'cancelar' in request.POST and \
           task.doc_type != 'FilterWFItems':
        if task.node_type == 'start':
            workflow.remove_relations()
            workflow.delete()
        return HttpResponseRedirect('/')

    elif 'cancelar' in request.POST and \
             task.doc_type == 'FilterWFItems':
        response_dict = {}
        response_dict['response'] = False
        response_dict['url'] = '/'
        return HttpResponse(simplejson.dumps(response_dict),\
                            mimetype='application/javascript')

    item = task.get_item()
    response_dict = {}

    item_validation_errors = []
    if task_type not in ('WFItemsLoader',):
        item_validation_errors = item.check_form(request.POST, task)

    if form.is_valid() and not item_validation_errors:
        user = request.user

        task.saved_by = user._id

        if item.is_clone:
            item.comments = form.cleaned_data['comments']
            item.save()

        if task.doc_type == "DecisionTask" or \
                task.doc_type == "DynamicDataTask":
            if item.is_clone:

                images = save_task_item(request, item, task)
                item.save()

                save_images(item, images)

                more_items = []
                if len(task.wfitems_ids) > 1:
                    more_items = [WFItem.get(x) for x in task.wfitems_ids]
                elif task.group_by_urn:
                    more_items = WFItem.view("couchflow/by_urn",
                        include_docs=True)[item.urn].all()

                if more_items:
                    for new_item in more_items:
                        if new_item._id != item._id:
                            # TODO: don't replace all the properties
                            new_item.fields_properties = item.fields_properties

                            new_item.comments = item.comments
                            try:
                                new_item.save()
                            except ResourceConflict:
                                pass

        if task.doc_type == "DynamicDataTask":
            for field in task.extra_fields:
                field_data = request.POST.getlist(field)
                if field_data == "":
                    field_data = None
                task.extra_fields[field]['exec_value'] = field_data
            task.save()
            task.active_conector()
            try:
                task.save()
            except ResourceConflict:
                pass
        elif task.doc_type == "WFItemsLoader":
            task.save()
            task.active_conector()
        elif task.doc_type == "DecisionTask":
            if  'aceptar' in request.POST:
                task.confirmation = True
            else:
                task.confirmation = False
            task.save()
            task.active_conector()

        elif task.doc_type == "FilterWFItems":
            selected_items = request.POST.getlist('selected_items')
            task.wfitems_ids = selected_items
            task.save()
            task.active_conector()
            response_dict['response'] = True
            return HttpResponse(simplejson.dumps(response_dict),\
                                mimetype='application/javascript')
        elif task.doc_type == "MarcImport":
            task.active_conector()

        groups = user.groups
        new_tasks = workflow.get_active_tasks()

        url_redirect = '/'
        for task in new_tasks:
            if task.group_id in groups or user.is_superuser:
                url_redirect = '/couchflow/execute_task/%s' % task._id
                break

        return  HttpResponseRedirect(url_redirect)

    if task.doc_type == 'FilterWFItems':
        response_dict['response'] = True
        response_dict['status'] = "Campos mal cargados"
        return HttpResponse(simplejson.dumps(response_dict),
                            mimetype='application/javascript')
    else:
        context = {
            'form': form,
            'task': task,
            'item_errors': item_validation_errors
        }
        return render_to_response('couchflow/save_task_error.html',
            context, context_instance=RequestContext(request))


@login_required
def item_delete(request):
    context = {}

    render = lambda: render_to_response('couchflow/item_delete.html',
        context, context_instance=RequestContext(request))

    if not request.method == "POST":
        return render()

    nro_inv = request.POST.get("inventory_nbr", None)

    if not nro_inv:
        context["status"] = "Debe ingresar el numero de inventario"
        return render()

    item = WFItem.view('couchflow/by_inventory_nbr', include_docs=True,
        startkey=nro_inv, endkey=nro_inv).first()

    if not item:
        context["status"] = "Ese item no existe"
        return render()

    # TODO: make it a list
    item.fields_properties['99989'].first['exec_value'] = ['eliminado']
    item.save()
    context["status"] = "Item dado de baja"

    return render()

# fixes that shouldn't be here for the barcode module

if barcode and barcode.writer.ImageWriter is not None:
    class ImageWriter(barcode.writer.ImageWriter):
        def _paint_text(self, xpos, ypos):
            font = barcode.writer.ImageFont.truetype(barcode.writer.FONT,
                self.font_size)
            textwidth = self._draw.textsize(self.text, font=font)[0]
            pos = (mm2px(xpos, self.dpi) - textwidth / 2, mm2px(ypos, self.dpi))
            self._draw.text(pos, self.text, font=font, fill=self.foreground)

        def calculate_size(self, modules_per_line, number_of_lines, dpi=300):
            width, oldheight = barcode.writer.ImageWriter.calculate_size(self,
                modules_per_line, number_of_lines, dpi)

            height = 1.0 + self.module_height * number_of_lines
            if self.text:
                font_mm = (self.font_size * 25.4) / float(dpi)
                height += font_mm + self.text_distance * 2

            return (width, int(mm2px(height, dpi)))
else:
    ImageWriter = None


@login_required
def render_barcode(request, doc_id):
    item = WFItem.get(doc_id)
    if not item or item.inventory_nbr is None or barcode is None:
        return HttpResponseNotFound()

    if ImageWriter is not None:
        writer = ImageWriter()
        mimetype = "image/png"
    else:
        # PIL not available, use SVG output instead
        writer = None
        mimetype = "image/svg+xml"

    output = StringIO()
    barcode.generate("code39", item.inventory_nbr, writer, output, {
        'module_width': 0.4,
        'module_height': 12,
        'text_distance': 3,
        'text_size': 12,
        'dpi': 96,
    })

    return HttpResponse(output.getvalue(), mimetype=mimetype)


@login_required
def stats(request):
    db = get_db("couchauth")
    users_month_group = db.view("couchauth/stats_by_month_group",
        group=True).all()

    group_keys = list(set([x['key'][1] for x in users_month_group]))
    if None in group_keys:
        group_keys.remove(None)

    group_name_map = dict([(x['key'], x['doc']['name'])
        for x in db.view('_all_docs', keys=group_keys,
            include_docs=True).all()])
    group_name_map[None] = '(Sin grupo)'

    users_month_group_name = {}
    for x in users_month_group:
        month = x['key'][0]
        users_month_group_name.setdefault(month, [])
        group_name = group_name_map[x['key'][1]]
        users_month_group_name[month].append((group_name, x['value']))

    users_month_group = sorted(users_month_group_name.items())
    users_month_group_graph_keys = simplejson.dumps(
        users_month_group_name.keys())
    users_month_group_graph_values = simplejson.dumps(
        users_month_group_name.values())

    db = get_db("couchflow")

    by_item_type = db.view("couchflow/stats_by_item_type", group=True).all()
    by_item_type_graph = simplejson.dumps([(x['key'], x['value'])
        for x in by_item_type])

    by_072 = db.view("couchflow/stats_by_072", group=True).all()
    by_072_graph = simplejson.dumps([(x['key'], x['value'])
        for x in by_072])

    by_041 = db.view("couchflow/stats_by_041", group=True).all()
    by_041_graph = simplejson.dumps([(x['key'], x['value'])
        for x in by_041])

    circulation = db.view("couchflow/stats_circulation", group=True).all()
    circulation_dict = {}
    for x in circulation:
        month, log_type = x['key']
        circulation_dict.setdefault(month, {})
        circulation_dict[month][log_type] = x['value']

    circulation_graph_dict = {}
    for x in circulation:
        month, log_type = x['key']
        circulation_graph_dict.setdefault(log_type, [])
        circulation_graph_dict[log_type].append((month, x['value']))

    TRANSLATIONS = {
        'loan': 'Pr\xc3\xa9stamo',
        'return': 'Devoluci\xc3\xb3n'
    }
    circulation_graph_keys = simplejson.dumps([TRANSLATIONS.get(x, x)
        for x in circulation_graph_dict.keys()])
    circulation_graph_values = simplejson.dumps(circulation_graph_dict.values())

    loans_type = db.view("couchflow/stats_loans_by_item_type", group=True).all()

    loans_type_dict = {}
    for x in loans_type:
        month, itype = x['key']
        if itype is None:
            itype = '---'
        loans_type_dict.setdefault(month, {})
        loans_type_dict[month][itype] = x['value']

    context = {
        'users_month_group': users_month_group,
        'users_month_group_graph_keys': users_month_group_graph_keys,
        'users_month_group_graph_values': users_month_group_graph_values,
        'by_item_type': by_item_type,
        'by_item_type_graph': by_item_type_graph,
        'by_072': by_072,
        'by_072_graph': by_072_graph,
        'by_041': by_041,
        'by_041_graph': by_041_graph,
        'circulation': sorted(circulation_dict.items()),
        'circulation_graph_keys': circulation_graph_keys,
        'circulation_graph_values': circulation_graph_values,
        'loans_by_type': sorted(loans_type_dict.items()),
    }
    return render_to_response('couchflow/stats.html', context,
                              context_instance=RequestContext(request))

def get_cita(request, item_id):
    item = WFItem.get(item_id)

    cita_fields = [('100', 'a'), ('245', 'a'),
            ('260', 'b'), ('260', 'c')]
    cita = ''
    for f, sf in cita_fields:
        cfield = get_field(item, f, sf)
        if not cfield:
            #print "Invaid Cita!", f, sf
            cita = 'Cita no encontrada'
            break
        if sf:
            cfield = cfield[0]
        cita += cfield + ' '
    print "CITA"
    print cita

    data = simplejson.dumps({'success': True,
        'message': 'Success', 'data': cita})
    return HttpResponse(data, mimetype='application/json')
