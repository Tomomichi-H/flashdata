import json
import hashlib

def add_data_point(params, redis_conn, logger):
    logger.debug("add_data_point with params %s", params)

    required_fields = ["dataSource", "updateFrequency", "price"]
    for field in required_fields:
        if field not in params:
            return {"error": f"Invalid request: Missing '{field}' field"}

    data_point_id = generate_data_point_id(params["dataSource"], params["updateFrequency"])
    params["dataPointID"] = data_point_id
    dp_data = json.dumps(params)
    redis_conn.set(f"data:{data_point_id}", dp_data)

    logger.debug("Added data point: %s", params)

    return {"dataPointID": data_point_id}

def generate_data_point_id(data_source, update_frequency):
    data_str = data_source + str(update_frequency)
    sha_signature = hashlib.sha256(data_str.encode()).hexdigest()
    return sha_signature
