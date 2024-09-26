from beacon.connections.mongo.g_variants import get_variants
from beacon.connections.mongo.individuals import get_individuals
from beacon.connections.mongo.analyses import get_analyses
from beacon.connections.mongo.biosamples import get_biosamples
from beacon.connections.mongo.runs import get_runs
import asyncio
from concurrent.futures import ThreadPoolExecutor
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from typing import Optional
from beacon.request.parameters import RequestParams

@log_with_args(level)
async def execute_function(self, entry_type: str, datasets: list, qparams: RequestParams, entry_id: Optional[str]):
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    datasets_docs={}
    datasets_count={}
    new_count=0
    if entry_type == 'genomicVariations':
        function=get_variants
    elif entry_type == 'individuals':
        function=get_individuals
    elif entry_type == 'analyses':
        function=get_analyses
    elif entry_type == 'biosamples':
        function=get_biosamples
    elif entry_type == 'runs':
        function=get_runs
    loop = asyncio.get_running_loop()

    if datasets != [] and include != 'NONE':
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, entry_id, qparams, dataset) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            entity_schema, count, dataset_count, records, dataset = task.result()
            if dataset_count != -1:
                new_count+=dataset_count
                datasets_docs[dataset]=records
                datasets_count[dataset]=dataset_count
        
        count=new_count
    
    else:
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, entry_id, qparams, dataset) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            entity_schema, count, dataset_count, records, dataset = task.result()
        datasets_docs["NONE"]=records
        if limit == 0 or new_count < limit:
            pass
        else:
            count = limit
        datasets_count["NONE"]=count
    return datasets_docs, datasets_count, count, entity_schema, include