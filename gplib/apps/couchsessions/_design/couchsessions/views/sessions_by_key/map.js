function(doc)
{
    if (doc.doc_type == 'Session')
    {
        emit(doc.session_key, null);
    }
}
