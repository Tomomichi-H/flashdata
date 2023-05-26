# Oracle Node Client API Specification

This API is a JSON-RPC API which Oracle Nodes expose to Aggregator Services.

## Methods

### getOracleInfo

Obtain information about the oracle node including the data it supports.

#### Request

    ```json
    {
      "method": "getOracleInfo",
      "params": [],
      "id": 1
    }
    ```

#### Response

    ```json
    {
      "result": {
        "id": "<node_id>",
        "supportedDataPoints": [
          {
            "dataPointID": "<data_point_id_1>",
            "dataPoint": "<data_point_1>",
            "dataSource": "<data_source_1>",
            "updateFrequency": "<update_frequency_1>",
            "price": "<price_in_millisatoshis>"
          },
          ...
        ]
      },
      "error": null,
      "id": 1
    }
    ```

### requestData

Request data from a specific data point.

#### Request

    ```json
    {
      "method": "requestData",
      "params": ["<data_point_id>"],
      "id": 1
    }
    ```

#### Response

    ```json
    {
      "result": {
        "dataPointID": "<data_point_id>",
        "data": "<data>"
      },
      "error": null,
      "id": 1
    }
    ```

## Errors

- If the requested data point is not supported by the Oracle Node, the `error` field in the response will contain a message indicating that the data point is not supported.

    ```json
    {
      "result": null,
      "error": "Requested data point is not supported.",
      "id": 1
    }
    ```
