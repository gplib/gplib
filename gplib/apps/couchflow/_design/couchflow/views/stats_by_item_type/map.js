function(doc) {
  // !code common/field_utils.js

  if (doc.doc_type=='WFItem' && doc.is_clone==true){
    var field = get_field("99989");

    if(field && field[0] == "catalogado"){
        emit(doc.item_type, 1)
    }
  }
}
