# Beacon v2 Production Reference Implementation 

This is an application that makes B2RI production ready. To go to the original B2RI product, please visit [B2RI](https://github.com/EGA-archive/beacon2-ri-api)

## Prerequisites

You should have installed:

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Light up the database and the Beacon

#### Up the containers

If you are using a build with all the services in the same cluster, you can use:

```bash
docker-compose up -d --build
```

#### Load the data

To load the database we execute the following commands:

```bash
docker cp /path/to/analyses.json mongoprod:tmp/analyses.json
docker cp /path/to/biosamples.json mongoprod:tmp/biosamples.json
docker cp /path/to/cohorts.json mongoprod:tmp/cohorts.json
docker cp /path/to/datasets.json mongoprod:tmp/datasets.json
docker cp /path/to/genomicVariations.json mongoprod:tmp/genomicVariations.json
docker cp /path/to/individuals.json mongoprod:tmp/individuals.json
docker cp /path/to/runs.json mongoprod:tmp/runs.json
```

```bash
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/datasets.json --collection datasets
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/analyses.json --collection analyses
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/biosamples.json --collection biosamples
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/cohorts.json --collection cohorts
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/genomicVariations.json --collection genomicVariations
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/individuals.json --collection individuals
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/runs.json --collection runs
```

This loads the JSON files inside of the `data` folder into the MongoDB database container. Each time you import data you will have to create indexes for the queries to run smoothly. Please, check the next point about how to Create the indexes.

#### Create the indexes

Remember to do this step every time you import new data!!

You can create the necessary indexes running the following Python script:

```bash
docker exec beacon python beacon/reindex.py
```

#### Fetch the ontologies and extract the filtering terms

> This step consists of analyzing all the collections of the Mongo database for first extracting the ontology OBO files and then filling the filtering terms endpoint with the information of the data loaded in the database.

You can automatically fetch the ontologies and extract the filtering terms running the following script:

```bash
 docker exec beaconprod python beacon/connections/mongo/extract_filtering_terms.py
```

#### Get descendant and semantic similarity terms

**If you have the ontologies loaded and the filtering terms extracted**, you can automatically get their descendant and semantic similarity terms by following the next two steps:

1. Add your .obo files inside [ontologies](../beacon/connections/mongo/ontologies) naming them as the ontology prefix in lowercase (e.g. ncit.obo) and rebuild the beacon container with:

2. Run the following script:

```bash
 docker exec beaconprod python beacon/connections/mongo/get_descendants.py
```

#### Check the logs

Check the logs until the beacon is ready to be queried:

```bash
docker-compose logs -f beaconprod
```

## Usage

You can query the beacon using GET or POST. Below, you can find some examples of usage:

> For simplicity (and readability), we will be using [HTTPie](https://github.com/httpie/httpie).

### Using GET

Querying this endpoit it should return the 13 variants of the beacon (paginated):

```bash
http GET http://localhost:5050/api/g_variants
```

You can also add [request parameters](https://github.com/ga4gh-beacon/beacon-v2-Models/blob/main/BEACON-V2-Model/genomicVariations/requestParameters.json) to the query, like so:

```bash
http GET http://localhost:5050/api/individuals?filters=NCIT:C16576,NCIT:C42331
```

### Using POST

You can use POST to make the previous query. With a `request.json` file like this one:

```json
{
    "meta": {
        "apiVersion": "2.0"
    },
    "query": {
        "requestParameters": {
    "alternateBases": "G" ,
    "referenceBases": "A" ,
"start": [ 16050074 ],
            "end": [ 16050568 ],
	    "referenceName": "22"
        },
        "filters": [],
        "includeResultsetResponses": "HIT",
        "pagination": {
            "skip": 0,
            "limit": 10
        },
        "testMode": false,
        "requestedGranularity": "record"
    }
}

```

You can execute:

```bash
curl \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "meta": {
        "apiVersion": "2.0"
    },
    "query": {
        "requestParameters": {
    "alternateBases": "G" ,
    "referenceBases": "A" ,
"start": [ 16050074 ],
            "end": [ 16050568 ],
	    "referenceName": "22"
        },
        "filters": [],
        "includeResultsetResponses": "HIT",
        "pagination": {
            "skip": 0,
            "limit": 10
        },
        "testMode": false,
        "requestedGranularity": "record"
    }
}' \
  http://localhost:5050/api/g_variants


```

But you can also use complex filters:

```json
{
    "meta": {
        "apiVersion": "2.0"
    },
    "query": {
        "filters": [
            {
                "id": "UBERON:0000178",
                "scope": "biosample",
                "includeDescendantTerms": false
            }
        ],
        "includeResultsetResponses": "HIT",
        "pagination": {
            "skip": 0,
            "limit": 10
        },
        "testMode": false,
        "requestedGranularity": "count"
    }
}
```

You can execute:

```bash
http POST http://localhost:5050/api/biosamples --json < request.json
```

And it will use the ontology filter to filter the results.

## Allowing authentication/authorization

Go to [auth folder](../beacon/auth/idp_providers) and create an .env file with the next Oauthv2 OIDC Identity Provider Relying Party known information:
```bash
CLIENT_ID='your_idp_client_id'
CLIENT_SECRET='your_idp_client_secret'
USER_INFO='https://login.elixir-czech.org/oidc/userinfo'
INTROSPECTION='https://login.elixir-czech.org/oidc/introspect'
ISSUER='https://login.elixir-czech.org/oidc/'
JWKS_URL='https://login.elixir-czech.org/oidc/jwk'
```

## Managing configuration

You can edit some parameters for your Beacon v2 API that are in [conf.py](../beacon/conf/conf.py). For that, edit the variables you see fit, save the file and restart the API by executing the next command:

```bash
docker-compose restart beaconprod
```

## Managing source

You can edit some parameters concerning entry types developed for your Beacon in [manage.py](../beacon/source/manage.py). For that, change to True the entry types you want to have developed and shown with data for your beacon and execute the next command:

```bash
docker-compose restart beaconprod
```


