function(doc) {
    if (doc.doc_type == "User") {
        if (doc.groups.length) {
            for (var g in doc.groups) {
                emit([doc.date_joined.substring(0,7), doc.groups[g]], 1)
            }
        } else {
            emit([doc.date_joined.substring(0,7), null], 1)
        }
    }
} 
