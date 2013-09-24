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
(function() {
    var __slice = Array.prototype.slice;

    CKEDITOR.on('instanceCreated', function(_arg) {
        var editor;
        console.log(editor);
        editor = _arg.editor;
        return editor.on('pluginsLoaded', function() {
            var $$, DISABLED, ENABLED, MenuElement, OffsetsByLevel, RedrawSubMenuName, cellNodeRegex, cmd, col, colItems, getCellColIndex, getColumnsIndices, getElementsByClassName, getSelectedCells, isFirstColumn, isFirstRow, isLastColumn, isLastRow, key, moveColumn, moveColumnAfter, moveColumnBefore, moveRowAfter, moveRowBefore, redrawContextMenu, row, rowItems, subMenuName, _fn, _i, _len, _ref;
            ENABLED = CKEDITOR.TRISTATE_OFF, DISABLED = CKEDITOR.TRISTATE_DISABLED;
            RedrawSubMenuName = null;
            OffsetsByLevel = [];
            row = editor.getMenuItem('tablerow');
            rowItems = row.getItems();
            row.getItems = function() {
                var sel;
                sel = editor.getSelection();
                return CKEDITOR.tools.extend({
                    tablerow_moveBefore: isFirstRow(sel) ? DISABLED : ENABLED,
                       tablerow_moveAfter: isLastRow(sel) ? DISABLED : ENABLED
                }, rowItems);
            };
            col = editor.getMenuItem('tablecolumn');
            colItems = col.getItems();
            col.getItems = function() {
                var sel;
                sel = editor.getSelection();
                return CKEDITOR.tools.extend({
                    tablecolumn_moveBefore: isFirstColumn(sel) ? DISABLED : ENABLED,
                       tablecolumn_moveAfter: isLastColumn(sel) ? DISABLED : ENABLED
                }, colItems);
            };
            editor.addMenuItems({
                tablerow_moveBefore: {
                    label: 'Move Row Before',
                group: 'tablerow',
                command: 'rowMoveBefore',
                order: 11
                },
                tablerow_moveAfter: {
                    label: 'Move Row After',
                group: 'tablerow',
                command: 'rowMoveAfter',
                order: 12
                },
                tablecolumn_moveBefore: {
                    label: 'Move Column Before',
                group: 'tablecolumn',
                command: 'columnMoveBefore',
                order: 11
                },
                tablecolumn_moveAfter: {
                    label: 'Move Column After',
                    group: 'tablecolumn',
                    command: 'columnMoveAfter',
                    order: 12
                }
            });
            editor.addCommand("rowMoveBefore", {
                exec: function(editor) {
                    return moveRowBefore(editor.getSelection());
                }
            });
            editor.addCommand("rowMoveAfter", {
                exec: function(editor) {
                    return moveRowAfter(editor.getSelection());
                }
            });
            editor.addCommand("columnMoveBefore", {
                exec: function(editor) {
                    return moveColumnBefore(editor.getSelection());
                }
            });
            editor.addCommand("columnMoveAfter", {
                exec: function(editor) {
                    return moveColumnAfter(editor.getSelection());
                }
            });
            _ref = ['rowInsertBefore', 'rowInsertAfter', 'columnInsertBefore', 'columnInsertAfter'];
            _fn = function(cmd, subMenuName) {
                cmd._origExec = cmd.exec;
                return cmd.exec = function() {
                    var args, rv;
                    args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
                    rv = this._origExec.apply(this, args);
                    redrawContextMenu(subMenuName);
                    return rv;
                };
            };
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                key = _ref[_i];
                cmd = editor._.commands[key];
                if (cmd._origExec) continue;
                subMenuName = "table" + (key.replace(/Insert.*/, ''));
                _fn(cmd, subMenuName);
            }
            MenuElement = null;
            CKEDITOR.ui.on('ready', function(_arg2) {
                var data, _ref2;
                data = _arg2.data;
                if ((_ref2 = data._) != null ? _ref2.panel : void 0) {
                    return MenuElement = data;
                }
            });
            editor.on('menuShow', function(_arg2) {
                var data, level, panel;
                data = _arg2.data;
                if (!RedrawSubMenuName) return;
                panel = data[0];
                level = panel._.definition.level;
                return setTimeout((function() {
                    var idx, item, _fn2, _len2, _ref2;
                    panel.element.setStyles(OffsetsByLevel[level]);
                    _ref2 = MenuElement.items;
                    _fn2 = function(MenuElement, idx) {
                        return setTimeout((function() {
                            return MenuElement._.showSubMenu(idx);
                        }), 201);
                    };
                    for (idx = 0, _len2 = _ref2.length; idx < _len2; idx++) {
                        item = _ref2[idx];
                        if (item.name !== RedrawSubMenuName) continue;
                        _fn2(MenuElement, idx);
                        RedrawSubMenuName = null;
                        return;
                    }
                }), 1);
            });
            isFirstRow = function(selection) {
                var cells, firstCell, mapCell, maxRowSpan, rowCells, startRow, startRowIndex, table;
                cells = getSelectedCells(selection);
                firstCell = cells[0];
                startRow = firstCell.getParent();
                startRowIndex = startRow.$.rowIndex;
                if (startRowIndex === 0) return true;
                table = firstCell.getAscendant('table');
                rowCells = table.$.rows[0].cells;
                maxRowSpan = Math.max.apply(Math, (function() {
                    var _j, _len2, _results;
                    _results = [];
                    for (_j = 0, _len2 = rowCells.length; _j < _len2; _j++) {
                        mapCell = rowCells[_j];
                        _results.push(mapCell.rowSpan);
                    }
                    return _results;
                })());
                return startRowIndex <= (maxRowSpan - 1);
            };
            isLastRow = function(selection) {
                var cells, endRow, endRowIndex, lastCell, mapCell, maxRowSpan, rowCells, table;
                cells = getSelectedCells(selection);
                lastCell = cells[cells.length - 1];
                table = lastCell.getAscendant('table');
                endRow = lastCell.getParent();
                rowCells = endRow.$.cells;
                endRowIndex = endRow.$.rowIndex;
                maxRowSpan = Math.max.apply(Math, (function() {
                    var _j, _len2, _results;
                    _results = [];
                    for (_j = 0, _len2 = rowCells.length; _j < _len2; _j++) {
                        mapCell = rowCells[_j];
                        _results.push(mapCell.rowSpan);
                    }
                    return _results;
                })());
                return (endRowIndex + maxRowSpan) >= table.$.rows.length;
            };
            isFirstColumn = function(selection) {
                var cells, startColIndex;
                cells = getSelectedCells(selection);
                startColIndex = getColumnsIndices(cells, 1);
                return startColIndex === 0;
            };
            isLastColumn = function(selection) {
                var cells, colIndex, endColIndex, lastRow, mapCell, rowCells, _j, _len2;
                cells = getSelectedCells(selection);
                endColIndex = getColumnsIndices(cells);
                lastRow = cells[cells.length - 1].getParent();
                rowCells = lastRow.$.cells;
                colIndex = -1;
                for (_j = 0, _len2 = rowCells.length; _j < _len2; _j++) {
                    mapCell = rowCells[_j];
                    colIndex += mapCell.colSpan;
                    if (colIndex > endColIndex) return false;
                }
                return true;
            };
            $$ = function(elm) {
                return new CKEDITOR.dom.element(elm);
            };
            moveRowBefore = function(selection) {
                var cells, endRow, firstCell, prevRow, startRowIndex, table;
                cells = getSelectedCells(selection);
                endRow = cells[cells.length - 1].getParent();
                firstCell = cells[0];
                startRowIndex = firstCell.getParent().$.rowIndex;
                table = firstCell.getAscendant('table');
                prevRow = table.$.rows[startRowIndex - 1];
                $$(prevRow).insertAfter(endRow);
                return redrawContextMenu('tablerow');
            };
            moveRowAfter = function(selection) {
                var cells, endRowIndex, lastCell, nextRow, startRow, table;
                cells = getSelectedCells(selection);
                startRow = cells[0].getParent();
                lastCell = cells[cells.length - 1];
                endRowIndex = lastCell.getParent().$.rowIndex + lastCell.$.rowSpan - 1;
                table = lastCell.getAscendant('table');
                nextRow = table.$.rows[endRowIndex + 1];
                $$(nextRow).insertBefore(startRow);
                return redrawContextMenu('tablerow');
            };
            moveColumn = function(selection, isBefore) {
                var cells, endColIndex, row, rowCells, startColIndex, table, _j, _len2, _ref2;
                cells = getSelectedCells(selection);
                table = cells[0].getAscendant('table');
                startColIndex = getColumnsIndices(cells, 1);
                endColIndex = getColumnsIndices(cells);
                _ref2 = table.$.rows;
                for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
                    row = _ref2[_j];
                    rowCells = row.cells;
                    if (isBefore) {
                        $$(rowCells[startColIndex - 1]).insertAfter($$(rowCells[endColIndex]));
                    } else {
                        $$(rowCells[endColIndex + 1]).insertBefore($$(rowCells[startColIndex]));
                    }
                }
                return redrawContextMenu('tablecolumn');
            };
            moveColumnBefore = function(selection) {
                return moveColumn(selection, true);
            };
            moveColumnAfter = function(selection) {
                return moveColumn(selection, false);
            };
            redrawContextMenu = function(subMenuName) {
                var $parent, elm, idx, _len2, _ref2;
                RedrawSubMenuName = subMenuName;
                _ref2 = getElementsByClassName('cke_contextmenu');
                for (idx = 0, _len2 = _ref2.length; idx < _len2; idx++) {
                    elm = _ref2[idx];
                    $parent = new CKEDITOR.dom.element(elm.parentNode);
                    OffsetsByLevel[idx] = {
                        top: $parent.getComputedStyle('top'),
                        left: $parent.getComputedStyle('left')
                    };
                }
                return editor.execCommand('contextMenu');
            };
            cellNodeRegex = /^(?:td|th)$/;
            getSelectedCells = function(selection) {
                var bookmarks, database, i, moveOutOfCellGuard, nearestCell, node, parent, range, ranges, retval, startNode, walker, _j, _len2;
                bookmarks = selection.createBookmarks();
                ranges = selection.getRanges();
                retval = [];
                database = {};
                i = 0;
                moveOutOfCellGuard = function(node) {
                    if (retval.length > 0) return;
                    if (node.type === CKEDITOR.NODE_ELEMENT && cellNodeRegex.test(node.getName()) && !node.getCustomData("selected_cell")) {
                        CKEDITOR.dom.element.setMarker(database, node, "selected_cell", true);
                        retval.push(node);
                    }
                };
                for (_j = 0, _len2 = ranges.length; _j < _len2; _j++) {
                    range = ranges[_j];
                    if (range.collapsed) {
                        startNode = range.getCommonAncestor();
                        nearestCell = startNode.getAscendant("td", true) || startNode.getAscendant("th", true);
                        if (nearestCell) retval.push(nearestCell);
                    } else {
                        walker = new CKEDITOR.dom.walker(range);
                        node = void 0;
                        walker.guard = moveOutOfCellGuard;
                        while ((node = walker.next())) {
                            parent = node.getAscendant("td") || node.getAscendant("th");
                            if (parent && !parent.getCustomData("selected_cell")) {
                                CKEDITOR.dom.element.setMarker(database, parent, "selected_cell", true);
                                retval.push(parent);
                            }
                        }
                    }
                }
                CKEDITOR.dom.element.clearAllMarkers(database);
                selection.selectBookmarks(bookmarks);
                return retval;
            };
            getColumnsIndices = function(cells, isStart) {
                var cell, colIndex, retval, _j, _len2;
                retval = (isStart ? Infinity : 0);
                for (_j = 0, _len2 = cells.length; _j < _len2; _j++) {
                    cell = cells[_j];
                    colIndex = getCellColIndex(cell, isStart);
                    if (isStart) {
                        if (colIndex < retval) retval = colIndex;
                    } else {
                        if (colIndex > retval) retval = colIndex;
                    }
                }
                return retval;
            };
            getCellColIndex = function(cell, isStart) {
                var colIndex, mapCell, rowCells, _j, _len2;
                row = cell.getParent();
                rowCells = row.$.cells;
                colIndex = 0;
                for (_j = 0, _len2 = rowCells.length; _j < _len2; _j++) {
                    mapCell = rowCells[_j];
                    colIndex += (isStart ? 1 : mapCell.colSpan);
                    if (mapCell === cell.$) break;
                }
                return colIndex - 1;
            };
            /*
               [MIT License Code Inclusion]
               Developed by Robert Nyman, http://www.robertnyman.com
               Code/licensing: http://code.google.com/p/getelementsbyclassname/
               */
            return getElementsByClassName = function(className, tag, elm) {
                if (document.getElementsByClassName) {
                    getElementsByClassName = function(className, tag, elm) {
                        var current, elements, i, il, nodeName, returnElements;
                        elm = elm || document;
                        elements = elm.getElementsByClassName(className);
                        nodeName = (tag ? new RegExp("\\b" + tag + "\\b", "i") : null);
                        returnElements = [];
                        current = void 0;
                        i = 0;
                        il = elements.length;
                        while (i < il) {
                            current = elements[i];
                            if (!nodeName || nodeName.test(current.nodeName)) {
                                returnElements.push(current);
                            }
                            i += 1;
                        }
                        return returnElements;
                    };
                } else if (document.evaluate) {
                    getElementsByClassName = function(className, tag, elm) {
                        var classes, classesToCheck, elements, j, jl, namespaceResolver, node, returnElements, xhtmlNamespace;
                        tag = tag || "*";
                        elm = elm || document;
                        classes = className.split(" ");
                        classesToCheck = "";
                        xhtmlNamespace = "http://www.w3.org/1999/xhtml";
                        namespaceResolver = (document.documentElement.namespaceURI === xhtmlNamespace ? xhtmlNamespace : null);
                        returnElements = [];
                        elements = void 0;
                        node = void 0;
                        j = 0;
                        jl = classes.length;
                        while (j < jl) {
                            classesToCheck += "[contains(concat(' ', @class, ' '), ' " + classes[j] + " ')]";
                            j += 1;
                        }
                        try {
                            elements = document.evaluate(".//" + tag + classesToCheck, elm, namespaceResolver, 0, null);
                        } catch (e) {
                            elements = document.evaluate(".//" + tag + classesToCheck, elm, null, 0, null);
                        }
                        while ((node = elements.iterateNext())) {
                            returnElements.push(node);
                        }
                        return returnElements;
                    };
                } else {
                    getElementsByClassName = function(className, tag, elm) {
                        var classes, classesToCheck, current, elements, k, kl, l, ll, m, match, ml, returnElements;
                        tag = tag || "*";
                        elm = elm || document;
                        classes = className.split(" ");
                        classesToCheck = [];
                        elements = (tag === "*" && elm.all ? elm.all : elm.getElementsByTagName(tag));
                        current = void 0;
                        returnElements = [];
                        match = void 0;
                        k = 0;
                        kl = classes.length;
                        while (k < kl) {
                            classesToCheck.push(new RegExp("(^|\\s)" + classes[k] + "(\\s|$)"));
                            k += 1;
                        }
                        l = 0;
                        ll = elements.length;
                        while (l < ll) {
                            current = elements[l];
                            match = false;
                            m = 0;
                            ml = classesToCheck.length;
                            while (m < ml) {
                                match = classesToCheck[m].test(current.className);
                                if (!match) break;
                                m += 1;
                            }
                            if (match) returnElements.push(current);
                            l += 1;
                        }
                        return returnElements;
                    };
                }
                return getElementsByClassName(className, tag, elm);
            };
        });
    });

}).call(this);
