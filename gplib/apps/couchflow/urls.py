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

from django.conf.urls.defaults import *

couchflow_webconf = patterns('',

                           (r'^couchflow/$', 'gplib.apps.couchflow.webconf.index'),
                           (r'^couchflow/new_workflow/$',
                            'gplib.apps.couchflow.webconf.new_workflow'),
                           (r'^couchflow/show_workflow/(?P<workflow_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.show_workflow'),
                           (r'^couchflow/enable_disable/(?P<workflow_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.enable_disable'),
                           (r'^couchflow/delete_workflow/(?P<workflow_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.delete_workflow'),
                           (r'^couchflow/save_workflow/(?P<workflow_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.save_workflow'),
                           (r'^couchflow/clone_workflow/(?P<workflow_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.clone_workflow'),
                           (r'^couchflow/save_workflow/$',
                            'gplib.apps.couchflow.webconf.save_workflow'),
                           (r'^couchflow/disconnect/(?P<conector_id>\w+)/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.disconnect_nodes'),
                           (r'^couchflow/new_task/(?P<workflow_id>\w+)/(?P<conector_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.new_task'),
                           (r'^couchflow/change_conector_type/(?P<conector_id>\w+)/(?P<conector_type>\w+)/$',
                            'gplib.apps.couchflow.webconf.change_conector_type'),
                           (r'^couchflow/show_task/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.show_task'),
                           (r'^couchflow/delete_task/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.delete_task'),
                           (r'^couchflow/connect_nodes/(?P<conector_id>\w+)/(?P<task_id>\w+)/(?P<conn_type>\w+)/$',
                            'gplib.apps.couchflow.webconf.connect_nodes'),
                           (r'^couchflow/save_task/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.save_task'),
                           (r'^couchflow/save_task/(?P<workflow_id>\w+)/(?P<conector_id>\w+)/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.save_task'),
                           (r'^couchflow/save_task/(?P<workflow_id>\w+)/(?P<conector_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.save_task'),
                           (r'^couchflow/create_form_task/(?P<workflow_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.create_form_task'),
                           (r'^couchflow/create_task/(?P<workflow_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.create_task'),
                           (r'^couchflow/edit_form_task/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.edit_form_task'),
                           (r'^couchflow/change_task/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.change_task'),
                           (r'^couchflow/edit_form_conector/(?P<conector_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.edit_form_conector'),
                           (r'^couchflow/edit_conector/(?P<conector_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.edit_conector'),
                           (r'^couchflow/task_pos/(?P<task_id>\w+)/(?P<pos_x>[0-9.]+)/(?P<pos_y>[0-9.]+)/$',
                            'gplib.apps.couchflow.webconf.task_pos'),
                           (r'^couchflow/new_item/$',
                            'gplib.apps.couchflow.webconf.item_form'),
                           (r'^couchflow/edit_item/(?P<item_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.item_form'),
                           (r'^couchflow/save_item/$',
                             'gplib.apps.couchflow.webconf.save_item'),
                           (r'^couchflow/save_item/(?P<item_id>\w+)/$',
                             'gplib.apps.couchflow.webconf.save_item'),
                           (r'^couchflow/select_item/(?P<workflow_id>\w+)/(?P<item_type>\w+)/$',
                             'gplib.apps.couchflow.webconf.select_item'),
                           (r'^couchflow/wf_item/(?P<workflow_id>\w+)/$',
                             'gplib.apps.couchflow.webconf.wf_item'),
                           (r'^couchflow/menueditor/$',
                             'gplib.apps.couchflow.webconf.menueditor_index'),
                           (r'^couchflow/menueditor/data.json$',
                             'gplib.apps.couchflow.webconf.menueditor_get_data'),
                           (r'^couchflow/menueditor/save$',
                             'gplib.apps.couchflow.webconf.menueditor_save'),

                           (r'^couchflow/edit_task_html/(?P<task_id>\w+)/$',
                            'gplib.apps.couchflow.webconf.edit_task_html'),
                           (r'^couchflow/clear_task_html/$',
                            'gplib.apps.couchflow.webconf.clear_task_html'),
                            )

urlpatterns = patterns('',
                       (r'^search_references/(?P<task_id>\w+)$',
                        'gplib.apps.couchflow.views.search_references'),
                       (r'^search_references$',
                        'gplib.apps.couchflow.views.search_references'),
                       (r'^use_reference/(?P<item_id>\w+)/(?P<reference_id>\w+)$',
                        'gplib.apps.couchflow.views.use_reference'),
                       (r'^use_reference/(?P<item_id>\w+)/(?P<reference_id>\w+)/(?P<client_side_changes>client_side_changes)$',
                        'gplib.apps.couchflow.views.use_reference'),

                       (r'^item_delete/$',
                        'gplib.apps.couchflow.views.item_delete'),
                       (r'^bulk_tasks/$',
                        'gplib.apps.couchflow.views.bulk_tasks'),
                       (r'^execute_task/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.execute_task'),
                       (r'^import_mrc/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.import_mrc'),

                       (r'^get_cita/(?P<item_id>\w+)/$',
                        'gplib.apps.couchflow.views.get_cita'),

                       (r'^save_task/(?P<task_type>\w+)/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.save_task'),
                       (r'^json/back_top/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.back_top'),
                       (r'^exec/(?P<url_name>\w+)/$',
                        'gplib.apps.couchflow.views.exec_url'),
                       (r'^edit_item/(?P<item_id>\w+)/$',
                        'gplib.apps.couchflow.views.edit_item'),
                       (r'^clone_edit_item/(?P<item_id>\w+)/$',
                        'gplib.apps.couchflow.views.clone_edit_item'),

                       (r'^item_create/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.item_create'),
                       (r'^item_created_edit/(?P<task_id>\w+)/(?P<item_id>\w+)/$',
                        'gplib.apps.couchflow.views.item_created_edit'),
                       (r'^del_item/(?P<item_id>\w+)/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.del_item'),

                       (r'^save_new_item/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.save_new_item'),
                       (r'^edit_new_item/(?P<task_id>\w+)/(?P<edit_item_id>\w+)/$',
                        'gplib.apps.couchflow.views.save_new_item'),

                       (r'^get_items/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.get_items'),

                       (r'^get_attach/(?P<db_name>\w+)/(?P<document_id>\w+)/(?P<name>.*)$',
                        'gplib.apps.couchflow.views.get_attach'),
                       (r'^export/(?P<doc_id>.*)$',
                        'gplib.apps.couchflow.views.export_mrc'),
                       (r'^render_barcode/(?P<doc_id>.*)$',
                        'gplib.apps.couchflow.views.render_barcode'),
                       (r'^stats/?$',
                        'gplib.apps.couchflow.views.stats'),
                       (r'^validate_task/(?P<task_id>\w+)/$',
                        'gplib.apps.couchflow.views.validate_task'),
                    )
