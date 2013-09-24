function(doc) {
  if (doc.doc_type == "WFItem" && doc.is_clone == true){
    var loan = doc.loan;
    if(loan){
        emit([loan.user_id, loan.start, loan.end], null);
    }
  }
}
