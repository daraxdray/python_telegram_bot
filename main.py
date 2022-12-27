# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
from typing import Tuple, Any
import time
import requests
import telebot
import threading
from datetime import datetime
from web3 import Web3, EthereumTesterProvider
from javascript import require
from operator import itemgetter

# on a condition where user data will be used
from web3.middleware import geth_poa_middleware


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.sex = None


# io1tzg22nkjntwc4t7c4cl8ycf0uy2cpwe6fnma55
# 0x5890a54ed29add8aafd8ae3e72612fe11580bb3a

# handles background operations
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()

    return backgrnd_func


# instance data
BOT_KEY = "5634039874:AAEUOw-Durtamov-LF_fbkj3mre3wiZbPCc"
ETHERSCAN_KEY = "MSCFKXM5AMAYM3D6E5N6D7XSB6BX37FSNQ"
myWallet = "0x9Ed55DEad64798EfFE2D994b5480925420664bC8"
bot = telebot.TeleBot(BOT_KEY, parse_mode=None)


#  get list of all transactions
def ethTransactions(wallet: str = None) -> list:
    assert (wallet is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 10,
        'sort': 'asc',
        'apikey': ETHERSCAN_KEY  # Use your API key here!
    }
    # https: // api.etherscan.io / api
    response = requests.get('https://api.etherscan.io/api', params=url_params)
    response_parsed = json.loads(response.content)
    print(response_parsed)
    assert (response_parsed['message'] == 'OK')
    txs = response_parsed['result']
    return [{'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} \
            for tx in txs]


def ioTexTransactions(wallet: str = None) -> list:
    assert (wallet is not None)
    url = Web3.HTTPProvider('https://babel-api.mainnet.iotex.io')
    web3 = Web3(url)
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    # request the latest block number
    ending_blocknumber = web3.eth.blockNumber
    # latest block number minus 100 blocks
    print("end")
    print(ending_blocknumber)
    starting_blocknumber = ending_blocknumber - 100
    # block = web3.eth.get_block('latest', True)
    all_transactions = []
    address = Web3.toChecksumAddress(convert_io_to_eth_wallet(wallet)) if is_iot_wallet(
        wallet) else Web3.toChecksumAddress(wallet)
    res = web3.eth.get_balance(address)
    for x in range(starting_blocknumber, ending_blocknumber):
        print(x)
        block = web3.eth.getBlock(x, True)
        for tx in block.transactions:
            print(Web3.toChecksumAddress(tx['from']) + "--" + Web3.toChecksumAddress(tx['to']))
            if Web3.toChecksumAddress(tx['from']).lower() == address.lower() or tx['to'].lower() == address.lower():
                all_transactions.append(
                    {'from': tx['from'], 'to': tx['to'], 'value': tx['value'],
                     'transactionIndex': tx['transactionIndex']})
    print(all_transactions)
    return all_transactions


# Setup global state runtime store
subscriptions = {}  # Update the transaction list for a specific chat's wallet


def update_subscriptions(chat_id, wallet) -> bool:
    global subscriptions
    try:
        print(wallet)
        txs = ioTexTransactions(wallet)
        if chat_id not in subscriptions.keys():
            subscriptions[chat_id] = {}
            subscriptions[chat_id][wallet] = txs
        return True
    except:
        return False  # Setup a message handler for 'add_wallet_listener'


def process_iotx_wallet_step(message):
    try:
        wallet_addr = convert_io_to_eth_wallet(message.text)
        print(wallet_addr)
        if not update_subscriptions(message.chat.id, wallet_addr):
            bot.reply_to(message, f'Failed to add the wallet to subsription list! Is it a real address?')
            return
        bot.reply_to(message,
                     f'You are now subscribed to events from the following wallets: {subscriptions[message.chat.id].keys()}')
    except Exception as e:
        print(e)
        bot.reply_to(message, 'oooops')


@bot.message_handler(commands=['start', 'help'])
def startBotOperation(message):
    bot.reply_to(message, f'Welcome to CryptoBotMonitor \n'
                          f'1. Subscscribe/Add wallet address to monitor transactions \n'
                          f'2. Get list of wallet addresses subscribed platform \n'
                          f'3. Get transaction of wallet address \n'
                          f'4. Convert IOTEX to Ethereum address \n'
                          f'5. Remove your wallet from the subscribed')
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('/add')
    itembtn2 = telebot.types.KeyboardButton('/get')
    itembtn3 = telebot.types.KeyboardButton('/transaction')
    itembtn5 = telebot.types.KeyboardButton('/convert')
    itembtn4 = telebot.types.KeyboardButton('/remove')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    # bot.register_next_step_handler(message, handle_start_command)
    bot.send_message(message.chat.id, "Select a command", reply_markup=markup)


# @bot.message_handler()
# def handle_start_command(message):
#     m_text = message.text
#     print("STart command is")
#     print(m_text)
#     if m_text == 'Add':
#         bot.register_next_step_handler(message, select_wallet_type)
#     elif m_text == 'Convert':
#         bot.reply_to(message, f'Please provide wallet address. to convert')
#         bot.register_next_step_handler(message, convert_eth_iotex_wallet)
#     elif m_text == 'Get':
#         bot.register_next_step_handler(message, handle_get_listening_wallets)
#     elif m_text == 'Transaction':
#         bot.register_next_step_handler(message, get_transactions)
#     else :
#         bot.register_next_step_handler(message, handle_remove_wallet_listener)


# @bot.message_handler(commands=['add'])
# def select_wallet_type(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
#     itembtn1 = telebot.types.KeyboardButton('/ethereum')
#     itembtn2 = telebot.types.KeyboardButton('/iotex')
#     markup.add(itembtn1, itembtn2)
#     bot.send_message(message.chat.id, "Choose wallet type:", reply_markup=markup)
#     print(message)
#     print(markup.selective)
#     print(markup.to_json())
#     bot.register_next_step_handler(message, handle_add_wallet_listener)


@bot.message_handler(commands=['convert'])
def convert_eth_iotex_wallet(message):
    print(message)
    m_text = message.text
    m_text = convert_io_to_eth_wallet(m_text)
    bot.reply_to(message, f'Your IoTex address is: \n {m_text}')


@bot.message_handler(commands=['add'])
def handle_add_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide IOTex or EVM compactible wallet address.')
        bot.register_next_step_handler(message, process_iotx_wallet_step)
        return
    wallet_addr = message_text[0]
    if not update_subscriptions(message.chat.id, wallet_addr):
        bot.reply_to(message, f'Failed to add the wallet to subsription list! Is it a real address?')
        return
    bot.reply_to(message,
                 f'You are now subscribed to events from the following wallets: {subscriptions[message.chat.id].keys()}')


# Show the user the wallets they're listening to
@bot.message_handler(commands=['get'])
def handle_get_listening_wallets(message):
    if message.chat.id in subscriptions.keys():
        bot.reply_to(message, f'You are currently subscribed to events from: {subscriptions[message.chat.id].keys()}')
    else:
        bot.reply_to(message, 'You are not subscribed to any wallet transactions!')


@bot.message_handler(commands=['transaction'])
def get_previous_transactions(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address to fetch transactions.')
        bot.register_next_step_handler(message, get_transactions)
        return


@bot.message_handler(commands=['all transaction'])
def get_transactions(message):
    wallet_addr = message.text
    trans_list = ioTexTransactions(wallet_addr)
    data = ""
    if (len(trans_list)):
        for tran in trans_list:
            data += "Sends from " + tran['from'] + " to " + tran['to'] + " of value: " + tran[
                'value'] + " on: " + datetime.fromtimestamp(tran['timestamp']) + "\n"
        bot.reply_to(message, data)
    else:
        bot.reply_to(message, "No transaction records found")


@bot.message_handler(commands=['remove_wallet'])
def handle_remove_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address.')
        return
    wallet_addr = message_text[1]
    if wallet_addr in subscriptions[message.chat.id].keys():
        del subscriptions[message.chat.id][wallet_addr]
        bot.reply_to(message, f'Wallet address {wallet_addr} now unsubscribed!')
    else:
        bot.reply_to(message,
                     f'Could not find wallet address subscription - did you ever subscribe? address: {wallet_addr}')


# Get the latest transaction timestamp from a list
def get_latest_tx(txs: list) -> int:
    return max(txs, key=lambda tx: int(tx['timestamp']))  # Format a transaction to string nicely


# //it gets the latest trasanction on web3 using index
def get_latest_web3_tx(txs: list) -> int:
    print("LATEST")
    return max(txs, key=lambda tx: int(tx['transactionIndex'])) if txs else 0  # Format a transaction to string nicely


def format_tx(tx: dict) -> str:
    return f'From: {tx["from"]}, To: {tx["to"]}, Amount: {tx["value"]}'


@background
def infinity_wallet_updates():
    while True:
        for chat in subscriptions:
            for wallet in subscriptions[chat]:
                previous_latest_tx = get_latest_web3_tx(subscriptions[chat][wallet])
                print(":Previous")
                print(previous_latest_tx)
                update_subscriptions(chat, wallet)
                current_latest_tx = get_latest_web3_tx(subscriptions[chat][wallet])
                print(subscriptions[chat][wallet])
                if current_latest_tx > previous_latest_tx:
                    bot.send_message(chat, f'New transactions occurred for {wallet}!')
                    [bot.send_message(chat, format_tx(tx)) for tx in \
                     filter(lambda tx: int(tx['transactionIndex']) > previous_latest_tx, subscriptions[chat][wallet])]
                elif len(subscriptions[chat][wallet]) > 0:
                    bot.send_message(chat, f'Last Transactions occurred for {wallet}!')
                    bot.send_message(chat, format_tx(subscriptions[chat][wallet][previous_latest_tx]))
                else:
                    bot.send_message(chat, f'Been a while you had a transaction,  {wallet}!')
        time.sleep(40)


def convert_io_to_eth_wallet(ethAddres: str) -> str:
    convertIotex = require("@iotexproject/iotex-address-ts")
    fr = itemgetter('from', )(convertIotex)
    result = fr(ethAddres)
    print(result.string())
    return result.stringEth()


def is_iot_wallet(wallet: str) -> bool:
    return wallet.startswith("io")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    infinity_wallet_updates()
    bot.infinity_polling()

