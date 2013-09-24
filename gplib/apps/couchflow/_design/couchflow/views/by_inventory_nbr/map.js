function(doc) {
  // !code common/field_utils.js

  if (doc.doc_type=='WFItem' && doc.is_clone==true){
      var field = get_field("876", "a");
      if(field && field[0]) {
          emit(field[0], null);
      }
  }
}
