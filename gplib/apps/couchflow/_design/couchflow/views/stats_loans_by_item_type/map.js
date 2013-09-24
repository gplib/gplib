function(doc) { 
  if (doc.doc_type=='CirculationLog' && doc.type == 'loan')
    emit([doc.date.substring(0,7), doc.item_type], 1); 
}
