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

import datetime

from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
#from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from couchdbkit.resource import ResourceNotFound

from gplib.apps.couchauth.models import User
from gplib.apps.couchflow.models import WFItem, Loan, Reserve
from gplib.apps.couchflow.models import CirculationLog
from gplib.apps.search.utils import search as search_lucene, sanitize_lucene

from datecalcs import get_business_day, get_hole


def jsonfy(*args, **kwargs):
    """
    Returns a django HttpResponse json response
    """
    return HttpResponse(simplejson.dumps(dict(*args, **kwargs)),\
                    mimetype='application/javascript')


def format_date(string, fmt="%Y-%m-%d"):
    return datetime.datetime.strptime(string, fmt).date()

@csrf_exempt
@login_required
def index(request):
    """
    Index page of circulation module
    """
    user = request.user
    context = {"user": user}

    return render_to_response('circulation/index.html', context)

@csrf_exempt
@login_required
def search_user(request):

    docs = []

    query = request.POST['filter']
    if not query:
        return_dict = {"sEcho": 1, "iTotalRecords": 0,
                       "iTotalDisplayRecords": 0,
                       "aaData": []}
        return jsonfy(**return_dict)

    if query.isdigit():
        query = "document_number:%s" % query
    else:
        query = "%s~.1" % sanitize_lucene(query)

    for doc in search_lucene('searchauth/user', database="couchauthsearch", q=query):
        docs.append(doc)

    start = int(request.POST['iDisplayStart'])
    length = int(request.POST['iDisplayLength'])
    secho = int(request.POST['sEcho'])+1

    #sort_col = int(request.POST['iSortCol_0'])
    #sort_dir = request.POST['sSortDir_0']

    count = len(docs)

    db = User.get_db()
    keys = [doc['id'] for doc in docs[start:start+length]]
    columns = []
    for doc in db.view('_all_docs', keys=keys, include_docs=True):
        doc = User.wrap(doc['doc'])

        username = '<a href="/circulation/user/%s">%s</a>' % \
                                        (doc._id, doc.username)

        if doc._attachments and 'photo' in doc._attachments:
            img_path = "/couchflow/get_attach/couchauth/%s/photo" % doc._id
            img = '<img style="width:40px" src="%s"/>' % img_path
        else:
            img = '<div class="nophoto">?</div>'
        first_name = doc.first_name
        last_name = doc.last_name
        dni = doc.document_number

        row = [doc._id, img, username, first_name, last_name, dni]

        columns.append(row)

    return_dict = {"sEcho": secho, "iTotalRecords": count,
                   "iTotalDisplayRecords": count,
                   "aaData": columns}
    return jsonfy(**return_dict)


@login_required
def user(request, user_id):
    """
    User Profile Page
    """
    #user = request.user

    user_db = User.get_db()

    if user_id == 'me':
        user = request.user
        groups = user.group_names
    else:
        user = User.get(user_id)
        groups = [x['doc']['name'] for x in
            user_db.view("couchauth/groups_by_username",
            key=user.username, include_docs=True)]

    if user._attachments and 'photo' in user._attachments:
        photo = "/couchflow/get_attach/couchauth/%s/photo" % user._id
    else:
        photo = None


    editlink = "/webconf/couchauth/edit_user/%s/" % user.username

    context = {
        "user": request.user,
        "userdoc": user,
        "photo": photo,
        "groups": groups,
        "editlink": editlink,
    }
    if 'biblio' in request.user.group_names:
        context['is_biblio'] = True

        if user_id == 'me':
            penalties = list(user_db.view("couchauth/penalties"))
            context['show_penalty_alert'] = True
            context['penalty_alert'] = penalties

    if context.get('is_biblio', False) or request.user.is_superuser or \
       user_id == 'me':

        circ_db = CirculationLog.get_db()
        startkey = [user._id]
        endkey = [user._id, {}]
        results = circ_db.view("circulation/logs",
            include_docs=True)[startkey:endkey]

        logs = {}
        for row in results:
            row_id = tuple(row['key'][1:])
            logs.setdefault(row_id, {})
            logs[row_id][row['doc']['doc_type']] = row['doc']

        logs_list = [x[1] for x in sorted(logs.items(), key=lambda x: x[0])]

        context['logs'] = logs_list

    return render_to_response('circulation/user.html', context)


@csrf_exempt
@login_required
def user_loans(request, user_id):
    """
    Returns the user loans as a json object
    """

    # use custom wrapper here, becouse default don't let you access to view keys
    loans = WFItem.view('circulation/loans', include_docs=True,
        wrapper=WFItem.wrap, startkey=[user_id], endkey=[user_id, {}, {}])

    reserves = WFItem.view('circulation/reserves', include_docs=True,
        wrapper=WFItem.wrap, startkey=[user_id], endkey=[user_id, {}, {}])

    start = int(request.POST['iDisplayStart'])
    length = int(request.POST['iDisplayLength'])
    secho = int(request.POST['sEcho'])+1
    count = len(loans) + len(reserves)

    columns = []
    for loan in loans:
        user_id, start, end = loan['_doc']['key']
        start, end = format_date(start), format_date(end)
        start = start.strftime("%d/%m/%Y")
        end = end.strftime("%d/%m/%Y")

        columns.append([loan._id, loan.inventory_nbr, "prestamo",loan.title, start, end, ""])

    for reserve in reserves:
        user_id, start, end = reserve['_doc']['key']
        start, end = format_date(start), format_date(end)
        start = start.strftime("%d/%m/%Y")
        end = end.strftime("%d/%m/%Y")
        columns.append([reserve._id, reserve.inventory_nbr, "reserva", reserve.title, start, end, ""])

    return_dict = {"sEcho": secho, "iTotalRecords": count,
                   "iTotalDisplayRecords": count,
                   "aaData": columns}

    return jsonfy(**return_dict)


@login_required
def search(request, user_id):
    """
    Search Item Popup
    """

    user = User.get(user_id)
    context = {"userdoc": user, "user": request.user}

    return render_to_response('circulation/search.html', context)

@login_required
def get_item_inventory(request, item_id):
    """
    Returns the list of inventory items
    """

    # TODO: Should this functiong get urn instead item_id?
    try:
        item = WFItem.get(item_id)
    except ResourceNotFound:
        return jsonfy(error='ResourceNotFound')

    urn = item.urn

    if not urn:
        return jsonfy(error='InvalidItem')

    items = WFItem.view('couchflow/by_urn',
            include_docs=True, startkey=urn, endkey=urn).all()

    return jsonfy(items=[item.inventory_nbr for item in items])


@csrf_exempt
@login_required
def return_loan(request, nro_inv=None):
    """
    Returns a loan by inventory number
    """

    context = {"user": request.user}

    if not request.method == "POST":
        return render_to_response('circulation/return_loan.html', context)

    nro_inv = request.POST.get("inventory_nbr", None)

    if not nro_inv:
        context["status"] = "Debe ingresar el numero de inventario"
        return render_to_response('circulation/return_loan.html', context)

    items = WFItem.view('couchflow/by_inventory_nbr', include_docs=True,
                                        startkey=nro_inv, endkey=nro_inv)

    if len(items) > 1:
        print "should only be one item"
    item = items.first()

    if not item:
        context["status"] = "Ese item no existe"
        return render_to_response('circulation/return_loan.html', context)

    if not item.loan.start:
        context["status"] = "Ese item no se encuentra prestado"
        return render_to_response('circulation/return_loan.html', context)

    # remove loan
    old_loan_type = item.loan.type
    old_loan_user = item.loan.user_id
    item.loan = Loan()
    item.save()
    CirculationLog(type='return', item_id=item._id,
        item_type=item.item_type, user_id=old_loan_user,
        loan_type=old_loan_type).save()

    context["status"] = 'El item "%s" ha sido devuelto exitosamente.' % nro_inv
    return render_to_response('circulation/return_loan.html', context)

@login_required
def remove_reserve(request, item_id, start, end):
    """
    Remove a reserve
    """

    item = WFItem.get(item_id)


def get_reserves_item(self, item_id):

    start = datetime.date.today()
    end = start + datetime.timedelta(days=7)

    requested_item = WFItem.get(item_id)

    urn = requested_item.urn

    if not urn:
        return jsonfy(error='invalid urn')

    items = WFItem.view('couchflow/by_urn',
            include_docs=True, startkey=urn, endkey=urn).all()

    loanable = False
    loanable_item = None

    for item in items:
        if not item.inventory_nbr:
            print "inventory_nbr is None"
            continue
        if not item.loan.start:
            loanable = True
            for reserve in item.reserves:
                if end >= reserve.start:
                    print "item unlonable:"
                    print "start:%s end: %s" % (start, end)
                    print reserve
                    print
                    loanable = False
                    break
        if loanable:
            loanable_item = item
            break

@login_required
def loan(request, what, user_id, item_id, loan_type=None):
    """
    Make a loan/reserve
    """

    # If date it's a reserve else it's a loan
    date = request.GET.get("date", None)
    user = User.get(user_id)
    if not user:
        return jsonfy(error='user not found')

    # TODO: get days from config
    days = 7
    if loan_type == 'room':
        days = 1

    if date:
        date = format_date(date, '%d/%m/%Y')
        start = get_business_day(date)

    start = get_business_day(datetime.date.today())
    end = get_business_day(start + datetime.timedelta(days=days))
    actual_days = (end - start).days

    requested_item = WFItem.get(item_id)


    # TODO: re do everything to use one item
    #urn = requested_item.urn

    #if not urn:
    #    return jsonfy(error='invalid urn')

    #items = WFItem.view('couchflow/by_urn',
    #        include_docs=True, startkey=urn, endkey=urn).all()

    items = [requested_item]

    loanable_items = []
    for item in items:
        if not item.inventory_nbr:
            print "inventory_nbr is None"
            continue

        # it's a reserve and item have a reserve
        # and it only must support 1 reserve per item
        if date and item.reserves:
            print 'No se puede reservar un item reservado'
            continue

        # it's a loan and item have a loan
        if not date and item.loan.start:
            print 'No se puede prestar un item prestado'
            continue

        # if nave no reserve and no loan it can
        # be given to anyone, so empty the list
        # and make it the only option
        if not item.reserves and not item.loan.start:
            loanable_items = [item]
            print "ideal, se puede prestar o reservar"
            break

        # if it's a loan, and item has not a loan and
        if (date and not item.reserves):
            loanable_items.append(item)

        # if it's a loan, and item has not a loan and
        # no fit in start and reserve
        if (not date and not item.loan.start):
            item_days = (item.reserves[0].start, item.reserves[0].end)
            new_start, new_end = get_hole([item_days], start, days)
            if new_start != start and new_end != end:
                loanable_items = [item]
                break


    # TODO: return json error
    # can't loan a item that is loaned
    if not loanable_items:
        all_dates = []
        for item in items:
            if item.loan.start and not item.reserves:
                all_dates.append(item.loan.end)
            elif item.reserves:
                all_dates.append(item.reserves[0].end)

        if not all_dates:
            return jsonfy(item=item_id, error="no se encuentra disponible")
        max_date = get_business_day(min(all_dates) + datetime.timedelta(1))
        max_date = max_date.strftime("%d/%m/%Y")
        error = 'No se pudo encontrar disponibilidad, '\
                'se calcula disponibilidad para el "%s"' % max_date
        return jsonfy(item=item_id, error=error)

    # if its a loan and there is only one
    # nothing else needed, dates and item is set
    if not date and len(loanable_items):
        item = loanable_items[0]

    # reserve an just one item
    elif date and len(loanable_items) == 1:
        item = loanable_items[0]

        # if there's a loan get the closest date
        if item.loan.start:
            item_days = (item.loan.start, item.loan.end)
            start, end = get_hole([item_days], start, days)

        # else you can make the reserve when asked
        else:
            print item.loan
            print item.reserves
            print 'IDEAL!'
    # there are more than one posible reserve, get the best
    else:
        loanable_dates = []
        for loanable in loanable_items:
            item_days = (loanable.loan.start, loanable.loan.end)
            new_start, new_end = get_hole([item_days], start, days)
            loanable_dates.append((new_start, new_end, loanable))
        loanable_dates.sort(key=lambda i:i[0])
        start, end, item = loanable_dates[0]

    if not date:
        loan = Loan(start=start, end=end, user_id=user_id, type=loan_type)
        item.loan = loan
        CirculationLog(type='loan', date=start, length=actual_days,
            item_type=item.item_type, loan_type=loan_type,
            item_id=item._id, user_id=user_id).save()
    else:
        reserve = Reserve(start=start, end=end, user_id=user_id)
        item.reserves.append(reserve)

    item.save()

    return jsonfy(item=item._id, status='loaned')

@login_required
def delete_loan(request, what, item_id):
    """
    Remove a loan from an item by item_id
    """

    item = WFItem.get(item_id)

    # item must have a loan
    if what == "loan" and not item.loan.start:
        return jsonfy(error='no existe el prestamo')
    # item must have a reserve
    elif what == "reserve" and not item.reserves:
        return jsonfy(error='no existe la reserve')

    if what == "loan":
        CirculationLog(type='return', item_id=item_id,
            item_type=item.item_type, user_id=item.loan.user_id,
            loan_type=item.loan.type).save()

        item.loan = Loan()
    else:
        # don't support pop
        #item.reserves.pop()
        del(item.reserves[0])

    item.save()

    return jsonfy(item=item_id, status='loan removed', what=what)

@login_required
def reserve_to_loan(request, item_id):

    item = WFItem.get(item_id)

    reserve = item.reserves.pop()
    item.loan = Loan.wrap(reserve.to_json())

    item.save()

    parse_date = lambda x: datetime.datetime.strptime(x, "%Y-%m-%d")
    length = (parse_date(item.loan.end) - parse_date(item.loan.start)).days

    CirculationLog(type='loan', date=item.loan.start, length=length,
        item_type=item.item_type, loan_type=item.loan.type,
        item_id=item._id, user_id=item.loan.user_id).save()

    return jsonfy(item=item_id, status='loan removed')


@login_required
def renew_loan(request, item_id):
    item = WFItem.get(item_id)

    # TODO: get days from config
    days = 7

    start = item.loan.end
    end = get_business_day(start + datetime.timedelta(days=days))
    actual_days = (end - start).days
    if item.reserves and item.reserves[0].start < end:
        return jsonfy(item=item_id, error="Se encuentra reservado")

    old_end = item.loan.end
    item.loan.end = end
    if not item.loan.renew_count:
        item.loan.renew_count = 0
    item.loan.renew_count += 1
    item.save()
    CirculationLog(type='renew', date=old_end, length=actual_days,
        item_id=item_id, item_type=item.item_type,
        loan_type=item.loan.type, user_id=item.loan.user_id).save()
    return jsonfy(item=item_id, status='loan renewed')


@login_required
def loan_ticket(request, item_id):
    item = WFItem.get(item_id)

    user = User.get(item.loan.user_id)
    context = {
        "user": user,
        "item": item,
        "end": item.loan.end.strftime("%d/%m/%Y"),
    }

    return render_to_response('circulation/loan_ticket.html', context)

@login_required
def return_loan_ticket(request, user_id, item_id):
    item = WFItem.get(item_id)

    now = datetime.datetime.now()

    user = User.get(user_id)
    context = {
        "user": user,
        "item": item,
        "end": now.strftime("%d/%m/%Y"),
    }

    return render_to_response('circulation/return_loan_ticket.html', context)
