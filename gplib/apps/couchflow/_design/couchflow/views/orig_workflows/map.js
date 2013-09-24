function(doc) { 
  if (doc.doc_type == "WorkFlow" && doc.is_clone == false) 
    emit(doc.workflow_type, null);
}
