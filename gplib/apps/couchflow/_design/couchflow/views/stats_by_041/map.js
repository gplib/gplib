function(doc) {
  // !code common/field_utils.js

  if (doc.doc_type=='WFItem' && doc.is_clone==true){
    var field = get_field("99989");

    if(field && field[0] == "catalogado"){
        var f041 = get_field("041");
        if(f041 && f041[0]){
            emit(f041[0], 1);
        }
    }
  }
}
