from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, send_file, session, flash
from web3 import Web3
from Blockchain import setup
import os
from werkzeug.utils import secure_filename
from moralis import auth
import requests
import json
from flask_cors import CORS
import time

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
           
####AUTOMATES SUBSCRIPTIONS###



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploaded_content')
def uploaded_content():
    print("entered222")
    user_address = session.get('wallet_address')
    if user_address:
        uploaded_content = setup.viewUploadedContent(user_address, user_address)
        print(uploaded_content)
        return render_template('uploadedContent.html', content=uploaded_content)
    else:
        return redirect(url_for('index'))  # Redirect to login if no user in session

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
    address = data.get('address')
    if not address:
        return jsonify({'error': 'No address provided'}), 400

    session['wallet_address'] = address
    print("Wallet Address Stored in Session:", session['wallet_address'])
    return jsonify({'message': 'Address stored in session'})

@app.route('/some_route')
def some_route():
    wallet_address = session.get('wallet_address')
    if wallet_address:
       pass
    else:
        pass
    return jsonify({'wallet_address': wallet_address})
    
@app.route('/submit_content', methods=['GET', 'POST'])
def submit_content():
    if request.method == 'POST':
        content_creator_address = session.get('wallet_address')
        print(content_creator_address)
        content_creator_private_key = request.form['key']
        print(content_creator_private_key)
        title = request.form['title']
        print(title)
        description = request.form['description']
        print(description)
        tags = request.form['tags']
        print(tags)
        ipfsHash = request.form['ipfsHash']
        print(ipfsHash)

        try:
            setup.uploadContent(content_creator_address, content_creator_private_key, title, description, tags, ipfsHash)
            return jsonify({'message': 'Content uploaded successfully'}) 
        except Exception as e:
            return jsonify({'error': f'UH OH! An error occurred: {e}'}), 500

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
    
@app.route('/get-subscriptions')
def get_subscriptions():
    print("ENTERED")
    user_address = session.get('wallet_address')  # Retrieve user address from session
    subscriptions = setup.viewSubscriptions(user_address)
    return jsonify(subscriptions)

@app.route('/get-subscribers')
def get_subscribers():
    creator_address = session.get('wallet_address')  # Retrieve creator address from session
    subscribers = setup.viewSubscribers(creator_address)
    return jsonify(subscribers)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_address = session.get('wallet_address')
    if not user_address:
        return redirect(url_for('login'))  # Redirect to login if no user in session

    try:
        setup.populateHomeFeed(web3, user_address)
        time.sleep(2)
    except Exception as e:
        # Log the error and handle the exception
        print(f"An error occurred: {e}")
        # Handle the error appropriately
        pass

    # Get the list of subscriptions for the current user
    subscriptions = setup.viewSubscriptions(user_address)

    # Get the uploaded content for each subscribed user
    feed_contents = []
    for creator_address in subscriptions:
        try:
            # Extract contents and process them
            contents = setup.viewUploadedContent(user_address, creator_address)
            for content in contents:
                # Assuming content is a tuple and the address is the first element
                processed_content = process_content(content)  # Define this function based on your content structure
                feed_contents.append(processed_content)
        except Exception as e:
            # Handle any exceptions during content fetching
            print(f"Error fetching content for creator {creator_address}: {e}")

    # Pass the feed_contents to your template
    return render_template('dashboard.html', feed_contents=feed_contents)

def process_content(content_tuple):
    # Assuming content_tuple structure is known, process it accordingly
    # Example: If address is the first element and title is the second
    address = content_tuple[0]
    title = content_tuple[1]
    # Process and return in a format suitable for your template
    return {"address": address, "title": title}

@app.route('/discover')
def discover():
    # Here, you would ideally fetch user addresses from your contract or database
    users = web3.eth.accounts
    user_address = session.get('wallet_address') 
    if user_address:
        user_address_normalized = web3.to_checksum_address(user_address)
        users = [addr for addr in users if web3.to_checksum_address(addr) != user_address_normalized]
    return render_template('discover.html', users=users)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    creator_address = request.form.get('creator')
    subscriber_private_key = request.form.get('key')
    subscriber_address = session.get('wallet_address')
    
    if not subscriber_address:
        return jsonify({'error': 'User not logged in'}), 403

    try:
        setup.subscribeToCreator(subscriber_address, subscriber_private_key, creator_address, web3)
        return jsonify({'message': 'Subscription successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def byte32_to_string(byte32):
    try:
        # Assuming the byte32 string is UTF-8 encoded
        return byte32.decode('utf-8').rstrip('\x00')
    except Exception as e:
        return str(e)  # Return error message if conversion fails

app.jinja_env.filters['byte32_to_string'] = byte32_to_string

if __name__ == '__main__':
    app.run(debug=True)