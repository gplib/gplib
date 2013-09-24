function(doc) { 
    if (doc.conector_type == true)
      emit(doc.workflow_id, null);
}
