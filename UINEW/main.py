from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, send_file, session, flash
from web3 import Web3
from Blockchain import setup
import os
from werkzeug.utils import secure_filename
from moralis import auth
import requests
import json
from flask_cors import CORS

UPLOAD_FOLDER = 'uploads'  # Set the path to the upload directory
ALLOWED_EXTENSIONS = {'doc','docx','pptx', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types
app = Flask(__name__)

## Connect to Ganache and keep secret key for sessions
try:
 app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
 web3 = setup.w3
except:
    print("Please place your keys and server_url in the .env file")
    exit()
    
try:
 ## Deploys the SmartContract on your local machine
 setup.deployContract(os.environ.get('owner_address'), os.environ.get('owner_private_key'),web3)
except:
    print("Please specify the owner address and owner private key in your .env file")
    exit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')

## Verifies the address is true
@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    address = data.get('address')

    if not web3.isAddress(address):
        return jsonify({'error': 'Invalid address'}), 400
    return jsonify({'message': 'Address verified successfully'}), 200

## Stores address in session state
@app.route('/store_address', methods=['POST'])
def store_address():
    data = request.json
    session['wallet_address'] = data.get('address')
    return jsonify({'message': 'Address stored in session'})

@app.route('/some_route')
def some_route():
    wallet_address = session.get('wallet_address')
    if wallet_address:
       pass
    else:
        pass
    return jsonify({'wallet_address': wallet_address})
    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        content_creator_address = session.get('wallet_address')
        content_creator_private_key = request.form['private_key']
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        ipfsHash = request.form['ipfsHash']

        try:
            setup.uploadContent(content_creator_address, content_creator_private_key, title, description, tags, ipfsHash)
            return "Content uploaded successfully"
        except Exception as e:
            return f"An error occurred: {e}"
    return render_template('upload.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
         return jsonify({'error': 'No file part'}), 400
    file = request.files['document']
    if file.filename == '':
         return jsonify({'error': 'No selected file'}), 400
    if file:
        # Prepare the file for upload to IPFS
        files = {'file': (file.filename, file)}
        # IPFS API endpoint for adding a file
        url = 'http://127.0.0.1:5001/api/v0/add'
        try:
            response = requests.post(url, files=files)
            ipfs_hash = json.loads(response.text)['Hash']
            return jsonify({'ipfs_hash': ipfs_hash})
        except requests.exceptions.RequestException as e:
            # Handle any exceptions (e.g., connection error)
            return jsonify({'error': str(e)}), 500

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