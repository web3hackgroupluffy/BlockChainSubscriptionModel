from flask import Flask, render_template, request, jsonify
from web3 import Web3

app = Flask(__name__)

# Connect to Ganache
ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    address = data.get('address')

    if not web3.isAddress(address):
        return jsonify({'error': 'Invalid address'}), 400
    return jsonify({'message': 'Address verified successfully'}), 200
