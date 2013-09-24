function(doc) { 
  if (doc.doc_type=='CirculationLog')
    emit([doc.date.substring(0,7), doc.type], 1); 
}
