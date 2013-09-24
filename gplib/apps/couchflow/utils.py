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

def get_field(doc, field, subfield=None, first=True):
    """
    Helper that returns field or subfield, or None if can't find it
    """

    field_prop = doc["fields_properties"].get(field, None)
    if not field_prop:
        return None

    # retro compatibility
    if first:
        field_prop = field_prop["list"][0]

    if not subfield:
        if not "exec_value" in field_prop:
            return None
        return field_prop["exec_value"]

    subfield_prop = field_prop["subfields"].get(subfield, None)

    if not subfield_prop or not subfield_prop["exec_value"]:
        return None

    return subfield_prop["exec_value"]

def get_urn(doc):
    """
    Returns the urn based on urn_config property
    or None if it have not a valid urn
    """

    # Reference items use id as urn
    if doc["reference"]:
        return doc["_id"]

    urn_value = ""
    for part in doc["urn_config"]:
        value = get_field(doc, part["field"], part["subfield"])
        if not value:
            value = "-"
        urn_value += value[0]

    if set(urn_value) == set("-"):
        return None
    return urn_value

import re
fields_rex = re.compile('<(span|div) class="block (read|write)" '
    'contenteditable="false">'
    '\s*?\[\[(?P<id>[0-9]*?) - (.*?)\]\]\s*?</(span|div)>')
empty_paragraph_re = re.compile('<p>\s*?\&nbsp;\s*?</p>')

def parse_wysiwyg_fields(task):
    from django.template import Context
    from django.template.loader import get_template

    tpl_by_field_type = {
        'read': get_template("couchflow/wysiwyg_read_data.html"),
        'write': get_template("couchflow/wysiwyg_write_data.html"),
    }

    read_fields = task.read_item_fields()
    write_fields = task.write_item_fields()

    fields_dict = {}

    for field_type, fields in [('read', read_fields), ('write', write_fields)]:
        for k, field, field_value, subfields, tema3 in fields:
            fields_dict[k] = (field_type, {"k": k, "field": field,
                "field_value": field_value, "tema3": tema3,
                "subfields": subfields})

    counter = [0] # hack to modify the value inside the function below

    def replace(match):
        group_dict = match.groupdict()
        _id = int(group_dict["id"])
        if _id in fields_dict:
            field_type, contextdict = fields_dict[_id]
            print "Found", field_type, _id
            tpl = tpl_by_field_type[field_type]

            counter[0] += 1
            contextdict["odd_or_even"] = 'odd' if counter[0] % 2 else 'even'

            return tpl.render(Context(contextdict))

    data = empty_paragraph_re.sub("", task.html_tpl)
    data = fields_rex.sub(replace, data)
    return data
