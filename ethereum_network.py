
# def process_wallet_step(message):
#     try:
#         wallet_addr = message.text
#         if not update_subscriptions(message.chat.id, wallet_addr):
#             bot.reply_to(message, f'Failed to add the wallet to subsription list! Is it a real address?')
#             return
#         bot.reply_to(message,
#                      f'You are now subscribed to events from the following wallets: {subscriptions[message.chat.id].keys()}')
#
#     except Exception as e:
#         print(e)
#         bot.reply_to(message, 'oooops')

