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

from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
#from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from gplib.apps.couchflow.models import Config
from gplib.libs import pythree


@csrf_exempt
@login_required
def index(request):
    user = request.user
    context = {"user": user}
    if request.method == "POST" and 'query' in request.POST:
        context['query'] = request.POST['query']
    return render_to_response('tematres/index.html', context)

@csrf_exempt
@login_required
def admin(request):
    user = request.user

    tematres_conf = Config.get_or_create("tematres")
    hosts = tematres_conf["values"].get("hosts", [])
    query = query_server = None

    context = {"user": user, "hosts": hosts, "info": None, "terms": []}

    if request.method == "POST":
        if 'host' in request.POST:
            hosts = list(filter(None, request.POST.getlist("host")))
            tematres_conf["values"]["hosts"] = hosts
            tematres_conf.save()
            context["hosts"] = hosts
        elif 'query' in request.POST:
            query = request.POST.get("query")
            query_server = request.POST.get("query_server")

    if hosts:
        infos = []
        for host in hosts:
            service = pythree.Service(host)
            infos.append((host, service.info()))
        context["infos"] = infos

    if query and query_server:
        service = pythree.Service(query_server)
        if service.info().status == "available":
            similar = service.similar(query)
            terms = service.search(query)
            context["query"] = query
            context["query_server"] = query_server
            context["terms"] = terms
            context["similar"] = similar
        else:
            context["query_error"] = True


    return render_to_response("tematres/admin.html", context)

@csrf_exempt
@login_required
def query(request):
    host = request.user.tematres_host
    if not host:
        tematres_conf = Config.get_or_create("tematres")
        host = tematres_conf["values"].get("hosts", [None])[0]

    result = []
    if host:
        service = pythree.Service(host)
        if service.info().status == "available":
            query = request.GET.get("term")
            similar = service.similar(query)
            terms = service.search(query)
            result.append({'category': 'similar', 'label': similar})
            i = 0
            for term in terms:
                termdict = {'category': 'terms',
                    'label': term.string}
                i += 1
                if i < 5:
                    try:
                        termdict['desc'] = term.notes[0].text
                    except IndexError:
                        pass
                result.append(termdict)

    return HttpResponse(simplejson.dumps(result),\
                mimetype='application/javascript')

