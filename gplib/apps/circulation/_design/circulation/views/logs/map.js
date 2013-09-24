function(doc) { 
    if (doc.doc_type == 'CirculationLog') {
        emit([doc.user_id, doc.timestamp_added, doc._id], {'_id': doc._id});
        emit([doc.user_id, doc.timestamp_added, doc._id], {'_id': doc.user_id});
        emit([doc.user_id, doc.timestamp_added, doc._id], {'_id': doc.item_id});
    }
}
