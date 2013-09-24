function(doc) {
  // !code common/field_utils.js

  if (doc.doc_type=='WFItem' && doc.is_clone==true){
    var field = get_field("99989");

    if(field && field[0] == "catalogado"){
        var f072 = get_field("072");
        if(f072 && f072[0]){
            emit(f072[0], 1);
        }
    }
  }
}
