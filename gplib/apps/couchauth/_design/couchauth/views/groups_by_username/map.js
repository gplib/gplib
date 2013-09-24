function(doc) {
    if (doc.doc_type == "User") {
        for (var i in doc.groups) {
            emit(doc.username, {_id: doc.groups[i]});
        }
    }
}
