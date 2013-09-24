function(doc) { 
  if (doc.doc_type=='WFItem' && doc.is_clone==false) 
    emit(doc.item_type, null);
}
