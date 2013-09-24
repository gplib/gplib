function(doc) {
    if (doc.doc_type == "WFItem" && doc.is_clone == true){
        fields_p = doc.fields_properties;
        if(fields_p["99989"]){
            var field_p = fields_p["99989"];
            if(field_p['list']){
                field_p = field_p['list'][0];
                if(field_p && field_p['exec_value']){
                    emit(field_p['exec_value'][0], null);
                }
            }
        }
    }
}
