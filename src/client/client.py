from flask import Flask, request, jsonify
import redis
import json
import hashlib
import toml
import logging
import requests

app = Flask(__name__)
redis_conn = None
logger = logging.getLogger(__name__)

def load_config():
    config = toml.load("config.toml")
    return config

def initialize_redis(config):
    global redis_conn
    redis_conn = redis.Redis(
        host=config["redis"]["host"],
        port=config["redis"]["port"],
        db=config["redis"]["db"]
    )

    # Fetch LND info and store identity_pubkey in Redis
    lnd_host = config["lnd"]["host"]
    lnd_port = config["lnd"]["port"]
    lnd_url = f"http://{lnd_host}:{lnd_port}"
    if lnd_url:
        try:
            logger.info("Connecting to LND at: %s", lnd_url)
            response = requests.get(f"{lnd_url}/v1/getinfo")
            response_data = response.json()
            identity_pubkey = response_data.get("identity_pubkey")
            if identity_pubkey:
                redis_conn.set(f"oracle:identity_pubkey", identity_pubkey)
                logger.info("Stored identity_pubkey in Redis: %s", identity_pubkey)
        except Exception as e:
            logger.exception("Failed to fetch LND info: %s", str(e))
    else:
        logger.warning("LND URL not specified in config.toml")

@app.route('/', methods=['POST'])
def handle_json_rpc():
    data = request.get_json()
    logger.info("Received JSON-RPC request: %s", data)

    if 'method' not in data or 'id' not in data:
        logger.error("Invalid JSON-RPC request")
        return jsonify({"error": "Invalid JSON-RPC request"}), 400

    method = data['method']
    params = data.get('params', {})
    request_id = data['id']

    handler = METHOD_HANDLERS.get(method)
    response = {
        'jsonrpc': '2.0',
        'id': request_id
    }
    if handler is None:
        logger.error("Method not found: %s", method)
        response["error"] = "Method not found"
    else:
        try:
            handler_output = handler(params)
            logger.debug("handler_output, %s", handler_output)
            if "error" in handler_output:
                logger.error("Error executing method: %s", handler_output["error"])
                response["error"] = handler_output["error"]
            else:
                response["result"] = handler_output
        except Exception as e:
            logger.exception("Error executing method: %s", str(e))
            response["error"] = "Internal server error"

    logger.info("Sending JSON-RPC response: %s", response)
    return jsonify(response)

def get_oracle_info(params):
    logger.debug("get_oracle_info with params %s", params)
    supported_data_points = []
    for key in redis_conn.keys("data:*"):
        dp = json.loads(redis_conn.get(key))
        supported_data_points.append({
            "dataPointID": dp["dataPointID"],
            "dataSource": dp["dataSource"],
            "updateFrequency": dp["updateFrequency"],
            "price": dp["price"]
        })

    identity_pubkey = redis_conn.get("oracle:identity_pubkey")
    logger.info("Identity pubkey: %s", identity_pubkey)
    response = {
        "result": {
            "identity_pubkey": identity_pubkey.decode() if identity_pubkey else None,
            "supported_data_points": supported_data_points
        }
    }

    return response

def request_data(params):
    logger.debug("request_data with params %s", params)
    data_point_id = params.get("dataPointID", [])
    if not data_point_id:
        return {"error": "Invalid request: Missing dataPoint parameter"}
    data_point_data = redis_conn.get(data_point_id)
    if not data_point_data:
        return {"error": f"No data for dataPointID {data_point_id}"}
    return data_point_data

def add_data_point(params):
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
    logger.debug("Added data point: %s", data_point)
    redis_conn.set(f"data:{data_point_id}", dp_data)

    return {"dataPointID": data_point_id}

def generate_data_point_id(data_source, update_frequency):
    data_str = data_source + str(update_frequency)
    sha_signature = hashlib.sha256(data_str.encode()).hexdigest()
    return sha_signature

# Mapping of method names to handler functions
METHOD_HANDLERS = {
    'getOracleInfo': get_oracle_info,
    'requestData': request_data,
    'addDataPoint': add_data_point
}

if __name__ == '__main__':
    config = load_config()

    # Configure logging
    log_level = config.get("logging", {}).get("level", "INFO")
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level)
    logger.setLevel(numeric_level)

    initialize_redis(config)
    app.run(debug=True, host=config["flask"]["host"], port=config["flask"]["port"])
