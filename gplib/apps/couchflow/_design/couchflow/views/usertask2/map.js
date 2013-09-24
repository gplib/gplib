function(doc) { 
    if (doc.task_type == true && doc.active == true && doc.enabled == true && doc.end == false && doc.is_clone == true && doc.wfitems_ids && doc.wfitems_ids.length && doc.visible != false){
      emit([doc.user_id, "task"],  {'_id': doc._id});
      emit([doc.group_id, "task"],  {'_id': doc._id});

      for (k in doc.wfitems_ids){
          emit([doc.user_id, k],  {'_id': doc.wfitems_ids[k]});
          emit([doc.group_id, k],  {'_id': doc.wfitems_ids[k]});
      }
    }
}
