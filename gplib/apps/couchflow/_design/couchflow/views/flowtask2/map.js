function(doc) { 
    if (doc.task_type == true && doc.active && doc.wfitems_ids && doc.wfitems_ids.length && doc.visible != false){
      emit(doc.workflow_id,  {'_id': doc._id});

      for (k in doc.wfitems_ids){
          emit(doc.workflow_id,  {'_id': doc.wfitems_ids[k]});
      }
    }
}
