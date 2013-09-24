/*
Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
    // Define changes to default configuration here. For example:
    config.language = 'es';
    // config.uiColor = '#AADC6E';
    config.toolbar = 'custom'
    config.toolbar_custom = [
        { name: 'document',	items : [ 'Source', 'Save'] },
        { name: 'clipboard',	items : [ 'Cut','Copy','Paste','PasteText','-','Undo','Redo' ] },
        { name: 'editing',	items : [ 'Find','Replace','-','SelectAll'] },
        '/',
        { name: 'basicstyles',	items : [ 'Bold','Italic','Underline','Strike','-','RemoveFormat' ] },
        { name: 'paragraph',	items : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'] },
        { name: 'links',	items : [ 'Link','Unlink','Anchor' ] },
        { name: 'insert',	items : [ 'Image','Table','HorizontalRule','SpecialChar'] },
        '/',
        { name: 'styles',	items : [ 'Styles','Format','Font','FontSize' ] },
        { name: 'colors',	items : [ 'TextColor','BGColor' ] },
        { name: 'tools',	items : [ 'Maximize', 'ShowBlocks','-','About' ] }
    ];
};
