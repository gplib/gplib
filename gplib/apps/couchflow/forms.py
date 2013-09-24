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

from couchdbkit.ext.django.schema import *
from couchdbkit.ext.django.forms  import DocumentForm
from models import WorkFlow, Task, Conector, WFItemsLoader, WFItem
from models import DynamicDataTask, DecisionTask, ProcessTask, FilterWFItems
from models import MultipleInstances, UntilConector, SequenceConector, CloneItems
from models import SimpleMergeConector, SyncConector, ParallelSplit, MarcImport
from django import forms
from django.forms.util import ValidationError, ErrorList


class MultipleInstancesForm(DocumentForm):
    class Meta:
        document = MultipleInstances

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['is_clone'])
        del(self.fields['step'])
        del(self.fields['saved_by'])
        del(self.fields['task_type'])
        del(self.fields['status'])
        del(self.fields['item_type'])


class WFItemForm(DocumentForm):
    class Meta:
        document = WFItem

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['is_clone'])
        del(self.fields['item_type'])

class ExecWFItemForm(DocumentForm):
    class Meta:
        document = WFItem

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['is_clone'])
        del(self.fields['name'])
        del(self.fields['item_type'])


class SimpleMergeConectorForm(DocumentForm):
    class Meta:
        document = SimpleMergeConector

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['workflow_id'])
        del(self.fields['is_clone'])
        del(self.fields['status'])


class SyncConectorForm(DocumentForm):
    class Meta:
        document = SyncConector

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['workflow_id'])
        del(self.fields['is_clone'])
        del(self.fields['status'])


class WorkFlowForm(DocumentForm):
    class Meta:
        document = WorkFlow

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['enabled'])
        del(self.fields['user_id'])
        del(self.fields['nro_pedido'])
        del(self.fields['workflow_type'])
        del(self.fields['item_type'])
        del(self.fields['steps'])
        del(self.fields['is_clone'])


class SequenceConectorForm(DocumentForm):
    class Meta:
        document = SequenceConector


class UntilConectorForm(DocumentForm):
    class Meta:
        document = UntilConector


class DynamicDataTaskForm(DocumentForm):
    class Meta:
        document = DynamicDataTask

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['prev_conector_id'])
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['node_type'])
        del(self.fields['workflow_id'])
        del(self.fields['task_type'])
        del(self.fields['saved_by'])
        del(self.fields['step'])
        del(self.fields['end'])
        del(self.fields['is_clone'])
        del(self.fields['status'])
        del(self.fields['have_until'])
        del(self.fields['enabled'])
        del(self.fields['group_id'])
        del(self.fields['user_id'])


class ProcessTaskForm(DocumentForm):
    class Meta:
        document = ProcessTask

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['prev_conector_id'])
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['node_type'])
        del(self.fields['saved_by'])
        del(self.fields['task_type'])
        del(self.fields['step'])
        del(self.fields['end'])
        del(self.fields['is_clone'])
        del(self.fields['status'])
        del(self.fields['enabled'])
        del(self.fields['group_id'])
        del(self.fields['user_id'])

class CloneItemsForm(DocumentForm):
    class Meta:
        document = CloneItems

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['prev_conector_id'])
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['node_type'])
        del(self.fields['saved_by'])
        del(self.fields['task_type'])
        del(self.fields['step'])
        del(self.fields['end'])
        del(self.fields['is_clone'])
        del(self.fields['status'])
        del(self.fields['enabled'])
        del(self.fields['group_id'])
        del(self.fields['user_id'])

class FilterWFItemsForm(DocumentForm):
    class Meta:
        document = FilterWFItems

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['prev_conector_id'])
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['task_type'])
        del(self.fields['step'])
        del(self.fields['saved_by'])
        del(self.fields['is_clone'])
        del(self.fields['status'])
        del(self.fields['have_until'])
        del(self.fields['enabled'])
        del(self.fields['multiple'])
        del(self.fields['node_type'])
        del(self.fields['group_id'])
        del(self.fields['end'])
        del(self.fields['user_id'])
        del(self.fields['item_type'])

class WFItemsLoaderForm(DocumentForm):
    class Meta:
        document = WFItemsLoader

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['prev_conector_id'])
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['saved_by'])
        del(self.fields['task_type'])
        del(self.fields['step'])
        del(self.fields['is_clone'])
        del(self.fields['status'])
        del(self.fields['have_until'])
        del(self.fields['enabled'])
        del(self.fields['multiple'])
        del(self.fields['node_type'])
        del(self.fields['group_id'])
        del(self.fields['end'])
        del(self.fields['user_id'])
        del(self.fields['item_type'])

class DecisionTaskForm(DocumentForm):
    class Meta:
        document = DecisionTask

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['enabled'])
        del(self.fields['saved_by'])
        del(self.fields['confirmation'])
        del(self.fields['have_until'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['group_id'])
        del(self.fields['node_type'])
        del(self.fields['user_id'])
        del(self.fields['task_type'])
        del(self.fields['status'])
        del(self.fields['prev_conector_id'])
        del(self.fields['is_clone'])
        del(self.fields['step'])
        del(self.fields['end'])
        del(self.fields['item_type'])
        del(self.fields['workflow_type'])
        del(self.fields['workflow_nro'])
        # WTF was sentence?
        del(self.fields['sentence'])

class MarcImportForm(DocumentForm):
    class Meta:
        document = MarcImport

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['enabled'])
        del(self.fields['saved_by'])
        del(self.fields['have_until'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['group_id'])
        del(self.fields['node_type'])
        del(self.fields['user_id'])
        del(self.fields['task_type'])
        del(self.fields['status'])
        del(self.fields['prev_conector_id'])
        del(self.fields['is_clone'])
        del(self.fields['step'])
        del(self.fields['end'])
        del(self.fields['item_type'])

class ExecMarcImportForm(DocumentForm):
    class Meta:
        document = MarcImport

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['enabled'])
        del(self.fields['saved_by'])
        del(self.fields['have_until'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['group_id'])
        del(self.fields['node_type'])
        del(self.fields['user_id'])
        del(self.fields['task_type'])
        del(self.fields['status'])
        del(self.fields['prev_conector_id'])
        del(self.fields['is_clone'])
        del(self.fields['step'])
        del(self.fields['end'])
        del(self.fields['item_type'])

class ExecDecisionForm(DocumentForm):
    class Meta:
        document = DecisionTask

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['name'])
        del(self.fields['saved_by'])
        del(self.fields['confirmation'])
        del(self.fields['end'])
        del(self.fields['item_type'])
        del(self.fields['sentence'])
        del(self.fields['enabled'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['node_type'])
        del(self.fields['user_id'])
        del(self.fields['group_id'])
        del(self.fields['task_type'])
        del(self.fields['have_until'])
        del(self.fields['status'])
        del(self.fields['is_clone'])
        del(self.fields['step'])
        del(self.fields['prev_conector_id'])



class ExecDynamicForm(DocumentForm):
    class Meta:
        document = DynamicDataTask

    def add_dynamic_fields(self, task):
        for field in  task.extra_fields:
            extra_field = task.extra_fields[field]
            if extra_field['type'] == 'int':
                self.fields[field] = forms.IntegerField(initial=extra_field['default_value'])  
            elif extra_field['type'] == 'boolean':
                self.fields[field] = forms.BooleanField()
            elif extra_field['type'] == 'string':
                self.fields[field] = forms.CharField(initial=extra_field['default_value'])

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['have_until'])
        del(self.fields['name'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['saved_by'])
        del(self.fields['is_clone'])
        del(self.fields['enabled'])
        del(self.fields['end'])
        del(self.fields['step'])
        del(self.fields['item_type'])
        del(self.fields['task_type'])
        del(self.fields['status'])
        del(self.fields['prev_conector_id'])
        del(self.fields['group_id'])
        del(self.fields['user_id'])
        del(self.fields['node_type'])
        del(self.fields['item_type'])

class ExecWFItemsLoader(DocumentForm):
    class Meta:
        document = WFItemsLoader
    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['prev_conector_id'])
        del(self.fields['active'])
        del(self.fields['node_type'])
        del(self.fields['name'])
        del(self.fields['conector_id'])
        del(self.fields['saved_by'])
        del(self.fields['workflow_id'])
        del(self.fields['task_type'])
        del(self.fields['step'])
        del(self.fields['is_clone'])
        del(self.fields['status'])
        del(self.fields['have_until'])
        del(self.fields['enabled'])
        del(self.fields['group_id'])
        del(self.fields['end'])
        del(self.fields['user_id'])

class  ExecFilterWFItemsForm(DocumentForm):
    class Meta:
        document = FilterWFItems
    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['prev_conector_id'])
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['workflow_id'])
        del(self.fields['task_type'])
        del(self.fields['saved_by'])
        del(self.fields['step'])
        del(self.fields['is_clone'])
        del(self.fields['status'])
        del(self.fields['have_until'])
        del(self.fields['enabled'])
        del(self.fields['multiple'])
        del(self.fields['node_type'])
        del(self.fields['group_id'])
        del(self.fields['end'])
        del(self.fields['user_id'])
        del(self.fields['item_type'])

class TaskForm(DocumentForm):
    class Meta:
        document = Task
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        del(self.fields['active'])
        del(self.fields['conector_id'])
        del(self.fields['saved_by'])
        del(self.fields['workflow_id'])
        del(self.fields['task_type'])
        del(self.fields['status'])
        del(self.fields['is_clone'])
        del(self.fields['step'])
        del(self.fields['prev_conector_id'])
        del(self.fields['group_id'])
        del(self.fields['node_type'])
        del(self.fields['user_id'])


CONECTOR_CHOICES = (
    ('SequenceConector', 'SequenceConector'),
    ('ExclusiveChoice', 'ExclusiveChoice'),
    ('ParallelSplit', 'ParallelSplit'),
    ('MultipleInstances', 'MultipleInstances'),
    ('UntilConector', 'UntilConector'),
    ('SyncConector', 'SyncConector'),
    ('SimpleMergeConector', 'SimpleMergeConector'),
    ('EndConector', 'Final de Workflow'),
    )


class ConectorChoiceForm(forms.Form):
    conector_type = forms.ChoiceField(choices=CONECTOR_CHOICES)


TASK_CHOICES = (
    ('DecisionTask', 'DecisionTask'),
    ('WFItemsLoader', 'WFItemsLoader'),
    ('FilterWFItems', 'FilterWFItems'),
    ('ProcessTask', 'ProcessTask'),
    ('MarcImport', 'MarcImport'),
    ('CloneItems', 'CloneItems'),
    )


class TaskChoiceForm(forms.Form):
    task_type = forms.ChoiceField(choices=TASK_CHOICES)
