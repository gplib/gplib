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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required


def check_perms(check_superuser=False, check_staff=False, check_group=None):
    def function_wrap(func):
        def wrap(request, *args, **kwargs):
            user = request.user

            if check_superuser:
                if not user.is_superuser:
                    context = { 'error': "no eres superusuario, no puedes acceder"
                                }
                    return render_to_response('error.html',
                                              context,
                                              context_instance=RequestContext(request)
                                              )
            if check_staff:
                if not user.is_staff:
                    context = {'error': "no eres staff, no puedes acceder"}
                    return render_to_response('error.html',
                                              context,
                                              context_instance=RequestContext(request)
                                              )
            if check_group:
                group_object = Group.objects.get(name=check_group)
                if group_object  not in user.groups.all():
                    context = {'error': "no perteneces al grupo: %s" % check_group}
                    return render_to_response('error.html', context,
                                              context_instance=RequestContext(request)
                                              )
            return func(request, *args, **kwargs)
        return wrap
    return function_wrap


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def index(request):
    context = {
                'pagina': "Webconf"
                }
    return render_to_response('webconf/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )

@login_required
@check_perms(check_superuser=True) # this isn't used anywhere else..
def greenstone(request, context=None):
    from gplib.apps.couchflow.models import Config

    conf = Config.get_or_create("greenstone")

    if not context:
        context = {}

    context['conf'] = conf.values

    return render_to_response('webconf/greenstone.html', context,
        context_instance=RequestContext(request))

@login_required
@check_perms(check_superuser=True)
def greenstone_edit(request):
    from gplib.apps.couchflow.models import Config
    import os.path

    if request.method == "POST":
        conf = Config.get_or_create("greenstone")

        for key in ['host', 'upload_path', 'template']:
            old_val = conf.values.get(key, '')
            conf.values[key] = request.POST.get(key, old_val)

        context = {}
        if not os.path.isdir(conf.values["upload_path"]):
            context['error'] = "Invalid upload path"
        elif not os.access(conf.values["upload_path"], os.W_OK):
            context['error'] = "Can't write to upload path"
        elif conf.values["template"].startswith("/"):
            context['error'] = "Template can't start with /"
        elif not conf.values["template"].endswith(".pdf"):
            context['error'] = "Template must include .pdf extension"

        if 'error' not in context:
            conf.save()

        return greenstone(request, context)

@login_required
@check_perms(check_superuser=True)
def greenstone_test(request):
    from gplib.apps.couchflow.models import Config
    from gplib.apps.search.utils import greenstone_query

    if request.method == "POST":
        conf = Config.get_or_create("greenstone")
        collection = request.POST.get("collection", "")
        query = request.POST.get("query", "")
        context = {}
        context['results'] = greenstone_query(collection, "", query)
        context['postdata'] = request.POST

        return greenstone(request, context)
