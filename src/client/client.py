from flask import Flask, request, jsonify
import redis
import toml
import logging
import requests
from internal import add_data_point
from external import get_oracle_info, request_data

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
                logger.info("Stored oracle:identity_pubkey in Redis: %s", identity_pubkey)
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
            handler_output = handler(params, redis_conn, logger)
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
