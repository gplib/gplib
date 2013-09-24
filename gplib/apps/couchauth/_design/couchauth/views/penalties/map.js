function(doc) { 
    if (doc.doc_type == "User") {
        for (var p in doc.penalties) {
            emit(doc.username, doc.penalties[p]);
        }
    } 
}
