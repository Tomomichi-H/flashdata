import json
import hashlib

def add_data_point(params, redis_conn, logger):
    logger.debug("add_data_point with params %s", params)

    data_point = params.get("dataPoint")

    if not data_point:
        return {"error": "Invalid request: Missing dataPoint parameter"}

    required_fields = ["dataSource", "updateFrequency", "price"]
    for field in required_fields:
        if field not in data_point:
            return {"error": f"Invalid request: Missing '{field}' field"}

    data_point_id = generate_data_point_id(data_point["dataSource"], data_point["updateFrequency"])
    data_point["dataPointID"] = data_point_id
    dp_data = json.dumps(data_point)
    redis_conn.set(f"data:{data_point_id}", dp_data)

    logger.debug("Added data point: %s", data_point)

    return {"dataPointID": data_point_id}

def generate_data_point_id(data_source, update_frequency):
    data_str = data_source + str(update_frequency)
    sha_signature = hashlib.sha256(data_str.encode()).hexdigest()
    return sha_signature
