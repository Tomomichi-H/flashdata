# FlashData: Data Normalizing Modules Technical Document

## Purpose of Data Normalizing Modules

Data Normalizing Modules are an essential component of the FlashData decentralized oracle network. These modules perform the task of normalizing request and response formats across various data sources, ensuring uniformity in the data that Oracle Nodes handle, regardless of the source of the data.

In a landscape where data sources are varied and distributed, each source might have its unique format for representing data. This variation presents a challenge for Oracle Nodes that need to understand and process data from numerous sources. Data Normalizing Modules exist to mediate this challenge. They act as a bridge between Oracle Nodes and data sources, translating the disparate data formats into a standard representation that Oracle Nodes can process consistently.

By utilizing Data Normalizing Modules, Oracle Nodes can operate in a uniform manner, uninfluenced by the individual characteristics of the underlying data source. This function contributes to the scalability, reliability, and overall robustness of the FlashData network.

## Data Normalizing Module Specification

Data Normalizing Modules communicate with Oracle Nodes using the JSON-RPC 2.0 protocol, a lightweight, transport-agnostic remote procedure call (RPC) protocol.

**Request Format**

Oracle Nodes send requests to the modules in the following JSON-RPC 2.0 format:

    ```json
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getData",
        "params": {
            "dataSource": "string",
            "dataPoint": "string"
        }
    }
    ```

In this request, `jsonrpc` and `id` follow the JSON-RPC 2.0 specification. The `method` represents the RPC method being called, while `params` contains `dataSource` and `dataPoint`. The `dataSource` represents the name of the data provider or source, while `dataPoint` is the specific data point required from the source.

**Response Format**

Data Normalizing Modules respond to Oracle Nodes in the following JSON-RPC 2.0 format:

    ```json
    {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "dataSource": "string",
            "dataPoint": "string",
            "value": "string",
            "timestamp": "string"
        }
    }
    ```

In this response, `jsonrpc` and `id` are compliant with the JSON-RPC 2.0 specification. The `result` contains `dataSource`, `dataPoint`, `value`, and `timestamp`. The `value` represents the resulting data from the data source corresponding to the request, and `timestamp` indicates when the data was retrieved.

The `value` field in the `result` object is always present, and it contains the normalized data value fetched from the data source. The location of `value` within the `result` object is fixed and predictable.

**Error Handling**

When a requested `dataPoint` isn't supported by a Data Normalizing Module, it will respond with a JSON-RPC 2.0 error message:

    ```json
    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32602,
            "message": "Invalid dataPoint",
            "data": "string indicating the dataPoint that was requested"
        }
    }
    ```

In this error message, `jsonrpc` and `id` are as per the JSON-RPC 2.0 specification. `code` is the error code specified by JSON-RPC 2.0 for Invalid Params, `message` gives a short description of the error, and `data` provides additional information about the error.
