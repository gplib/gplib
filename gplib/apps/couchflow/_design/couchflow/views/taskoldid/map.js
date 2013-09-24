function(doc) { 
   if (doc.task_type == true && doc.old_id != null && doc.is_clone == false) 
      emit(doc.old_id, null);
}
