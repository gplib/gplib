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

# DJANGO IMPORTS
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from couchdbkit.exceptions import ResourceNotFound

from forms import UserForm
from forms import GroupForm
from models import User, Group
from gplib.apps.couchflow.models import Config

# TODO: review permissions in this module

@login_required
def index(request):
    context = {}
    return render_to_response('webconf/couchauth/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
def show_users(request):
    groups = Group.view("couchauth/all_groups")
    users = User.view("couchauth/all_users")
    context = {'users': users, 'groups': groups,
               'form_title': 'Usuarios'
                }
    return render_to_response('webconf/couchauth/show_users.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
def edit_or_create_user(request, user_id=None, form=None, user=None):

    if (((user_id and user_id != request.user.username) or not user_id)
        and not request.user.is_superuser):
        context = {'error': 'No autorizado'}
        return render_to_response('error.html',
            context, context_instance=RequestContext(request))

    if user is None:
        if user_id:
            user = User.view("couchauth/username", key=user_id).one()
            if not user:
                return HttpResponseRedirect('/webconf/couchauth/show_users/')
        else:
            user = User()

    user.password = ''
    if form is None:
        form = UserForm(instance=user)

    if not request.user.is_superuser:
        del form.fields['is_staff']
        del form.fields['is_active']
        del form.fields['is_superuser']

    # Moved out of the main form layout on the template
    del form.fields['photo']

    tematres_conf = Config.get_or_create("tematres")
    hosts = tematres_conf["values"].get("hosts", [])
    form.fields['tematres_host'].widget.choices = map(None, hosts, hosts)

    form_url = "/webconf/couchauth/save_user/%s" % (user_id or '')

    if user_id:
        delete_url = "/webconf/couchauth/delete_user/%s" % (user._id)
        form_title = "Editando usuario: " + user.username
    else:
        delete_url = None
        form_title = "Creando usuario"

    groups = Group.view("couchauth/all_groups")

    if user._attachments and 'photo' in user._attachments:
        photo = "/couchflow/get_attach/couchauth/%s/photo" % (user._id)
    else:
        photo = None

    context = {
        'form': form,
        'userdoc': user,
        'form_title': form_title,
        'form_url': form_url,
        'delete_url': delete_url,
        'groups': groups,
        'photo': photo,
    }
    return render_to_response('webconf/couchauth/form_user.html',
        context, context_instance=RequestContext(request))

@login_required
def delete_user(request, user_id):
    if user_id != request.user.get_id and not request.user.is_superuser:
        context = {'error': 'No autorizado'}
        return render_to_response('error.html',
            context, context_instance=RequestContext(request))

    if request.method == 'POST':
        db = User.get_db()
        try:
            db.delete_doc(user_id)
        except ResourceNotFound:
            pass
    return HttpResponseRedirect('/webconf/couchauth/show_users/')

@login_required
def save_users(request):
    if request.method == 'POST':
        users_dic = {}
        for i in request.POST:
            if i[:5] == 'user_':
                user_id = i.split('_')[1]
                if user_id not in users_dic:
                    users_dic[user_id] = []
            elif i[:6] == 'group_':
                user_id, group_id = i.split('_')[1:]
                if user_id not in users_dic:
                    users_dic[user_id] = []
                users_dic[user_id].append(group_id)
        for user_id in users_dic:
            user = User.get(user_id)
            user.groups = users_dic[user_id]
            user.save()
    return HttpResponseRedirect('/webconf/couchauth/show_users/')


@login_required
def save_user(request, user_id=None):
    if (((user_id and user_id != request.user.username) or not user_id)
        and not request.user.is_superuser):
        context = {'error': 'No autorizado'}
        return render_to_response('error.html',
            context, context_instance=RequestContext(request))

    if request.method == 'POST':
        if user_id:
            user = user = User.view("couchauth/username", key=user_id).one()
            if not user:
                return HttpResponseRedirect('/webconf/couchauth/show_users/')
        else:
            user = User()

        form = UserForm(request.POST, instance=user)
        if not request.user.is_superuser:
            del form.fields['is_staff']
            del form.fields['is_active']
            del form.fields['is_superuser']

        if form.is_valid():
            oldpassword = user.password
            form.save(commit=False)

            if not form.cleaned_data['password']:
                user.password = oldpassword
            else:
                user.set_password(form.cleaned_data['password'])

            if request.user.is_superuser:
                groups = request.POST.getlist('groups')
                user.update_groups(groups)

            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                user.put_attachment(photo.read(), "photo", photo.content_type)

            user.save()
        else:
            return edit_or_create_user(request, user_id=user_id,
                form=form, user=user)
    return HttpResponseRedirect('/webconf/couchauth/show_users/')


@login_required
def show_groups(request):
    groups = Group.view("couchauth/all_groups")
    context = { 'groups': groups,
                }
    return render_to_response('webconf/couchauth/show_groups.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
def show_group(request, group_id):
    try:
        group = Group.get(group_id)
    except:
        return HttpResponseRedirect('/webconf/couchauth/show_groups/')

    form = GroupForm(instance=group)
    if form.is_valid():
        group = Group()
        group.name = form.cleaned_data['name']
        group.max_loan_days = form.cleaned_data['max_loan_days']
        group.save()
    form_url = "/webconf/couchauth/save_group/%s/" % group_id
    context = { 'form': form,
                'form_title': 'Editar Grupo',
                'group': group,
                'form_url': form_url,
                }
    return render_to_response('webconf/couchauth/form_group.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
def new_group(request):
    form = GroupForm()
    users = User.view("couchauth/all_users")
    form_url = "/webconf/couchauth/save_new_group/"
    context = { 'form': form,
                'form_url': form_url,
                'form_title': 'Crear Grupo',
                'users': users,
                }
    return render_to_response('webconf/couchauth/form_group.html',
                              context,
                              context_instance=RequestContext(request)
                              )




@login_required
def save_new_group(request):

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = Group()
            group.name = form.cleaned_data['name']
            group.max_loan_days = form.cleaned_data['max_loan_days']
            group.save()

    return HttpResponseRedirect('/webconf/couchauth/')


@login_required
def save_group(request, group_id):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():

            try:
                group = Group.get(group_id)
            except:
                return HttpResponseRedirect('/webconf/couchauth/show_groups/')

            users = request.POST.getlist('users')
            group.update_users(users)
            if group.name != form.cleaned_data['name']:
                group.name = form.cleaned_data['name']
                group.save()


    return HttpResponseRedirect('/webconf/couchauth/show_groups/')
