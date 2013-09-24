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
function make_table(id, headers){
    var thead = $('<thead>');
    var body = $('<tbody>').append(
       $('<tr>').append(
           $('<td colspan>').attr('colspan', 5)
              .attr('class', 'dataTables_empty')
              .html('Cargando Datos')
        )
    );
    var tr = $('<tr>');
    for(i in headers){
        var head = headers[i];
        if(typeof(head) == "object"){
            head = head[0];
        }
        tr.append($('<th>').html(head));
    }
    thead.append(tr);

    var table = $('<table>').attr('id', id+'_table')
        .attr('class', 'display').append(thead).append(body);
    $("#"+id).html(table);
}

function render_table(id, url, headers, extradata, selectable){
    make_table(id, headers);

    var columns_opts = [];

    for(k in headers){
        var head = headers[k];
        if(typeof(head) == "string"){
            columns_opts.push(null);
        }else{
            columns_opts.push(head[1]);
        }
    }

    var selected = [];
    var table = $('#'+id+'_table').dataTable({
            "bProcessing": true,
            "bServerSide": true,
            "bDestroy": true, // TODO: don't destroy, update =)
            "bFilter": true,
            "bInfo": true,
            "bJQueryUI": true,
            "bAutoWidth": true,
            "oLanguage": {
                    "sProcessing":   "Procesando...",
                    "sLengthMenu":   "Mostrar _MENU_ registros",
                    "sZeroRecords":  "No se encontraron resultados",
                    "sInfo":         "Mostrando desde _START_ hasta _END_ de _TOTAL_ registros",
                    "sInfoEmpty":    "Mostrando desde 0 hasta 0 de 0 registros",
                    "sInfoFiltered": "(filtrado de _MAX_ registros en total)",
                    "sInfoPostFix":  "",
                    "sSearch":       "Buscar:",
                    "sUrl":          "",
                    "oPaginate": {
                        "sFirst":    "Primero",
                        "sPrevious": "Anterior",
                        "sNext":     "Siguiente",
                        "sLast":     "Último"
                    }
            },
            //"bScrollCollapse": false,
            //"bLengthChange": false,
            "sAjaxSource": url,
            "fnRowCallback": function(nRow, aData, iDisplayIndex){
                if(selectable){
                    if(jQuery.inArray(aData[0], selected) != -1){
                        $(nRow).addClass('row_selected');
                    }
                }
                return nRow;
             },
            "aoColumns": columns_opts,
            "fnServerData": function (sSource, aoData, fnCallback){
                for(i in extradata){
                    //aoData.push({name:'{{input}}', value:$('#{{input}}')});
                    aoData.push({name:  extradata[i],
                                 value: $("#"+extradata[i]).val()});
                }

                $.ajax({
                    "dataType": 'json',
                    "type": "POST",
                    "url": sSource,
                    "data": aoData,
                    "success": fnCallback
                    });
            }
    });


    /* Click event handler */
    if(selectable){
        $('#'+id+'_table tbody tr').live('click', function(){
            var aData = table.fnGetData(this);
            var iId = aData[0];

            if(jQuery.inArray(iId, selected) == -1){
                selected[selected.length++] = iId;
            }else{
                selected = jQuery.grep(selected, function(value){
                    return value != iId;
                });
            }

            $(this).toggleClass('row_selected');
        });
    }
    table.selected = selected;
    return table;
}

$.fn.dataTableExt.oApi.fnMultiFilter = function( oSettings, oData ) {
    for ( var key in oData )
    {
        if ( oData.hasOwnProperty(key) )
        {
            for ( var i=0, iLen=oSettings.aoColumns.length ; i<iLen ; i++ )
            {
                if( oSettings.aoColumns[i].sName == key )
                {
                    /* Add single column filter */
                    oSettings.aoPreSearchCols[ i ].sSearch = oData[key];
                    break;
                }
            }
        }
    }
    this.oApi._fnDraw( oSettings );
}

function render_search_table(render_actions, config) {
  var default_config = {"input": "filter", 
                        "submit": "subfilter",
                        "showImage": true,
                        "actions_visible": true,
                        "extraData": ["filter"]
                        };
  var config = $.extend(default_config, config);

  var information = "Información";
  if(config.render_info) {
    information = [information, {'fnRender': config.render_info}];
  }

  var table = render_table('search_table', '/search/data',
    [
      ['id', {"bVisible": 0 }],
      ['Imagen', {'sWidth': "50px", "bVisible": config["showImage"]}],
      information,
      ['Acciones', {"bVisible": config.actions_visible, 'fnRender': render_actions, 'sWidth': '120px'}],

    ], config["extraData"], false);

  old_fnRowCallback = table.fnSettings().fnRowCallback;
  table.fnSettings().fnRowCallback = function(nRow, aData, iDisplayIndex) {
      nRow = old_fnRowCallback(nRow, aData, iDisplayIndex);
      link = $("<a>").text("Ver más").attr("href", "#").click(function(e) {
          e.preventDefault();
          $(this).parent().hide().parent().find(".search_more").show();
      });
      if(config["showImage"]){
        var td = "td:eq(1)";
      }else{
        var td = "td:eq(0)";
      }
      $(td, nRow).append($("<div>").append(link));
      return nRow;
  }

  table.hide();

  var filter = $('#'+config["input"])
  var sfilter = $('#'+config["submit"])

  sfilter.click(function(){
      table.fnDraw();
      table.show();
  });

  filter.keypress(function(e){
      var code = (e.keyCode ? e.keyCode : e.which);
      if(code == 13){
          sfilter.click();
      }
  });

  if(filter.val()){
      //sfilter.click();
      table.show();
  }
  return table;
}
