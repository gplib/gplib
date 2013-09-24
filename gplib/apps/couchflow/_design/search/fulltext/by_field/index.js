/* the indentation in this file is awful */
function (doc){
   if(doc.doc_type == "WFItem" && doc.is_clone == true){
     var fps = eval(doc["fields_properties"].toSource());

     // Shamelessly copypasted from field_utils.js, since we hit the death bug
     // includes stealth bugfixes for urn
     function get_field(field, subfield){
       // use fps from the upper function
       if(fps && fps[field]){
           var fp = fps[field];
           if(fp && fp['list']){
               // TODO: make posible to get all fields
               fp = fp['list'][0]
           }
           if(subfield == null){
               if(fp && fp["exec_value"]){
                   return fp["exec_value"];
               }
           }else{
               if(fp && fp["subfields"]){
                   var sfp = fp["subfields"][subfield];
                   if(sfp && sfp["exec_value"]){
                       var value = sfp["exec_value"];
                       if (value.length) return value[0];
                   }
               }
           }
        }
     }

     // TODO: check why it's not a list
     var state = fps['99989']['list'][0]['exec_value'];
     if(state && state[0]){
        state = state[0];
     }
     if(state != 'catalogado' && (doc.reference != true || state != "activo")){
         log.info("El documento no esta catalogado: "+state);
         return;
     }
     var ret = new Document();

     ret.add(doc.name, {field: 'item_name'});
     ret.add(doc.item_type, {field: 'item_type'});

     var urn = "";
     if (!doc.reference) {
         var urn_config = doc['urn_config'];
         var urn = "";
         for (i in urn_config) {
             urn += (get_field(urn_config[i].field, urn_config[i].subfield) || "-");
         }
         if (urn.replace(/-/g, "").length == 0) {
             urn = "";
             log.info("urn null");
         }
     } else {
        // if the document is a reference use the doc._id as urn
        urn = doc._id;
     }

     if (urn) {
         ret.add(urn, {"field": "urn", "store": "yes"});
     }

     // Tell if the doc is existence or master field
     var existence = get_field("1111");
     if(existence && existence[0]){
        existence = existence[0];
     }
     existence = existence == "existencia" || false;
     ret.add(existence, {"field": "existence", "store": "yes"});

     if(doc.reference){
         ret.add(true, {"field": "reference", "store": "yes"});
     }else{
         // Compatibility with old items
         ret.add(false, {"field": "reference", "store": "yes"});
     }

     for(field in doc["fields_properties"]){

       // TODO: make posible to get all fields
       fp = fps[field]['list'][0];
       if(fp["subfields"]){
         for(sfield in fp["subfields"]){
           var sfp = fp["subfields"][sfield];
           for(value in sfp['exec_value']){
             value = sfp['exec_value'][value];
             var field_id = fps[field]['id'] +"_"+ sfp["field_name"];

             if(value){
                d = {"field": field_id, "store": "no"}
                if (sfp['type'] == 'date') {
                    d['type'] = 'date';
                }
                ret.add(value, d);
             }
           }
         }
       }

       if(fp['exec_value']){
         for(key in fp['exec_value']){
           value = fp['exec_value'][key];
           if(value){
             d = {"field": fps[field]["id"]}
             if (fps[field]['type'] == 'date') {
               d['type'] = 'date';
               value = new Date(value);
             }
             ret.add(value, d);
           }
         }
       }

     }
     return ret;
   }
}
