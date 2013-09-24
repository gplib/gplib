function(doc) { 
  if (doc.doc_type == "User") 
    emit(doc._id, doc); 
}