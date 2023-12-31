from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, send_file, session, flash
from web3 import Web3
import os
from werkzeug.utils import secure_filename
from moralis import auth
import requests
import json
from flask_cors import CORS

UPLOAD_FOLDER = 'uploads'  # Set the path to the upload directory
ALLOWED_EXTENSIONS = {'doc','docx','pptx', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types

app = Flask(__name__)

# Connect to Ganache
ganache_url = "HTTP://172.17.64.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload')
def upload_page():
    # Your code for handling upload page
    return render_template('upload.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return 'No file part'
    file = request.files['document']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Prepare the file for upload to IPFS
        files = {'file': (file.filename, file)}
        # IPFS API endpoint for adding a file
        url = 'http://127.0.0.1:5001/api/v0/add'
        try:
            response = requests.post(url, files=files)
            ipfs_hash = json.loads(response.text)['Hash']
            # Use the hash as needed (e.g., store it, return it to the user, etc.)
            return ipfs_hash
        except requests.exceptions.RequestException as e:
            # Handle any exceptions (e.g., connection error)
            return str(e)

@app.route('/get_file/<ipfs_hash>')
def get_file(ipfs_hash):
    try:
        # Fetch the file from IPFS using IPFS Gateway
        gateway_url = f'http://localhost:8080/ipfs/{ipfs_hash}'
        return redirect(gateway_url)
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    address = data.get('address')

    if not web3.isAddress(address):
        return jsonify({'error': 'Invalid address'}), 400
    return jsonify({'message': 'Address verified successfully'}), 200
