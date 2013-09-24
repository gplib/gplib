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

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import datetime


from gplib.apps.webconf.views import  check_perms



@login_required
def index(request):
    context = { 'fecha': datetime.datetime.now(),
                'pagina': "esta es la pagina sin auth"
                }
    return render_to_response('portal/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
def only_users(request):
    context = { 'fecha': datetime.datetime.now(),
                'pagina': "Estas logeado"
                }
    return render_to_response('portal/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
@check_perms(check_superuser=False, check_staff=True, check_group=None)
def only_staff(request):
    context = { 'fecha': datetime.datetime.now(),
                'pagina': "Estas loggeado y sos staff"
                }
    return render_to_response('portal/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
@check_perms(check_superuser=True, check_staff=False, check_group=None)
def only_admins(request):
    context = { 'fecha': datetime.datetime.now(),
                'pagina': "Estas loggeado y sos admin"
                }
    return render_to_response('portal/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )


@login_required
@check_perms(check_superuser=False, check_staff=False, check_group="Bibliotecarios")
def only_biblio(request):
    context = { 'fecha': datetime.datetime.now(),
                'pagina': "Eres un usuario del grupo Bibliotecarios"
                }
    return render_to_response('portal/index.html',
                              context,
                              context_instance=RequestContext(request)
                              )
