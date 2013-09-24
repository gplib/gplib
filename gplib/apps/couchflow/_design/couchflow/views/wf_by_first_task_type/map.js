function(doc) { 
  if (doc.doc_type == "WorkFlow" && doc.is_clone == false && doc.first_task_type){
    emit(doc.first_task_type, {"_id": doc.first_task_id});
    emit(doc.first_task_type, {"_id": doc._id});
  }
}
