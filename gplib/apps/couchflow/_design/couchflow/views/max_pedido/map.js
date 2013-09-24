function(doc) { 
    if(doc.order_nbr){
      emit(doc.order_nbr,  null); 
    }
}
