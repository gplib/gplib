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

import random
import datetime


def get_weekday(date):
    """
    If date is weekend go to next monday
    """

    weekday = date.weekday()
    if weekday > 4:
        date += datetime.timedelta(7-weekday)
    return date

def get_day_next_holydays(date):
    """
    Return next non holydays day
    """
    # get holydays from db
    return date

def get_business_day(date):
    """
    Return next business day
    """

    old_date = date

    date = get_weekday(date)
    date = get_day_next_holydays(date)

    if date != old_date:
        #print "Not Business Day!"
        return get_business_day(date)
    return date


def get_hole(dates, min_start, min_days):
    """
    Return the hole between dates where dates is a list
    of date tuples (start_date, end_date)

    Also check if start and end date is business day
    """

    days = datetime.timedelta(min_days)

    dates = sorted(dates, reverse=True)
    while dates:
        if len(dates) < 2:
            break
        start1, end1 = dates.pop()
        start2, end2 = dates[-1]

        # hole must start in >= min_start
        if min_start >= end1:
            continue

        end1 = get_business_day(end1)

        end_hole = end1 + days

        end_hole = get_business_day(end_hole)

        if end_hole < start2:
            #print 'free', end1, start2
            return end1, end_hole

    #print 'last'
    # if not found, return the greates one in the list
    # plus 1, becouse can't reserve same day it's returned
    start = dates[0][1] + datetime.timedelta(1)
    start = get_business_day(start)

    end = start + days
    end = get_business_day(end)
    return start, end


# TEST STUFF

def random_dates(max_dates=30):
    start = datetime.date.today()

    dates = []
    for i in xrange(max_dates):
        start = start + datetime.timedelta(random.randint(1, 142))
        end = start + datetime.timedelta(7)
        #print start, end
        start = end
        dates.append((start, end))
    return dates


if __name__ == '__main__':
    #min_start = datetime.date.today() + datetime.timedelta(9+random.randint(10, 98))
    #
    #all_holes = []
    #for i in range(10):
    #    dates = random_dates(1212)
    #    hole = get_hole(dates, min_start, 8)
    #    all_holes.append(hole)
    #
    #print min(all_holes)

    dates = [
        (datetime.date(2011, 10, 10), datetime.date(2011, 10, 16)),
        (datetime.date(2011, 10, 25), datetime.date(2011, 11, 10)),
        ]


    print "there's one hole 11/16 to 11/25"
    print
    print 'given minimun start "10/15" and days needed "7"'
    print "expected 10/17, 10/24 (start moves because weekend)"
    print "returned", get_hole(dates, datetime.date(2011, 10, 15), 7)
    print

    print 'given minimun start "10/15" and days needed "8"'
    print "expected 11/11, 11/21 (holes don't fit, take max date,"\
            " and last it's saturday, so plus 2 days)"
    print "returned", get_hole(dates, datetime.date(2011, 10, 15), 8)
    print
