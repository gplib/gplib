function(doc) { 
  if (doc.doc_type == "WFItem" && doc.is_clone == true){
    var reserves = doc.reserves;
    if(reserves){
        for(k in reserves){
            var reserve = reserves[k];
            emit([reserve.user_id, reserve.start, reserve.end], null);
        }
    }
  }
}
