function(doc) { 
    if (doc.task_type == true && doc.have_until == true && doc.is_clone == true){
       emit(doc.workflow_id,  doc); 
    }
}