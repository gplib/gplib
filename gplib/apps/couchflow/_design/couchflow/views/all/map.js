function(doc) { 
  if (doc.doc_type == "WorkFlow") 
    emit(doc._id, null);
}
