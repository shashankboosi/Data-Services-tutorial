# Data Services Tutorial

## Tutorial 1 (Data Play - Pandas)

    This directory consists of first send of tasks required for Data Services, which are 
    Data Ingestion, Manipulation and Visualization

## Tutorial 2 (API play - Flask Restplus)
    
### Task 1

The service will download the JSON data for all countries respective to the year 2012 to 2017 and identified by the indicator id given by the user and process the content into an internal data format and store it in the database; use sqlite for storing the data

**Curl command**: `curl -X POST "http://127.0.0.1:5000/collections/?indicator_id=NY.GDP.MKTP.CD" -H "accept: application/json"`    

**Request URL**: `POST` `/collections/?indicator_id=NY.GDP.MKTP.CD`

**Output**: 
    
```
{
  "uri": "/collections/2",
  "id": "2",
  "creation_time": "2020-04-04T16:08:03.323419",
  "indicator_id": "NY.GDP.MKTP.CD"
}
```

### Task 2

This task deletes an existing collection from the database

**Curl command**: `curl -X DELETE "http://127.0.0.1:5000/collections/1" -H "accept: application/json"`    

**Request URL**: `DELETE ` `/collections/1`

**Output**: 
    
```
{
  "message": "The collection 1 was removed from the database!",
  "id": "1"
}
```

### Task 3

This task retrieves all available collections. **order_by** is a comma separated string value to sort the collection based on the given criteria. Each segment of this value indicates how the collection should be sorted, and it consists of two parts (+ or -, and the name of column e.g., id). In each segment, + indicates ascending order, and - indicates descending order.

**Curl command**: `curl -X GET "http://127.0.0.1:5000/collections/?order_by=%2Bid%2C%20-creation_time" -H "accept: application/json"`    

**Request URL**: `GET` `http://127.0.0.1:5000/collections/?order_by=%2Bid%2C%20-creation_time`

**Output**: 
    
```
[
  {
    "uri": "/collections/1",
    "id": 1,
    "creation_time": "1.0.HCount.2.5usd",
    "indicator": "2020-04-04T16:07:50.956829"
  },
  {
    "uri": "/collections/2",
    "id": 2,
    "creation_time": "NY.GDP.MKTP.CD",
    "indicator": "2020-04-04T16:08:03.323419"
  }
]
```


### Task 4

This operation retrieves a collection by its ID . The response of this operation will show the imported content from world bank API for all 6 years.

**Curl command**: `curl -X GET "http://127.0.0.1:5000/collections/1" -H "accept: application/json"`    

**Request URL**: `GET` `http://127.0.0.1:5000/collections/1`

**Output**: 
    
```
{
  "id": 1,
  "indicator": "1.0.HCount.2.5usd",
  "indicator_value": "Poverty Headcount ($2.50 a day)",
  "creation_time": "2020-04-04T16:07:50.956829",
  "entries": [
    {
      "country": "Andean Region",
      "date": "2014",
      "value": 12.0147485733032
    },
    {
      "country": "Andean Region",
      "date": "2013",
      "value": 12.7574424743652
    },
    {
      "country": "Andean Region",
      "date": "2012",
      "value": 14.7959203720093
    },
    {
      "country": "Argentina",
      "date": "2014",
      "value": 5.40922260284424
    }
    ...
  ]
}
```

### Task 5

Retrieve economic indicator value for given country and a year

**Curl command**: `curl -X GET "http://127.0.0.1:5000/collections/2/2016/World" -H "accept: application/json"`    

**Request URL**: `GET` `http://127.0.0.1:5000/collections/2/2016/World`

**Output**: 
    
```
{
  "id": 2,
  "indicator": "NY.GDP.MKTP.CD",
  "country": "World",
  "year": "2016",
  "value": 76163840829219.8
}
```

### Task 6

Retrieve top/bottom economic indicator values for a given year. The example below shows the top 10 indicator values for collection `id` 2

**Curl command**: `curl -X GET "http://127.0.0.1:5000/collections/1/2012/?q=%2B10" -H "accept: application/json"`    

**Request URL**: `GET` `http://127.0.0.1:5000/collections/1/2012/?q=%2B10`

**Output**: 
    
```
{
  "indicator": "1.0.HCount.2.5usd",
  "indicator_value": "Poverty Headcount ($2.50 a day)",
  "entries": [
    {
      "country": "Honduras",
      "value": 42.4187431335449
    },
    {
      "country": "Central America",
      "value": 24.932918548584
    },
    {
      "country": "Colombia",
      "value": 17.5397624969482
    },
    {
      "country": "Bolivia",
      "value": 17.1273899078369
    },
    {
      "country": "Andean Region",
      "value": 14.7959203720093
    },
    {
      "country": "El Salvador",
      "value": 14.6787967681885
    },
    {
      "country": "Dominican Republic",
      "value": 14.5516204833984
    },
    {
      "country": "Ecuador",
      "value": 12.8523483276367
    },
    {
      "country": "Latin America and the Caribbean",
      "value": 12.1378555297852
    },
    {
      "country": "Paraguay",
      "value": 12.0395565032959
    }
  ]
}
```

## Tutorial 3