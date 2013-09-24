function (doc, req) {
    // the list of doc_types is result of a grep of couchflow/models.py,
    // removing manually the ones that are DocumentSchema
    // or that are stored in different dbs
    var COUCHFLOW_TYPES = ['Task', 'MarcImport', 'DecisionTask', 'DynamicDataTask', 'ProcessTask', 'CloneItems', 'WFItemsLoader', 'FilterWFItems', 'Conector', 'WFItem', 'WorkFlow', 'SequenceConector', 'SimpleMergeConector', 'SyncConector', 'ExclusiveChoice', 'ParallelSplit', 'UntilConector', 'MultipleInstances', 'CirculationLog'];
    if (doc.doc_type && (COUCHFLOW_TYPES.indexOf(doc.doc_type) >= 0)) {
        if (req.query.no_clones) {
            if (doc.is_clone) {
                return false;
            } else if (req.query.couchflow == undefined) {
                // if the filter is just here for no_clones
                return true;
            }
        }
        return (req.query.couchflow == '1');
    } else {
        return (req.query.couchflow != '1')
    }
    return false;
}
