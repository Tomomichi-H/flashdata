import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/v1/getinfo', methods=['GET'])
def get_info():
    logger.info("Received GET request for /v1/getinfo")

    response_data = {
        "version": "<string>",
        "commit_hash": "<string>",
        "identity_pubkey": "<string>",
        "alias": "<string>",
        "color": "<string>",
        "num_pending_channels": "<uint32>",
        "num_active_channels": "<uint32>",
        "num_inactive_channels": "<uint32>",
        "num_peers": "<uint32>",
        "block_height": "<uint32>",
        "block_hash": "<string>",
        "best_header_timestamp": "<int64>",
        "synced_to_chain": "<bool>",
        "synced_to_graph": "<bool>",
        "testnet": "<bool>",
        "chains": "<Chain>",
        "uris": "<string>",
        "features": "<FeaturesEntry>",
        "require_htlc_interceptor": "<bool>",
        "store_final_htlc_resolutions": "<bool>"
    }

    logger.info("Sending response data for /v1/getinfo")
    return jsonify(response_data)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host="0.0.0.0", port="8080")
