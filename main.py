# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import time
import requests
import telebot
import threading
from datetime import datetime

# on a condition where user data will be used
class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.sex = None

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
def transactions(wallet: str = None) -> list:
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
    response = requests.get('https://api.etherscan.io/api', params=url_params)
    response_parsed = json.loads(response.content)
    assert (response_parsed['message'] == 'OK')
    txs = response_parsed['result']
    return [{'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} \
            for tx in txs]


# Setup global state runtime store
subscriptions = {}  # Update the transaction list for a specific chat's wallet


def update_subscriptions(chat_id, wallet) -> bool:
    global subscriptions
    try:
        txs = transactions(wallet)
        if chat_id not in subscriptions.keys():
            subscriptions[chat_id] = {}
            subscriptions[chat_id][wallet] = txs
        return True
    except:
        return False  # Setup a message handler for 'add_wallet_listener'

def process_wallet_step(message):
    try:
        chat_id = message.chat.id
        wallet_addr = message.text
        if not update_subscriptions(message.chat.id, wallet_addr):
            bot.reply_to(message, f'Failed to add the wallet to subsription list! Is it a real address?')
            return
        bot.reply_to(message,
                     f'You are now subscribed to events from the following wallets: {subscriptions[message.chat.id].keys()}')


    except Exception as e:
        bot.reply_to(message, 'oooops')

@bot.message_handler(commands=['start','help'])
def startBotOperation(message):
    print(message)
    bot.reply_to(message,f'Welcome to CryptoBotMonitor \n Here are list of our commands\n'
                         f'\\add_wallet\n'
                         f'\\get_wallets\n'
                         f'\\prev_transaction\n'
                         f'\\remove_wallet\n')


# Show the user the wallets they're listening to
@bot.message_handler(commands=['get_wallets'])
def handle_get_listening_wallets(message):
    if message.chat.id in subscriptions.keys():
        bot.reply_to(message, f'You are currently subscribed to events from: {subscriptions[message.chat.id].keys()}')
    else:
        bot.reply_to(message, 'You are not subscribed to any wallet transactions!')

@bot.message_handler(commands=['add_wallet'])
def handle_add_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address.')
        bot.register_next_step_handler(message, process_wallet_step)
        return
    wallet_addr = message_text[1]
    print(message_text)
    if not update_subscriptions(message.chat.id, wallet_addr):
        bot.reply_to(message, f'Failed to add the wallet to subsription list! Is it a real address?')
        return
    bot.reply_to(message,
                 f'You are now subscribed to events from the following wallets: {subscriptions[message.chat.id].keys()}')


@bot.message_handler(commands=['prev_transaction'])
def get_previous_transactions(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address to fetch transactions.')
        bot.register_next_step_handler(message,get_transactions)
        return

@bot.message_handler(commands=['prev_transaction'])
def get_transactions(message):
    wallet_addr = message.text
    trans_list  = transactions(wallet_addr)
    data = "";
    if(len(trans_list)):
        for tran in trans_list:
            data += "Sends from " + tran['from'] + " to " + tran['to'] + " of value: "+ tran['value'] + " on: " + datetime.timestamp(tran['timestamp']) +"\n"
        bot.reply_to(message,data)
    else:
        bot.reply_to(message,"No transaction records found")

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
        bot.reply_to(message, f'Could not find wallet address subscription - did you ever subscribe? address: {wallet_addr}')

# Get the latest transaction timestamp from a list
def get_latest_tx(txs: list) -> int:
    return max(txs, key=lambda tx: int(tx['timestamp']))  # Format a transaction to string nicely


def format_tx(tx: dict) -> str:
    return f'From: {tx["from"]}, To: {tx["to"]}, Amount: {tx["value"]}'

@background
def infinity_wallet_updates():
    while True:
        for chat in subscriptions:
            for wallet in subscriptions[chat]:
                previous_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                print(previous_latest_tx)
                update_subscriptions(chat, wallet)
                current_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                if int(current_latest_tx['timestamp']) > int(previous_latest_tx['timestamp']):
                    bot.send_message(chat, f'New transactions occurred for {wallet}!')
                    [bot.send_message(chat, format_tx(tx)) for tx in \
                     filter(lambda tx: int(tx['timestamp']) > previous_latest_tx, subscriptions[chat][wallet])]
                # else:
                    # bot.send_message(chat, f'Last Transactions occurred for {wallet}!')
        time.sleep(60)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    infinity_wallet_updates()
    bot.infinity_polling()