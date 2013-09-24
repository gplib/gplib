// Included from field_utils.js
  function get_field(field, subfield){
    var fps = doc["fields_properties"];

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
                    return value;
                }
            }
        }
     }
  }
