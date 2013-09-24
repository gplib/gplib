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

import datetime
from couchdbkit import schema, DocumentSchema
from couchdbkit.ext.django.loading import get_db
from couchdbkit.resource import ResourceNotFound
from couchdbkit import ResourceConflict

from gplib.document import Document
from gplib.apps.couchauth.models import User

from utils import get_urn, get_field

import pymarc

VALID_CONECTORS = ["SequenceConector", "ExclusiveChoice", "MultipleInstances",
        "UntilConector", "SyncConector", "SimpleMergeConector", "ParallelSplit"]


def get_conector(conector_id):
    try:
        conector = Conector.get(conector_id)
    except ResourceNotFound:
        return None

    doc_type = conector.doc_type
    if doc_type not in VALID_CONECTORS:
        raise Exception, 'Invalid doc_type!:" %s"' % doc_type

    cls = globals().get(doc_type)

    #conector = cls.get(conector_id)
    conector = cls.wrap(conector.to_json())

    return conector


VALID_TASKS = ["DynamicDataTask", "DecisionTask", "WFItemsLoader",
        "ProcessTask", "FilterWFItems", "MarcImport", "CloneItems"]
def get_task(task_id):
    try:
        task = Task.get(task_id)
    except ResourceNotFound:
        return None

    doc_type = task.doc_type
    if doc_type not in VALID_TASKS:
        raise Exception, 'Invalid doc_type!:" %s"' % doc_type

    cls = globals().get(doc_type)
    #task = cls.get(task_id)
    task = cls.wrap(task.to_json())

    return task


class Task(Document):
    _db = get_db("couchflow")
    name = schema.StringProperty()
    task_type = schema.BooleanProperty(default=True)
    item_type = schema.StringProperty()
    node_type = schema.StringProperty(default="default")
    workflow_id = schema.StringProperty()
    workflow_type = schema.StringProperty()
    workflow_nro = schema.IntegerProperty(default=0)
    comments = schema.StringProperty()
    wfitems_ids = schema.ListProperty()
    conector_id = schema.StringProperty(default=None)
    user_id = schema.StringProperty(default=None)
    saved_by = schema.StringProperty(default=None)
    group_id = schema.StringProperty(default=None)
    prev_conector_id = schema.StringProperty(default=None)
    is_clone = schema.BooleanProperty(default=False)
    item_fields = schema.DictProperty()
    item_required_fields = schema.DictProperty()
    item_tema3_fields = schema.DictProperty()
    end = schema.BooleanProperty(default=False)
    step = schema.IntegerProperty(default=0)
    active = schema.BooleanProperty()
    have_until = schema.BooleanProperty(default=False)
    enabled = schema.BooleanProperty(default=False)
    status = schema.StringProperty()
    position = schema.DictProperty(default={'x':50, 'y':50})
    get_id = property(lambda self: self['_id'])

    # text shown in the task
    description = schema.StringProperty()
    group_by_urn = schema.BooleanProperty(default=False)
    visible = schema.BooleanProperty(default=True)

    # template used to display tasks, if exists
    html_tpl = schema.StringProperty(default="")

    # Used in loader
    base_item = schema.StringProperty()

    def is_bulkable(self):
        for i in self.item_fields:
            if self.item_fields[i] == 'write':
                return False
        return True

    def exec_process(self):
        return True

    @property
    def item_name(self):
        name = ''
        try:
            item = self.get_item(json=True)
            field = item['fields_properties']['245']['list'][0]
            name = field['subfields']['a']['exec_value'][0]
        except Exception, error:
            print 'Cant get item_name', error
            try:
                item = self.get_item(json=True)
                field = item['fields_properties']['700']['list'][0]
                name = field['subfields']['a']['exec_value'][0]
            except Exception, error:
                print '  Cant get item_name', error
        return name

    def get_saved_username(self):
        user = User.get(self.saved_by)
        return user.username

    def get_nro_pedido(self):
        #workflow = WorkFlow.get(self.workflow_id)
        #return workflow.nro_pedido
        return self.workflow_nro

    def get_info(self):
        info_list = []
        for i in self.wfitems_ids:
            item = WFItem.get(i)
            info_list.append(('item_name', item.name))
            item_info = item.get_info()
            info_list += item_info
        return info_list


    def get_item(self):
        if self.wfitems_ids:
            _id = self.wfitems_ids[0]
            return WFItem.get(_id)

        if self.base_item:
            return WFItem.get(self.base_item)

        if not self.item_type:
            return False

        items = WFItem.view("couchflow/item_names", limit=1,
            include_docs=True)
        item = items[self.item_type]
        item = item.one()
        return item

    def get_field_modes(self):
        item = self.get_item()
        field_mode = []
        for field in item.fields_properties:
            field_name = item.fields_properties[field]['field_name']
            if field in self.item_fields:
                mode = self.item_fields[field]
            else:
                mode = 'none'

            required = []

            field_doc = item.fields_properties[field].first
            for subfield_id, subfield in field_doc.subfields.iteritems():
                full_subfield_id = "%s_%s" % (field, subfield_id)
                required.append((full_subfield_id, subfield.description,
                    self.item_required_fields.get(full_subfield_id, False)))

            if not required:
                required.append((field, field_name,
                    self.item_required_fields.get(field, False)))

            tema3 = self.item_tema3_fields.get(field, False)

            field_mode.append((field, field_name, mode, required, tema3))
        field_mode.sort(key=lambda x: x[0])
        return field_mode

    def get_field_val(self, field_prop, field_mode):
        first = getattr(field_prop, 'first', field_prop)

        if 'exec_value' in first:
            exec_value = first['exec_value']
        else:
            exec_value = ""

        if field_mode == 'write':
            if exec_value:
                value = exec_value
            else:
                value = field_prop['default_value']
        else:
            value = exec_value

        if not value:
            value = ''
        if not isinstance(value, list):
            value = [value]
        return value

    def get_fields(self, field_mode):
        item = self.get_item()
        fields = []

        for i in self.item_fields:
            if self.item_fields[i] == field_mode:
                field_prop = item.fields_properties.get(i, None)
                if not field_prop:
                    continue
                value = self.get_field_val(field_prop, field_mode)

                tema3 = self.item_tema3_fields.get(i, False)

                subfields = []
                item_field = [int(i), field_prop, value, subfields, tema3]

                for sf in field_prop.first['subfields'].values():
                    sf_value = self.get_field_val(sf, field_mode)
                    subfields.append((sf, sf_value))

                fields.append(item_field)
        return fields

    def get_list_fields(self):
        items = WFItem.view("couchflow/item_names", include_docs=True)
        item = items[self.item_type]
        item = item.one()
        return simplejson.dumps(['id'] + item.fields_properties.keys())

    def read_item_fields(self):
        items = self.get_fields('read')
        return sorted(items)

    def write_item_fields(self):
        items = self.get_fields('write')
        return sorted(items)

    def get_wfitems_name(self):
        wfitems = []
        for i in self.wfitems_ids:
            wfitem = WFItem.get(i)
            wfitems.append((wfitem._id, wfitem.name))
        return wfitems

    def put_step(self):
        prev_conector = get_conector(self.prev_conector_id)
        self.step = prev_conector.step
        self.save()
        return True

    def go_deep(self):
        conector = get_conector(self.conector_id)
        tasks = conector.go_deep()
        if tasks:
            data = []
            for task in tasks:
                next_tasks = task.go_deep()
                data += next_tasks
            data.append(self)
            return data
        return [self]

    def back_to_top(self):
        conector = get_conector(self.prev_conector_id)
        tasks = conector.back_to_top()
        if tasks:
            data = []
            for task in tasks:
                prev_tasks = task.back_to_top()
                data += prev_tasks
            data.append(self)
            return data
        return [self]

    def finish_task(self, status):
        self.active = False
        self.status = status
        return True

    def active_conector(self):
        self.finish_task("finished")
        self.save()
        if self.conector_id:
            conector = get_conector(self.conector_id)
            if conector.to_next_tasks():
                return True
        return False


class MarcImport(Task):
    def check_data(self):
        return True

    def exec_process(self):
        # TODO: check this method:
        #item = self.get_item()
        #self.item_fields = {}
        #for i in item.fields_properties:
        #self.item_fields[i] = 'write'
        self.save()

    def import_marc(self, marc_file):
        pass

class DecisionTask(Task):
    sentence = schema.StringProperty()
    confirmation = schema.BooleanProperty(default=None)

    def check_data(self):
        return self.confirmation

    def active_conector(self):
        if self.conector_id:
            conector = get_conector(self.conector_id)
            if conector.doc_type == "SequenceConector" and \
                   self.confirmation:
                self.finish_task("finished")
                self.save()
                conector.to_next_tasks()
                return True
            if conector.doc_type == "SequenceConector" and \
                   not self.confirmation:
                self.finish_task("cancel")
                self.save()
                return True
            elif conector.doc_type != "SequenceConector":
                self.finish_task("finished")
                self.save()
                conector.to_next_tasks()
                return True
        return True


class DynamicDataTask(Task):
    """
    En el diagrama uml puesta como DataTask
    """
    extra_fields = schema.DictProperty()
    def show_extra_fields(self):
        fields = []
        for k in self.extra_fields:
            field = (k, self.extra_fields[k]['type'],
                     self.extra_fields[k]['default_value'])
            fields.append(field)
        return fields

    def check_data(self):
        for key in self.extra_fields:
            if not self.extra_fields[key]["exec_value"]:
                return False
        return True

class ProcessTask(Task):
    def exec_process(self):
        item = self.get_item()
        for field in self.item_fields:
            if not field in item.fields_properties:
                continue
            if self.item_fields[field]:
                item.fields_properties[field].first['exec_value'] = \
                                                [self.item_fields[field]]
        item.status = 'finished'
        item.active = False
        item.save()
        self.active_conector()
        return True

    def show_extra_fields(self):
        fields = []
        for k in self.extra_fields:
            field = (k, self.extra_fields[k]['type'],
                     self.extra_fields[k]['default_value'])
            fields.append(field)
        return fields

    def check_data(self):
        return True

class CloneItems(ProcessTask):
    def check_data(self):
        return True

    def exec_process(self):
        item = self.get_item()
        count = 0
        for field in item.fields_properties:
            field_prop = item.fields_properties[field]
            first = field_prop.first
            if field_prop['field_name'] == 'Cantidad' and\
                              field_prop['type'] == 'int':
                try:
                    count = int(first['exec_value'][0])
                    first['exec_value'] = ['0']
                except ValueError:
                    pass

        item.status = 'finished'
        item.active = False
        item.save()

        # TODO: bulk_save
        # should find a workarround with attachments
        #cloned_items = []
        for i in range(count-1):
            #new_item = item.really_clone(save=False)
            new_item = item.really_clone(save=True)
            self.wfitems_ids.append(new_item._id)
            #cloned_items.append(new_item)

        #db = self.get_db()
        #db.bulk_save(cloned_items)


        if len(self.wfitems_ids) > 1:
            self.save()

        self.active_conector()
        return True

class WFItemsLoader(DynamicDataTask):
    wfitems = schema.ListProperty()
    multiple = schema.BooleanProperty(default=False)
    order_nbr = schema.IntegerProperty()

    def active_conector(self):
        self.finish_task("finished")
        self.save()
        if self.conector_id:
            conector = get_conector(self.conector_id)
            if conector.doc_type != "MultipleInstances":
                tasks = Task.view("couchflow/flowtask", include_docs=True)
                tasks = tasks[self.workflow_id]
                for task in tasks:
                    if task._id != self._id:
                        task.wfitems_ids = self.wfitems_ids
                        task.save()
            if conector.to_next_tasks():
                return True
        return False

class FilterWFItems(WFItemsLoader):
    pass

class Conector(Document):
    _db = get_db("couchflow")
    workflow_id = schema.StringProperty()
    conector_type = schema.BooleanProperty(default=True)
    name = schema.StringProperty(default="Conector")
    status = schema.StringProperty()
    step = schema.IntegerProperty(default=0)
    is_clone = schema.BooleanProperty(default=False)
    start = schema.BooleanProperty(default=True)
    end = schema.BooleanProperty(default=False)
    active = schema.BooleanProperty()
    previous_tasks = schema.ListProperty()
    next_tasks = schema.ListProperty()
    get_id = property(lambda self: self['_id'])
    wfitems_ids = schema.ListProperty()

    def put_step(self):
        if not self.previous_tasks:
            self.step = 1
            self.save()
            workflow = WorkFlow.get(self.workflow_id)
            workflow.steps = self.step
            return True
        prev_task = get_task(self.previous_tasks[0])
        self.step = prev_task.step + 1
        workflow = WorkFlow.get(self.workflow_id)
        workflow.steps = self.step
        workflow.save()
        self.save()
        return True

    def back_to_top(self):
        previous_tasks = []
        if self.previous_tasks:
            for prev_task_id in self.previous_tasks:
                prev_task = Task.get(prev_task_id)
                previous_tasks.append(prev_task)
            return previous_tasks
        return None

    def go_deep(self):
        next_tasks = []
        if self.next_tasks:
            for next_task_id in self.next_tasks:
                next_task = get_task(next_task_id)
                next_tasks.append(next_task)
            return next_tasks
        return None


class BaseField(DocumentSchema):
    """
    A document schema representing a WFItem base field
    used by field and subfield
    """
    id = schema.StringProperty()
    field_name = schema.StringProperty()
    repeat = schema.BooleanProperty()
    type = schema.StringProperty()
    default_value = schema.StringProperty()
    exec_value = schema.ListProperty()

class SubField(BaseField):
    """
    A document schema representing a WFItem subfield
    """
    description = schema.StringProperty()

class Field(schema.DocumentSchema):
    """
    A document schema representing a WFItem field
    """
    indicator1 = schema.StringProperty()
    indicator2 = schema.StringProperty()
    subfields = schema.SchemaDictProperty(SubField())
    def __repr__(self):
        return "<Field i:[%s, %s]>" %  (self.indicator1, self.indicator2)

class Fields(BaseField):
    """
    A document schema representing a list of Field
    """
    list = schema.SchemaListProperty(Field)

    @property
    def first(self):
        return self.list[0]
    #def __getattr__(self, name):
    #    list = schema.DocumentSchema.__getitem__(self, 'list')
    #    if name == 'list':
    #        return list
    #    return getattr(list[0], name)

    def __repr__(self):
        return "<Fields id:%s name: %s>" %  (self.id, self.field_name)

class Loan(DocumentSchema):
    """
    A document schema representing a WFItem loan
    """
    user_id = schema.StringProperty()
    type = schema.StringProperty(choices=['room', 'home'])
    start = schema.DateProperty()
    end = schema.DateProperty()
    renew_count = schema.IntegerProperty()

    def __repr__(self):
        class_name = self.__class__.__name__
        start, end = self.start, self.end
        return '<%s: start:"%s" end:"%s">' % (class_name, start, end)

class Reserve(Loan):
    """
    A document schema representing a WFItem reserve
    """
    pass

class UrnConfig(DocumentSchema):
    """
    A document schema representing a WFItem urn_config
    used to identify unique groups of items
    """
    field = schema.StringProperty()
    subfield = schema.StringProperty()

class WFItem(Document):
    """
    WFItem could be any material of the system, like a book or a movie
    """
    _db = get_db("couchflow")
    name = schema.StringProperty()
    item_type = schema.StringProperty()
    is_clone = schema.BooleanProperty(default=False)

    fields_properties = schema.SchemaDictProperty(Fields)

    # circulation
    loan = schema.SchemaProperty(Loan)
    reserves = schema.SchemaListProperty(Reserve)

    # Unified Resource Name
    # We use a sum of fields to generate urn field
    urn_config = schema.SchemaListProperty(UrnConfig)

    # Not every item in the system can be loanable
    loanable = schema.BooleanProperty(default=True)

    # Order Number to track orders between workflows
    order_nbr = schema.IntegerProperty()

    # Reference Item
    # if it's a reference, it is used to complete fields from other items
    reference = schema.BooleanProperty(default=False)

    comments = schema.StringProperty()

    @property
    def urn(self):
        """
        Returns the urn based on urn_config property
        or None if it have not a valid urn
        """

        return get_urn(self)

    @property
    def inventory_nbr(self):
        """
        Returns inventory number (876_a) or None
        """

        field = self.get_field("876", "a")
        if field:
            return field[0]

    @property
    def title(self):
        """
        Returns item title, here for consistency
        """

        title = self.get_field("245", "a")
        if not title:
            title = "Unknown title"
        else:
            title = title[0]
        return title

    def get_field(self, field, subfield=None, first=True):
        """
        Helper that returns field or subfield, or None if can't find it
        """
        return get_field(self, field, subfield, first)

    def get_info(self):
        fields = []
        for k in self.fields_properties:
            field_prop = self.fields_properties[k]
            # TODO: support to more fields
            first_field_prop = field_prop.first
            if first_field_prop['exec_value']:
                value = first_field_prop['exec_value']
                k = k + ' - ' +  field_prop['field_name']
                field = (k, value)
                fields.append(field)

        return fields

    def show_fields_properties(self):
        """
        returns [(sequence number, Fields), ...]
        """
        return enumerate(sorted(self.fields_properties.values(),
            key=lambda x: x.id and int(x.id)))

    def fields_properties_items_sorted(self):
        return sorted(self.fields_properties.items())

    def check_form(self, post, task=None):
        errors = []

        def validate_field(number, value, field_type):
            """
            spec is the DocumentSchema for either Field or SubField
            """

            if field_type == 'int':
                if not value.isdigit():
                    errors.append([number, field_type])
            elif field_type == 'float':
                try:
                    float(value)
                except ValueError:
                    errors.append((number, field_type))

        for field_id, fields in self.fields_properties.iteritems():
            # forms don't support repeated fields yet (TODO elsewhere)
            field = fields.first
            field_name = fields.field_name
            if field_id in post:
                validate_field(field_name, post[field_id], fields.type)
                for subfield_id, subfield in field.subfields.iteritems():
                    sf_full_id = "%s_%s" % (field_id, subfield_id)
                    # TODO: check
                    if "sf_input" in post:
                        validate_field(sf_full_id, post["sf_" + sf_full_id],
                            subfield)

        if task:
            for field in task.item_required_fields:
                if "_" in field:
                    value = post.get("sf_" + field, '')
                else:
                    value = post.get(field, '')

                if not value:
                   errors.append([field, 'required'])

        return errors

    def marc_record(self):
        """
        Returns the item as a pymarc Record
        """
        record = pymarc.Record()

        for tag, fprop in self.fields_properties.iteritems():
            try:
                tag = int(tag)
            except Exception, error:
                continue

            # only marc fields
            if tag > 999:
                continue

            if fprop.first.subfields:
                sfields = []
                indicators = [fprop.first.indicator1 or "#",
                              fprop.first.indicator2 or "#"]
                for sf in fprop.first.subfields.values():
                    for val in sf.exec_value:
                        sfields.append(sf.field_name)
                        sfields.append(val)
                field = pymarc.Field(tag, indicators, sfields)
                record.add_field(field)
            else:
                try:
                    exec_value = fprop.first.exec_value
                except Exception:
                    exec_value = []
                indicators = [fprop.first.indicator1 or "#",
                              fprop.first.indicator2 or "#"]
                for val in exec_value:
                    record.add_field(pymarc.Field(tag, indicators, data=str(val)))
        return record

class WorkFlow(Document):
    _db = get_db("couchflow")
    name = schema.StringProperty()
    workflow_type = schema.StringProperty()
    item_type = schema.StringProperty()
    user_id = schema.StringProperty()
    conectors = schema.DictProperty()
    nro_pedido = schema.IntegerProperty(default=0)
    tasks = schema.DictProperty()
    merge_conectors = schema.DictProperty()
    original_task_ids = schema.DictProperty()
    enabled = schema.BooleanProperty(default=False)
    steps = schema.IntegerProperty(default=0)
    is_clone = schema.BooleanProperty(default=False)
    get_id = property(lambda self: self['_id'])
    # text shown in the task
    description = schema.StringProperty()
    path = schema.ListProperty(schema.StringProperty())
    # keep track of starting point of workflow
    # usefull to get all workflows that starts
    # with X task type, for example FilterItems
    first_task_type = schema.StringProperty()
    first_task_id = schema.StringProperty()
    visible = schema.BooleanProperty(default=True)

    def get_item(self):
        if not self.item_type:
            return False
        items = WFItem.view("couchflow/item_names", limit=1, include_docs=True)
        item = items[self.item_type]
        item = item.one()
        return item

    def get_items(self):
        item_query = WFItem.view("couchflow/items", include_docs=True)
        items = {}
        for item in item_query.all():
            items[item.item_type] = (item.name, False)

        if self.item_type in items:
            items[self.item_type] = (items[self.item_type][0], True)

        items = [(key, items[key][0], items[key][1]) for key in items]
        return items

    def remove_relations(self):
        conectors = WorkFlow.view("couchflow/flowconector", include_docs=True)
        conectors = conectors[self._id]
        # TODO: bulk delete
        for conector in conectors:
            conector.delete()
        tasks = Task.view("couchflow/flowtask", include_docs=True)
        tasks = tasks[self._id]
        for task in tasks:
            task.delete()
        return True

    def set_all_inactive(self):
        conectors = WorkFlow.view("couchflow/flowconector", include_docs=True)
        conectors = conectors[self._id]
        # TODO: bulk save
        for conector in conectors:
            conector.active = False
            conector.save()
        tasks = Task.view("couchflow/flowtask", include_docs=True)
        tasks = tasks[self._id]
        for task in tasks:
            task.finish_task(None)
            task.save()
        return True

    def get_docs(self):
        documents = WorkFlow.view("couchflow/flowdocs", include_docs=True)
        documents = documents[self._id]
        documents = documents.all()
        documents.reverse()
        return documents

    def set_enabled(self):
        tasks = Task.view("couchflow/flowtask", include_docs=True)
        tasks = tasks[self._id]
        flag = True
        for task in tasks:
            task.enabled = flag
            task.save()
        return True

    def set_disabled(self):
        tasks = Task.view("couchflow/flowtask", include_docs=True)
        tasks = tasks[self._id]
        flag = True
        for task in tasks:
            task.enabled = flag
            task.save()
        return True

    def get_first_conector(self):
        conectors = WorkFlow.view("couchflow/firstconector", include_docs=True)
        conectors = conectors[self._id]
        return conectors.one()

    def get_active_tasks(self):
        tasks = Task.view("couchflow/activetask", include_docs=True)
        tasks = tasks[self._id]
        return tasks

    def conector_tasks(self, conector):
        if len(conector.next_tasks) > 0:
            tasks = []
            # TODO: use bulk api to get tasks
            if not  conector.doc_type == "UntilConector":
                for task_id in conector.next_tasks:
                    task = Task.get(task_id)
                    tasks.append(task)
            else:
                task = Task.get(conector.next_tasks[0])
                tasks.append(task)
            return tasks
        return False

    def tasks_conectors(self, tasks):
        conectors = []
        for task in tasks:
            if task.conector_id:
                conector = get_conector(task.conector_id)
                #if conector.doc_type == "SequenceConector" and
                #conector.active:
                #    sequence_conector = SequenceConector.get(conector._id)
                conectors.append(conector)
        if len(conectors) > 0:
            return conectors
        return False

    def tasks_tree(self):
        first_conector = self.get_first_conector()
        tasks_tree = [[first_conector], ]

        tasks = self.conector_tasks(first_conector)

        while tasks:
            tasks_tree.append(tasks)
            conectors = self.tasks_conectors(tasks)
            if conectors:
                tasks_tree.append(conectors)
                tasks = []
                for conector in conectors:
                    try:
                        tasks += self.conector_tasks(conector)
                    except:
                        pass
            else:
                tasks = False
        if len(tasks_tree) > 1:
            return tasks_tree
        return False

    def add_conector(self, conector, active=False):
        self.conectors[conector._id] = active
        self.save()
        return True

    def add_task(self, task, active=False):
        self.tasks[task._id] = active
        self.save()
        return True

    def remove_tree(self, task):
        return True


class SequenceConector(Conector):

    def add_next_task(self, task):
        """
        Los sequence conector solo tienen una tarea  siguiente,
        si el objeto ve que tiene una tarea ya guardada devuelve
        False
        """
        if len(self.next_tasks) > 0:
            return False

        self.next_tasks.append(task._id)
        task.prev_conector_id = self._id
        task.save()
        self.save()
        return True

    def add_previous_task(self, task):
        """
        Los sequence conector solo tienen una tarea  previa,
        si el objeto ve que tiene una tarea ya guardada devuelve
        False
        """
        if len(self.previous_tasks) > 0:
            return False

        self.previous_tasks.append(task._id)
        return True

    def check_previous_tasks(self):
        """
        Chequea el status de sus previous_tasks,
        si las tareas padres cumplen el status
        cambia el atributo active a False.
        Si todas las tareas padres estan en active=False
        devuelve True al WorkFlow y
        cambia el status del conector a False.
        En Caso que no se cumpla alguno de los status
        devuelve False al WorkFlow y
        En el Caso de Sequence solo tendra un previous_tasks.
         """

    def to_next_tasks(self):
        """
        Pone a sus next_tasks el atributo active en True.
        Pone al atributo active del conector de sus next_task en True
        En el caso de SequenceConector solo tendra una Task
        """
        if len(self.next_tasks) > 0:
            if self.previous_tasks:
                previous_tasks = get_task(self.previous_tasks[0])
                if previous_tasks.check_data():
                    task = get_task(self.next_tasks[0])
                    task.active = True
                    task.save()
                    task.exec_process()
                if not previous_tasks.active:
                    previous_tasks.active = False
                    previous_tasks.save()
            else:
                task = get_task(self.next_tasks[0])
                task.active = True
                task.save()
                task.exec_process()
                self.active = True
                self.save
            return True
        return False


class SimpleMergeConector(Conector):

    def add_next_task(self, task):
        if len(self.next_tasks) > 0:
            return False

        self.next_tasks.append(task._id)
        task.prev_conector_id = self._id
        task.save()
        self.save()
        return True

    def add_previous_task(self, task):
        self.previous_tasks.append(task._id)
        self.save()
        return True

    def to_next_tasks(self):
        if len(self.next_tasks) > 0:
            if self.previous_tasks:
                for previous_task_id in self.previous_tasks:
                    previous_task = get_task(previous_task_id)
                    if previous_task.status == "finished":
                        task = Task.get(self.next_tasks[0])
                        task.active = True
                        task.exec_process()
                        task.save()


            else:
                task = Task.get(self.next_tasks[0])
                task.active = True
                task.exec_process()
                task.save()
                self.active = True
                self.save
            return True
        return False


class SyncConector(Conector):

    def add_next_task(self, task):
        if len(self.next_tasks) > 0:
            return False
        self.next_tasks.append(task._id)
        task.prev_conector_id = self._id
        task.save()
        self.save()
        return True

    def add_previous_task(self, task):
        self.previous_tasks.append(task._id)
        self.save()
        return True

    def to_next_tasks(self):
        if len(self.next_tasks) > 0:
            if self.previous_tasks:
                active_next = True
                for previous_task_id in self.previous_tasks:
                    previous_task = get_task(previous_task_id)
                    if previous_task.status != "finished":
                        active_next = False
                if active_next:
                    task = Task.get(self.next_tasks[0])
                    task.active = True
                    task.exec_process()
                    task.save()
            else:
                task = Task.get(self.next_tasks[0])
                task.active = True
                task.exec_process()
                task.save()
                self.active = True
                self.save
            return True
        return False


class ExclusiveChoice(Conector):
    def add_next_task(self, task):
        if len(self.next_tasks) >= 2:
            return False
        self.next_tasks.append(task._id)
        task.prev_conector_id = self._id
        task.save()
        self.save()
        return True
    def add_previous_task(self, task):
        if len(self.previous_tasks) > 0:
            return False
        self.previous_tasks.append(task._id)
        return True

    def check_previous_tasks(self):
        """
        """

    def to_next_tasks(self):
        if len(self.next_tasks) > 1 and self.previous_tasks:
            previous_tasks = Task.get(self.previous_tasks[0])
            if previous_tasks.doc_type == "DecisionTask":
                previous_tasks = DecisionTask.get(previous_tasks._id)
            elif  previous_tasks.doc_type == "DynamicDataTask":
                previous_tasks = DynamicDataTask.get(previous_tasks._id)
            if previous_tasks.check_data():
                task_id = self.next_tasks[0]
            else:
                task_id = self.next_tasks[1]

            task = get_task(task_id)
            self.active = True
            task.active = True
            task.exec_process()
            try:
                task.save()
            except ResourceConflict, error:
                print "[CONFLICT]", error
            previous_tasks.active = False
            previous_tasks.save()
            return True
        return False


class ParallelSplit(Conector):

    def add_next_task(self, task):
        if len(self.next_tasks) >= 2:
            return False
        self.next_tasks.append(task._id)
        task.prev_conector_id = self._id
        task.save()
        self.save()
        return True

    def add_previous_task(self, task):
        if len(self.previous_tasks) > 0:
            return False
        self.previous_tasks.append(task._id)
        return True

    def check_previous_tasks(self):
        """
        """

    def to_next_tasks(self):
        if len(self.next_tasks) > 1 and self.previous_tasks:
            previous_tasks = get_task(self.previous_tasks[0])
            if previous_tasks:
                if previous_tasks.check_data():
                    for task_id in self.next_tasks:
                        task = get_task(task_id)
                        if task:
                            task.active = True
                            task.exec_process()
                            task.save()
                    self.active = True
                    self.save()
                    previous_tasks.active = False
                    previous_tasks.save()
                    return True
        return False


class UntilConector(Conector):
    back_task_id = schema.StringProperty(default=None)
    def add_next_task(self, task):
        if len(self.next_tasks) >= 2:
            return False
        elif len(self.next_tasks) == 1 and \
                 self.back_task_id == self.next_tasks[0]:
            self.next_tasks = [task._id] + self.next_tasks
            self.save()
        elif len(self.next_tasks) == 1 and \
                 not self.back_task_id:
            self.back_task_id = task._id
            self.next_tasks.append(task._id)
        elif len(self.next_tasks) == 0:
            self.next_tasks.append(task._id)
        if not task.prev_conector_id:
            task.prev_conector_id = self._id
            task.save()
        else:
            task.have_until = True
            task.save()
        self.save()
        return True

    def add_previous_task(self, task):
        if len(self.previous_tasks) > 0:
            return False

        self.previous_tasks.append(task._id)
        return True

    def check_previous_tasks(self):
        """
        """

    def to_next_tasks(self):
        if len(self.next_tasks) > 1 and self.previous_tasks:
            previous_tasks = get_task(self.previous_tasks[0])
            if previous_tasks.check_data():
                task = get_task(self.next_tasks[0])
            else:
                task = get_task(self.next_tasks[1])
                task.status = None
            self.active = True
            task.active = True
            task.enabled = True
            task.exec_process()
            task.save()
            previous_tasks.active = False
            previous_tasks.save()
            return True
        return False


class MultipleInstances(Conector):
    iterator_field = schema.StringProperty()

    def add_next_task(self, task):
        if len(self.next_tasks) >= 1:
            return False
        self.next_tasks.append(task._id)
        task.prev_conector_id = self._id
        task.save()
        self.save()
        return True

    def add_previous_task(self, task):
        if len(self.previous_tasks) > 0:
            return False
        self.previous_tasks.append(task._id)
        return True

    def check_previous_tasks(self):
        """
        """

    def clone_conector(self, conector_id, wfitem_id=False):
        conector = get_conector(conector_id)
        try:
            del(conector._id)
        except AttributeError:
            pass

        try:
            del(conector._rev)
        except AttributeError:
            pass

        conector.previous_id = conector_id
        conector.is_clone = True

        if wfitem_id:
            conector.wfitems_ids.append(wfitem_id)
        conector.save()
        return conector._id

    def clone_task(self, task_id, wfitem_id=False):
        task = get_task(task_id)
        task = task.really_clone()

        task.previous_id = task_id
        task.is_clone = True
        if wfitem_id:
            task.wfitems_ids = [wfitem_id]
        task.save()
        if task.conector_id:
            task.conector_id = self.clone_conector(task.conector_id, wfitem_id)
            task.save()
            conector = get_conector(task.conector_id)
            conector.previous_tasks[conector.previous_tasks.index(task_id)] = task._id
            conector.save()
            next_tasks = []

            if conector.doc_type == "UntilConector":
                next_tasks.append(self.clone_task(conector.next_tasks[0], wfitem_id))
                t_id = conector.next_tasks[1]
                t_task = Task.view("couchflow/wf_oldid", include_docs=True)
                t_task = t_task[conector.workflow_id]
                t_task = t_task.all()[0]
                next_tasks.append(t_task._id)
            else:
                for con_task_id in conector.next_tasks:
                    next_tasks.append(self.clone_task(con_task_id, wfitem_id))

            conector.next_tasks = next_tasks
            conector.save()
        return task._id

    def create_multiple(self, number):
        task = get_task(self.next_tasks[0])
        number = int(number)
        for i in range(1, number):
            new_clone_id = self.clone_task(task._id)
            new_task = get_task(new_clone_id)
            new_task.active = True
            new_task.save()
            self.next_tasks.append(new_clone_id)
        self.save()
        return True

    def create_multiple_wfitems(self, wfitems):
        task = get_task(self.next_tasks[0])
        for wfitem_id in wfitems:
            new_clone_id = self.clone_task(task._id, wfitem_id)
            new_task = get_task(new_clone_id)
            new_task.active = True
            new_task.save()
            self.next_tasks.append(new_clone_id)
        self.next_tasks.remove(self.next_tasks[0])
        self.save()
        return True

    def to_next_tasks(self):
        if len(self.next_tasks) >= 1 and self.previous_tasks:
            previous_tasks = get_task(self.previous_tasks[0])
            if  previous_tasks.doc_type == "DynamicDataTask":
                number = previous_tasks.extra_fields[self.iterator_field]['exec_value'][0]
                try:
                    number = int(number)
                except ValueError:
                    return False
                self.create_multiple(number)
                task = Task.get(self.next_tasks[0])
                task.active = True
                task.save()
                self.save()
            elif previous_tasks.doc_type == "WFItemsLoader" or \
                     previous_tasks.doc_type == "FilterWFItems" or\
                     previous_tasks.doc_type == "CloneItems":
                self.create_multiple_wfitems(previous_tasks.wfitems_ids)
            for i in self.next_tasks:
                task = get_task(i)
                task.exec_process()
        return False

class Config(Document):
    _db = get_db("config")
    values = schema.DictProperty()

class CirculationLog(Document):
    _db = get_db("couchflow")

    type = schema.StringProperty(choices=['loan', 'return', 'renew'])
    loan_type = schema.StringProperty(choices=['room', 'home',
        'interbiblio'])
    item_type = schema.StringProperty()
    date = schema.DateProperty(default=datetime.date.today)
    length = schema.IntegerProperty()
    item_id = schema.StringProperty()
    user_id = schema.StringProperty()
    timestamp_added = schema.DateTimeProperty(default=datetime.datetime.now)
