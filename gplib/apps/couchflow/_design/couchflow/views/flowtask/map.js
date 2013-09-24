function(doc) { 
    if (doc.task_type == true)
      emit(doc.workflow_id, null);
}
