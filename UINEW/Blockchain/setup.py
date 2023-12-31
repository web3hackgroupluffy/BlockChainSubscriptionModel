#Author: Larnell Moore
#Purpose: Helper functions that encapsulates the Smart Contract functionilities. Please make an .env file that contains the server url.
from web3 import Web3
import json
from dotenv import load_dotenv
from Blockchain.contract import SubContract
import os

global c
c = SubContract()

def connectToBlockChain():
  load_dotenv()
  server_url = os.getenv('Ganache_url')
  print(server_url)
  w3 = Web3(Web3.HTTPProvider(server_url))
  assert w3.is_connected(), "Failed to connect to Ethereum node."
  print(w3.is_connected())
  return w3

def deployContract(owner_address, owner_private_key,w3):
    """Deploys the Subscription Smart Contract onto the blockchain"""
    contract = w3.eth.contract(abi=c.contract_abi, bytecode=c.contract_bytecode)
    tx = contract.constructor().build_transaction({
    'from': owner_address,
    'nonce': w3.eth.get_transaction_count(owner_address),
    'gas': 2000000,  # Set the gas limit
    'gasPrice': w3.to_wei('50', 'gwei')  # Set the gas price
})
    signed_tx = w3.eth.account.sign_transaction(tx, owner_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    c.contract_address = tx_receipt.contractAddress
    c.contract = w3.eth.contract(address=c.contract_address, abi=c.contract_abi)
    print(f"Contract deployed at address: {c.contract_address}")
    
def uploadContent(content_creator_address, content_creator_private_key, title, description,tags, ipfsHash):
   """Precondition: Title must be 32 characters or less"""
   if len(title) > 32:
    raise ValueError("String is too long. Maximum length is 32 bytes.")

   content_creator_address = Web3.to_checksum_address(content_creator_address)

   # Convert to bytes
   bytes_str = Web3.to_bytes(text=title)

   # If necessary, pad the byte array to make it bytes32
   bytes32_str = bytes_str.ljust(32, b'\0')
   
   tx = c.contract.functions.creatorUpload(
    bytes32_str, description, tags, ipfsHash
).build_transaction({
    'from': content_creator_address,
    'gas': 2000000,
    'gasPrice': w3.to_wei('50', 'gwei'),
    'nonce': w3.eth.get_transaction_count(content_creator_address)
})

   signed_tx = w3.eth.account.sign_transaction(tx, content_creator_private_key)
   tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
   tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
   print(f"Receipt at address: {tx_receipt}")


def subscribeToCreator(subscriber_acc, subscriber_privatekey, creator_address,w3):
    creator_address =  Web3.to_checksum_address(creator_address)
    subscriber_acc =  Web3.to_checksum_address(subscriber_acc)
    subscription_fee = c.contract.functions.subscriptionFee().call()
    
    tx = c.contract.functions.subscribe(creator_address).build_transaction({
    'from': subscriber_acc,
    'value': subscription_fee,
    'gas': 2000000,
    'gasPrice': w3.to_wei('50', 'gwei'),
    'nonce': w3.eth.get_transaction_count(subscriber_acc)
})

    signed_tx = w3.eth.account.sign_transaction(tx, subscriber_privatekey)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Receipt at address: {tx_receipt}")


def viewUploadedContent(initiator_address, creator_address):
    """Returns a list of all the content posted by a specified creator. Initiator must be either the creator or subscriber."""
    content = c.contract.functions.getUploadsByCreator(creator_address).call({'from': initiator_address})
    return content

def viewSubscribers(creator_address):
  """Returns a list of all subscribers for a creator"""
  creator_subscribers = c.contract.functions.getSubscribers(creator_address).call()
  print("Creator Subscribers:", creator_subscribers)
  return creator_subscribers

def viewSubscriptions(user_address):
   """Returns a list of the people a user has subscribed to."""
   user_subscriptions = c.contract.functions.getSubscriptions(user_address).call()
   print("User Subscriptions:", user_subscriptions)
   return user_subscriptions

def isSubbed(subscriber_acc, creator_address):
    """Checks if the initator is subbed to the specified creator"""
    creator_address =  Web3.to_checksum_address(creator_address)
    subscriber_acc =  Web3.to_checksum_address(subscriber_acc)
    is_subbed = c.contract.functions.isSubscribed(subscriber_acc, creator_address).call()
    print("User Subscriptions:", is_subbed)
    return is_subbed

#Connect Function
w3 = connectToBlockChain()

