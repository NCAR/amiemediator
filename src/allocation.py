from amieparms import (AMIEParmDescAware, process_parms)

class UpdateAllocation(AMIEParmDescAware,dict):

    @process_parms(
        allowed=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'resource_name',
            'requested_resource',
            'requested_amount',
            'AllocationType',
            'EndDate',
            'ProjectID',
            'ServiceUnitsAllocated',
            'StartDate',
            ],
        required=[
            'amie_transaction_id',
            'amie_packet_id',
            'job_id',
            'amie_packet_type',
            'task_name',
            'timestamp',

            'resource_name',
            'requested_resource',
            'requested_amount',
            'AllocationType',
            'EndDate',
            'ProjectID',
            'ServiceUnitsAllocated',
            'StartDate',
            ])
    def __init__(self, *args, **kwargs):
        """Validate, filter, and transform arguments to ``update_allocation()``"""
        dict.__init__(self, **kwargs)


