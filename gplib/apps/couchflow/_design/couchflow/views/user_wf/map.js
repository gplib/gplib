function(doc) { 
  if (doc.doc_type == "WorkFlow" && doc.is_clone == true && doc.enabled == true) 
    emit(doc.user_id, null);
}
