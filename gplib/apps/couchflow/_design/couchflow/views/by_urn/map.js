function(doc) {
  // !code common/field_utils.js

  if (doc.doc_type=='WFItem' && doc.is_clone==true){
    // TODO: set urn properly using urn_config

    var field = get_field("99989");
    if(field && field[0] == "catalogado"){
        var urn_config = doc['urn_config'];
        var urn = "";
        for (i in urn_config) {
            urn += (get_field(urn_config[i].field, urn_config[i].subfield)[0] || "-")
        }
        if (urn.replace(/-/g, "").length != 0) {
            emit(urn, null);
        }
    }
  }
}
