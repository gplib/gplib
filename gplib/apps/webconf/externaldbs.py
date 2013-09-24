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

# PYTHON IMPORTS
import datetime
import pickle

# DJANGO IMPORTS
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db import connections, transaction
import django.conf

# GPLIB IMPORTS
from gplib.apps.externaldbs.models import  ExternalDatabases, ExternalQuery
from gplib.apps.externaldbs.forms import ExternalQueryForm, ExternalDatabasesForm
from gplib.apps.webconf.views import  check_perms


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def index(request):
    context = {}
    return render_to_response('webconf/externaldbs/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
@check_perms(check_superuser=True, check_staff=False,check_group=None)
def create_extra_query(request):
    form = ExternalQueryForm()
    form_url = "/webconf/externaldbs/post_extra_query/"
    context = {
        'form': form,
        'form_url': form_url,
        }
    return render_to_response('webconf/externaldbs/form_extra_dbs.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def drop_extra_query(request, query_id):
    try:
        query = ExternalQuery.objects.get(id=query_id)
        query.delete()
    except ExternalQuery.DoesNotExist:
        pass
    return HttpResponseRedirect('/webconf/externaldbs/show_extra_dbs/')




@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def show_extra_query(request, query_id):
    query = ExternalQuery.objects.get(id=query_id)
    settings.DATABASES = get_dbs_dic()
    cursor = connections[query.external_database.name].cursor()
    cursor.execute(query.external_query)
    rows = cursor.fetchall()
    show_query = ""
    for row in rows:

        show_query += " - ".join(row) + "<br />"

    context = {
                'show_query': show_query,
                }
    return render_to_response('webconf/externaldbs/show_query.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def edit_extra_query(request,query_id):
    query = ExternalQuery.objects.get(id=query_id)
    form = ExternalQueryForm(instance=query)
    form_url = "/webconf/externaldbs/post_extra_query/%s/" % query_id
    context = {'form': form,
                'form_url': form_url,
                }
    return render_to_response('webconf/externaldbs/form_extra_dbs.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def new_extra_query(request):
    if request.method == 'POST':
        form = ExternalQueryForm(request.POST)
        if form.is_valid():
            extra_query_db = ExternalQuery()
            extra_query_db.external_query = form.cleaned_data['external_query']
            extra_query_db.external_database = form.cleaned_data['external_database']
            extra_query_db.save()
    return HttpResponseRedirect('/webconf/externaldbs/')



@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def save_extra_query(request, query_id):
    if request.method == 'POST':
        form = ExternalQueryForm(request.POST)
        if form.is_valid():
            extra_query_db = ExternalQuery.objects.get(id=query_id)
            extra_query_db.external_query = form.cleaned_data['external_query']
            extra_query_db.external_database = form.cleaned_data['external_database']
            extra_query_db.save()
    return HttpResponseRedirect('/webconf/externaldbs/')


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def show_extra_queries(request):
    context = {'queries': ExternalQuery.objects.all(),
                }
    return render_to_response('webconf/externaldbs/show_extra_queries.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def create_extra_db(request):
    form = ExternalDatabasesForm()
    form_url = "/webconf/externaldbs/post_extra_db/"
    context = { 'form' : form,
                'form_url': form_url,
                }
    return render_to_response('webconf/externaldbs/form_extra_dbs.html',
                              context,
                              context_instance=RequestContext(request)
                              )



@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def drop_extra_db(request, db_id):
    database = ExternalDatabases.objects.get(id=db_id)
    database.delete()
    return HttpResponseRedirect('/webconf/externaldbs/show_extra_dbs/')


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def edit_extra_db(request, db_id):
    database = ExternalDatabases.objects.get(id=db_id)
    form = ExternalDatabasesForm(instance=database)
    form_url = "/webconf/externaldbs/post_extra_db/%s/" % db_id
    context = { 'form' : form,
                'form_url': form_url,
                'database': database,
                }
    return render_to_response('webconf/externaldbs/form_extra_dbs.html',
                              context,
                              context_instance=RequestContext(request)
                              )





@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def save_extra_db(request, db_id):
    if request.method == 'POST':
        form = ExternalDatabasesForm(request.POST)
        database = ExternalDatabases.objects.get(id=db_id)
        if form.is_valid():
            database.name = form.cleaned_data['name']
            database.engine = form.cleaned_data['engine']
            database.database_name = form.cleaned_data['database_name']
            database.host = form.cleaned_data['host']
            database.port = form.cleaned_data['port']
            database.username = form.cleaned_data['username']
            database.password = form.cleaned_data['password']
            database.save()
            return HttpResponseRedirect('/webconf/externaldbs/')
        context = { 'form' : form,
                    }
        return render_to_response('webconf/externaldbs/form_extra_dbs.html',
                                  context,
                                  context_instance=RequestContext(request)
                                  )

    return HttpResponseRedirect('/webconf/externaldbs/')



@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def new_extra_db(request):
    if request.method == 'POST':
        form = ExternalDatabasesForm(request.POST)
        if form.is_valid():
            database = ExternalDatabases()
            database.name = form.cleaned_data['name']
            database.engine = form.cleaned_data['engine']
            database.database_name = form.cleaned_data['database_name']
            database.host = form.cleaned_data['host']
            database.port = form.cleaned_data['port']
            database.username = form.cleaned_data['username']
            database.password = form.cleaned_data['password']
            database.save()
            return HttpResponseRedirect('/webconf/externaldbs/')
        context = { 'form' : form,
                    }
        return render_to_response('webconf/externaldbs/form_extra_dbs.html',
                                  context,
                                  context_instance=RequestContext(request)
                                  )

    return HttpResponseRedirect('/webconf/externaldbs/')

@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def show_extra_dbs(request):
    context = { 'databases': ExternalDatabases.objects.all(),
                }
    return render_to_response('webconf/externaldbs/show_extra_dbs.html',
                              context,
                              context_instance=RequestContext(request)
                              )


def get_dbs_dic():
    extras_dbs_dict = settings.DATABASES
    for extra_database in ExternalDatabases.objects.all():
        extras_dbs_dict[extra_database.name] = {
            'ENGINE': extra_database.engine,
            'NAME': extra_database.database_name,
            'USER': extra_database.username,
            'PASSWORD': extra_database.password,
            'HOST': extra_database.host,
            'PORT': extra_database.port,
            }
    return extras_dbs_dict


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def database_save(request):
    extra_path = settings.PROJECT_PATH + "/extras_dbs.pck"
    extras_dbs_file = open(extra_path, "w")
    extras_dbs_dict = get_dbs_dic()
    pickle.dump(extras_dbs_dict, extras_dbs_file)
    extras_dbs_file.close()
    return HttpResponseRedirect("/webconf/externaldbs/")
