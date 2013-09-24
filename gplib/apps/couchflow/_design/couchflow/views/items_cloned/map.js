function(doc) {
  if (doc.doc_type=='WFItem' && doc.is_clone==true)
    emit(doc._id, null);
}
