/*
 Este archivo es parte de GPLib - http://gplib.org/

 GPlib es software libre desarrollado en la Facultad de Filosofía y Letras de
 la Universidad de Buenos Aires y liberado bajo los términos de la licencia
 GPLIB FILO www.gplib.org/licencia bajo los términos de GPL de  GNU.  Usted
 puede redistribuirlo y/o modificarlo bajo los términos de la licencia GPLIB
 FILO de GNU General  Public License como esta publicado en la Free Software
 Foundation, tanto en la versión 3 de la licencia,  o cualquiera de las
 versiones futuras Gplib es distribuido con el objetivo de que sea útil, pero
 SIN NINGUNA GARANTÍA DE FUNCIONAMIENTO; ni siquiera la garantía implícita de
 que sirva para un propósito particular.  Cuando implemente este sistema
 sugerimos el registro en www.gplib.org/registro, con el fin de fomentar una
 comunidad de usuarios de GPLib.  Ver la GNU General Public License para más
 detalles.http://www.gnu.org/licenses/>


 Este arquivo é parte do GPLib http://gplib.org/

 GPLib é sofware livre desenviolvido na Faculdade de Filosofia e Letras da
 Universidade de Buenos Aires e liberado sob os termos da licença GPLib FILO
 www.gplib.org/licencia/ sob os termos de GPL de GNU.  Você pode redistribuí-lo
 e/ou modificá-lo sob os termos da licença pública geral GNU como publicado na
 Free Software Foundation , tanto na   versão 3 da licença ou  quaisquer
 versões futuras.  GPLib é distribuído com o objetivo de que seja útil, mas SEM
 QUALQUER GARANTIA DE PERFORMANCE; nem a garantia implícita de que servem a uma
 finalidade específica.  Quando  você implementar este sistema sugerimos o
 registro em www.gplib.org/registro/, a fim de promover uma comunidade de
 usuarios do GPLib.  Veja a GNU General Public License para mais detalles.
 http://www.gnu.org/licenses/


 This file is part of GPLib - http://gplib.org/

 GPLib is free software developed by Facultad de Filosofia y Letras Universidad
 de Buenos Aires and distributed under the scope of GPLIB FILO
 www.gplib.org/license and the GPL Public License GNU.  You can redistribute it
 and/or modify it under the terms of the GPLIB FILO GNU General Public License
 as published by the Free Software Foundation, either version 3 of the License,
 or  (at your option) any later version.

 GPLib is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 A PARTICULAR PURPOSE.  After roll your  own version of GPLIB you may register
 at www.gplib.org/register to buld a comunity of users and developers.  See the
 GNU General Public License for more details.
*/
(function(global){    // BEGIN CLOSURE

var Joint = global.Joint,
     Element = Joint.dia.Element,
     point = Joint.point;

/**
 * @name Joint.dia.ngw
 * @namespace Holds functionality related to ngw-charts.
 */
var ngw = Joint.dia.ngw = {};

/**
 * Predefined arrow. You are free to use this arrow as the option parameter to joint method.
 * @name arrow
 * @memberOf Joint.dia.ngw
 * @example
 * var arrow = Joint.dia.ngw.arrow;
 */
ngw.arrow = {
    startArrow: {type: 'none'},
    endArrow: {type: 'none'},
    attrs: {"stroke-dasharray": "none", 'stroke-width': 2, stroke: 'gray' }
};


ngw.arrow = {
        startArrow: {type: "none"},
        endArrow: {type: "basic", size: 7},
        attrs: {"stroke-dasharray": "none", 
                'stroke-width': 2 },
        data: {}
};


/**
 * Organizational chart member.
 * @methodOf Joint.dia.ngw
 */
ngw.Node = Element.extend({
    object: 'Node',
    module: 'ngw',
    init: function(properties) {
        var p = Joint.DeepSupplement(this.properties, properties, {
            attrs: { fill: 'lightgreen', stroke: '#008e09', 'stroke-width': 2 },
            description: '',
            title: '',
            titleAttrs: { 'font-weight': 'bold', 'font-size': 15},
            descriptionAttrs: { 'font-size': 11},
            labelOffsetY: 35,
            radius: 10,
            shadow: true,
            padding: 5
        });
        this.setWrapper(this.paper.rect(p.rect.x, p.rect.y, p.rect.width, p.rect.height, p.radius).attr(p.attrs));
        this.data = {"id": p.id};

        p.labelOffsetX = 10;

        if (p.title) {
            var titleElement = this.getTitleElement();
            this.addInner(titleElement[0]);
            this.addInner(titleElement[1]);      // swimlane
        }
        this.addInner(this.getDescriptionElement());
    },
    getTitleElement: function() {
        var p = this.properties;
        var bb = this.wrapper.getBBox();
        var t = this.paper.text(bb.x + bb.width/2, bb.y + bb.height/2, p.title).attr(p.titleAttrs || {});
        var tbb = t.getBBox();

        t.translate(bb.x - tbb.x + p.labelOffsetX, bb.y - tbb.y + tbb.height - 10);
        tbb = t.getBBox();
        var l = this.paper.path(['M', tbb.x, tbb.y + tbb.height + p.padding,
                                'L', tbb.x + tbb.width, tbb.y + tbb.height + p.padding].join(' '));
        return [t, l];
    },
    getDescriptionElement: function() {
        var p = this.properties;
        var bb = this.wrapper.getBBox();
        var t = this.paper.text(0, 0).attr(p.descriptionAttrs || {});

        var words = p.description.split(" ");

        var tmp = "";
        for (var i=0; i<words.length; i++) {
          t.attr("text", tmp + " " + words[i]);
          if (t.getBBox().width > bb.width - 16) {
            tmp += "\n" + words[i];
          } else {
            tmp += " " + words[i];
          }
        }
        t.attr("text", tmp.substring(1));
        t.attr('text-anchor', 'start');

        var tbb = t.getBBox();

        t.translate(bb.x - tbb.x + p.labelOffsetX, bb.y - tbb.y + p.labelOffsetY);
        return t;
    }
});

})(this);    // END CLOSURE
