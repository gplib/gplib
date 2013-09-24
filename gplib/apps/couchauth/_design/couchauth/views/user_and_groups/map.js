function(doc) {
    if (doc.doc_type == "User") {
        emit([doc.username, 0], null);
        for (var i in doc.groups) {
            emit([doc.username, 1], {_id: doc.groups[i]});
        }
    }
}
