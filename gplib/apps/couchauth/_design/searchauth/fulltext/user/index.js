function (doc){
   if(doc.doc_type == "User" && doc.is_staff != true){ // && doc.is_staff != true && doc.is_superuser != true){
     //log.info("USER:");
     //log.info(doc.is_staff);
     var ret = new Document();

     ret.add(doc.username)//, {field: 'username'});
     ret.add(doc.first_name)//, {field: 'first_name'});
     ret.add(doc.last_name)//, {field: 'last_name'});
     ret.add(doc.document_number, {field: 'document_number'});
     ret.add(doc.email, {field: 'email'});

     return ret;
   }
}
