function(doc) { 
    if (doc.task_type == true && doc.active == true && doc.enabled == true && doc.end == false)
      emit(doc.workflow_id, null);
}
