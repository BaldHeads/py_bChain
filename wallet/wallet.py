# Import dependencies
import subprocess
import json
import os
# import pp
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import *

# middleware components for poa
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
# from web3.middleware import geth_poa_middleware
# w3.middleware_onion.inject(geth_poa_middleware, layer=0)
 
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json' 
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# derive_wallets test
# pp(derive_wallets(mnemonic, "BTC", numderive=3))

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"btc","eth","btc-test"}
keys = {}
for coin in coins:
    keys[coin] = derive_wallets(mnemonic, coin, numderive=5)

# keys[coin][set][which_info] --- dict order
# pks to be used
btctest_key = keys["btc-test"][0]["privkey"]
eth_key = keys["eth"][0]["privkey"]
btctest_address = keys["btc-test"][0]["address"]
eth_address = keys["eth"][0]["address"]

# # Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    # Using elif in case of other coins being added
    # not sure if it may be useful to create a dict of coin: command here or if it would work out
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    elif coin == ETH:
        return Account.privateKeyToAccount(priv_key)

# Generate Account objects for coins
BTCTEST_acc = priv_key_to_account(BTCTEST, btctest_key)
ETH_acc = priv_key_to_account(ETH, eth_key)

# # Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
#      will need if/elif again for adjusting based on coin
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
    
    elif coin == ETH:
        estGas = w3.eth.estimateGas({"from": ETH_acc.address, "to": to, "value": amount})
        return {
            "chainId": 1111,
            "to": to,
            "from": ETH_acc.address,
            "value": amount,
            "gas": estGas,
            "gasPrice": w3.eth.gasPrice,
            "nonce": w3.eth.getTransactionCount(ETH_acc.address)
            #"chainID": 1111
        }


# # Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
#     # will need if/elif again for adjusting based on coin
    txn = create_tx(coin, account, to, amount)
    signed = account.sign_transaction(txn)
    if coin == BTCTEST:
        print(signed)
        return NetworkAPI.broadcast_tx_testnet(signed)
    elif coin == ETH:
        print(signed)
        return w3.eth.sendRawTransaction(signed.rawTransaction)

# View info for prefunding
# print(btctest_address)
# print(eth_address)


