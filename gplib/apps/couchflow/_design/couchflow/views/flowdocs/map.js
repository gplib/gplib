function(doc) { 
    if (doc.is_clone == false)
      emit(doc.workflow_id, null);
}
