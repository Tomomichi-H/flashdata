import json

def get_oracle_info(params, redis_conn, logger):
    logger.debug("get_oracle_info with params %s", params)

    supported_data_points = []
    data_keys = redis_conn.keys("data:*")
    if data_keys is not None:
        for key in data_keys:
            dp = json.loads(redis_conn.get(key))
            supported_data_points.append({
                "dataPointID": dp["dataPointID"],
                "dataSource": dp["dataSource"],
                "updateFrequency": dp["updateFrequency"],
                "price": dp["price"]
            })

    oracle_info = {}
    info_keys = redis_conn.keys("oracle:*")
    if info_keys is not None:
        for key in info_keys:
            name = key.decode("utf-8").split(":")[1].strip()
            value = redis_conn.get(key)
            oracle_info[name] = value.decode("utf-8")

    response = {
        "result": {
            "oracle_info": oracle_info,
            "supported_data_points": supported_data_points
        }
    }

    return response

def request_data(params, redis_conn, logger):
    logger.debug("request_data with params %s", params)

    data_point_id = params.get("dataPointID", [])
    if not data_point_id:
        return {"error": "Invalid request: Missing dataPoint parameter"}

    data_point_data = redis_conn.get(data_point_id)
    if not data_point_data:
        return {"error": f"No data for dataPointID {data_point_id}"}

    return data_point_data
