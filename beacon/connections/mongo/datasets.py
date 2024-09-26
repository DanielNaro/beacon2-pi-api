from beacon.connections.mongo.__init__ import client
from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.exceptions.exceptions import raise_exception
from beacon.connections.mongo.utils import get_count
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams

@log_with_args_mongo(level)
def get_datasets(self):
    try:
        collection = client.beacon.datasets
        query = {}
        query = collection.find(query)
        return query
    except Exception as e:# pragma: no cover
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args_mongo(level)
def get_full_datasets(self, entry_id: Optional[str], qparams: RequestParams):
    try:
        collection = client.beacon.datasets
        if entry_id == None:
            query = {}
        else:# pragma: no cover
            query = {'id': entry_id}
        count = get_count(self, client.beacon.datasets, query)
        query = collection.find(query)
        entity_schema = DefaultSchemas.DATASETS
        return query, count, entity_schema
    except Exception as e:# pragma: no cover
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args_mongo(level)
def get_list_of_datasets(self):
    try:
        datasets = get_datasets(self)
        beacon_datasets = [ r for r in datasets ]
        return beacon_datasets
    except Exception as e:# pragma: no cover
        err = str(e)
        errcode=500
        raise_exception(err, errcode)