function(doc) { 
  if (doc.conector_type == true && doc.previous_tasks == 0 && doc.step == 1)
    emit(doc.workflow_id, null);
}
