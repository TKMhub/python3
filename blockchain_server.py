from flask import Flask
from flask import jsonify
from flask import request

import blockchain
import wallet
import json

app = Flask(__name__)

cache = {}

def get_blockchain():
    cached_blockchain = cache.get('blockchain')
    if not cached_blockchain:
        miners_wallet = wallet.Wallet()
        cache['blockchain'] = blockchain.BlockChain(
            miners_wallet.blockchain_address,
            port=app.config['port']
        )
        app.logger.warning({
            'private_key': miners_wallet.private_key,
            'public_key': miners_wallet.public_key,
            'blockchain_address': miners_wallet.blockchain_address
        })
    return cache['blockchain']


@app.route('/chain', methods=['GET'])
def get_chain():
    block_chain = get_blockchain()
    response = {
        'chain': block_chain.chain
    }
    return jsonify(response), 200

@app.route('/transactions', methods=['GET', 'POST', 'PUT', 'DELETE'])
def transaction():
    block_chain = get_blockchain()
    if request.method == 'GET':
        transactions = block_chain.transaction_pool
        response = {
            'transactions': transactions,
            'length': len(transactions)
        }
        return jsonify(response), 200

    if request.method == 'POST':
        request_json = request.json
        required = (
            'sender_blockchain_address'
            'recipient_blockchain_address',
            'sender_public_key',
            'value',
            'signature')
        if not all(k in request_json for k in required):
            return jsonify({'message', 'missing values'}), 400

        is_created = block_chain.create_transaction(
            request_json['sender_blockchain_address'],
            request_json['recipient_blockchain_address'],
            request_json['sender_public_key'],
            request_json['value'],
            request_json['signature'],
        )
        if not is_created:
            return jsonify({'message': 'fall'}), 400
        return jsonify({'message': 'success'}), 201

    if request.method == 'PUT':
        request_json = request.json
        required = (
            'sender_blockchain_address'
            'recipient_blockchain_address',
            'sender_public_key',
            'value',
            'signature')
        if not all(k in request_json for k in required):
            return jsonify({'message', 'missing values'}), 400

        is_update = block_chain.add_transaction(
            request_json['sender_blockchain_address'],
            request_json['recipient_blockchain_address'],
            request_json['sender_public_key'],
            request_json['value'],
            request_json['signature'],
        )
        if not is_update:
            return jsonify({'message': 'fall'}), 400
        return jsonify({'message': 'success'}), 200

    if request.method == 'DELETE':
        block_chain.transaction_pool = []
        return jsonify({'message': 'success'}), 200


@app.route('/mine', methods=['GET'])
def mine():
    block_chain = get_blockchain()
    is_mind = block_chain.mining()
    if is_mind:
        return jsonify({'message': 'success'}), 200
    return jsonify({'message': 'fail'}), 400


@app.route('/mine/start', methods=['GET'])
def start_mine():
    get_blockchain().start_minig()
    return jsonify({'message': 'success'}), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5002,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.config['port'] = port

    get_blockchain().sync_neighbours()

    app.run(host='0.0.0.0', port=port, threaded=True, debug=True)
