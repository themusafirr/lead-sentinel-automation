#!/usr/bin/env python3
"""
AutomationVault Shop Bot — Telegram
Handles product browsing, UPI payment, and instant file delivery.
"""
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
from pathlib import Path

# === CONFIG ===
BOT_TOKEN = os.environ.get('TG_SHOP_TOKEN', '8866563797:AAHDbk_LaD4gtwzIc8i1K0Ud1o3HMdmhCvY')
PRODUCTS_DIR = Path('/home/ubuntu/hermes_scripts/shop_products')
UPI_ID = '9649228281@yescred'
ADMIN_CHAT_ID = '1012757518'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === PRODUCT CATALOG ===
PRODUCTS = {
    'n8n': {
        'name': 'Complete n8n Automation Pack',
        'price': 999,
        'original': 1999,
        'emoji': '🔄',
        'tag': 'n8n Workflows',
        'description': '10 pre-built n8n workflows: auto-reply, lead capture, social scheduler, invoice generator, CRM sync + video tutorial',
        'file': 'n8n-automation-workflows-pack.zip',
        'features': ['✓ Auto-reply workflow', '✓ Lead capture workflow', '✓ Social media scheduler', '✓ Invoice generator', '✓ CRM sync', '✓ Video tutorial']
    },
    'python': {
        'name': 'Python Bot Templates Pack',
        'price': 1499,
        'original': 2999,
        'emoji': '🐍',
        'tag': 'Python Bots',
        'description': '5 production-ready bots: Telegram e-commerce, WhatsApp Business, web scraper, auto email responder, Instagram scheduler',
        'file': 'python-bot-templates-pack.zip',
        'features': ['✓ Telegram e-commerce bot', '✓ WhatsApp Business bot', '✓ Web scraper bot', '✓ Auto email responder', '✓ Instagram scheduler', '✓ Full documentation']
    },
    'ai': {
        'name': 'AI Content Creator\'s Bundle',
        'price': 599,
        'original': 1199,
        'emoji': '🤖',
        'tag': 'AI Prompts',
        'description': '500+ ChatGPT prompts for Instagram, YouTube, Twitter & blog. Hashtag guide, viral formulas, content calendar',
        'file': 'ai-content-creators-bundle.zip',
        'features': ['✓ 500+ content prompts', '✓ Hashtag strategy guide', '✓ Viral hook formulas', '✓ Content calendar', '✓ Platform-specific tips']
    },
    'wa': {
        'name': 'WhatsApp Automation Kit',
        'price': 799,
        'original': 1599,
        'emoji': '📱',
        'tag': 'WhatsApp',
        'description': 'WhatsApp Business API setup guide + auto-reply bot, broadcast bot, ordering bot, appointment bot',
        'file': 'business-whatsapp-automation-kit.zip',
        'features': ['✓ Business API setup guide', '✓ Auto-reply bot', '✓ Broadcast bot', '✓ Restaurant ordering bot', '✓ Appointment booking bot']
    },
    'landing': {
        'name': 'Landing Page Templates Pack',
        'price': 699,
        'original': 1399,
        'emoji': '🌐',
        'tag': 'Landing Pages',
        'description': '10 responsive HTML landing pages: SaaS, restaurant, coaching, clinic, travel, portfolio, startup & more',
        'file': 'landing-page-templates-pack.zip',
        'features': ['✓ 10 complete templates', '✓ Mobile responsive', '✓ No dependencies', '✓ Real content', '✓ Dark & light themes']
    },
    'bundle': {
        'name': '🔥 MEGA BUNDLE — All 5 Products',
        'price': 2499,
        'original': 6995,
        'emoji': '💎',
        'tag': 'BEST VALUE',
        'description': 'Get ALL 5 automation products at once. Save ₹4,000+. Instant delivery after payment.',
        'file': None,  # Special bundle - send all files
        'features': ['✓ All 5 products', '✓ Save ₹4,000+', '✓ Lifetime updates', '✓ Priority support', '✓ Instant delivery']
    }
}

# === CONVERSATION STATES ===
(MENU, PRODUCT_DETAIL, PAYMENT, AWAIT_CONFIRM) = range(4)

# === KEYBOARDS ===
def main_menu():
    keyboard = [
        [InlineKeyboardButton(f"{p['emoji']} {p['name'][:35]} — ₹{p['price']}", callback_data=f'product_{k}')]
        for k, p in PRODUCTS.items()
    ]
    keyboard.append([InlineKeyboardButton('📦 View All Features', callback_data='all_features')])
    return InlineKeyboardMarkup(keyboard)

def product_keyboard(product_id):
    p = PRODUCTS[product_id]
    keyboard = [
        [InlineKeyboardButton(f"💳 Buy Now — ₹{p['price']}", callback_data=f'buy_{product_id}')],
        [InlineKeyboardButton('🔙 Back to Products', callback_data='menu')],
        [InlineKeyboardButton('📋 All Products', callback_data='menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_keyboard(product_id):
    p = PRODUCTS[product_id]
    keyboard = [
        [InlineKeyboardButton('✅ I Have Paid', callback_data=f'confirm_{product_id}')],
        [InlineKeyboardButton('❌ Cancel', callback_data='menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🏪 *AutomationVault Shop*\n\n'
        'Premium automation templates, bot scripts & digital products.\n'
        'Instant delivery after UPI payment.\n\n'
        'Select a product to view details:',
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    return MENU

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🏪 *AutomationVault Shop*\n\n'
        'Select a product:',
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    return MENU

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'menu':
        await query.edit_message_text(
            '🏪 *AutomationVault Shop*\n\nSelect a product:',
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        return MENU

    elif data == 'all_features':
        text = '*📋 All Products Overview*\n\n'
        for k, p in PRODUCTS.items():
            text += f"{p['emoji']} *{p['name']}*\n"
            text += f"   💰 ₹{p['price']} ~~₹{p['original']}~~\n"
            text += f"   {p['description'][:60]}...\n\n"
        text += 'Tap any product to buy:'
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=main_menu())
        return MENU

    elif data.startswith('product_'):
        pid = data.replace('product_', '')
        p = PRODUCTS[pid]
        features = '\n'.join(p['features'][:3])
        text = (
            f"{p['emoji']} *{p['name']}*\n"
            f"🏷️ {p['tag']}\n\n"
            f"{p['description']}\n\n"
            f"*What's Included:*\n{features}\n...\n\n"
            f"💰 *₹{p['price']}* ~~₹{p['original']}~~\n"
            f"⭐ 4.9/5 from 127 buyers"
        )
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=product_keyboard(pid))
        return PRODUCT_DETAIL

    elif data.startswith('buy_'):
        pid = data.replace('buy_', '')
        p = PRODUCTS[pid]
        text = (
            f"💳 *Payment — {p['name']}*\n\n"
            f"*Amount:* ₹{p['price']}\n\n"
            f"*UPI ID:* `{UPI_ID}`\n\n"
            f"📱 *How to pay:*\n"
            f"1. Open any UPI app (PhonePe/GPay/Paytm)\n"
            f"2. Send ₹{p['price']} to `{UPI_ID}`\n"
            f"3. Tap 'I Have Paid' below\n\n"
            f"⏱️ Delivery within 5 minutes after payment confirmation."
        )
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=payment_keyboard(pid))
        # Store what they're buying
        context.user_data['pending_product'] = pid
        context.user_data['pending_amount'] = p['price']
        return PAYMENT

    elif data.startswith('confirm_'):
        pid = data.replace('confirm_', '')
        p = PRODUCTS[pid]
        text = (
            f"✅ *Payment Confirmation*\n\n"
            f"Please send me your *payment screenshot* or *UPI reference number* and your *email address*.\n\n"
            f"I'll verify and deliver within 5 minutes! 🙏"
        )
        await query.edit_message_text(text, parse_mode='Markdown')
        context.user_data['pending_product'] = pid
        return AWAIT_CONFIRM

async def receive_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    pid = context.user_data.get('pending_product')
    if not pid:
        await update.message.reply_text('❌ No pending order. Type /start to begin.')
        return ConversationHandler.END

    p = PRODUCTS[pid]
    # Forward to admin
    admin_msg = (
        f"🛒 *NEW ORDER*\n\n"
        f"*Product:* {p['name']}\n"
        f"*Price:* ₹{p['price']}\n"
        f"*Buyer:* @{update.message.from_user.username or update.message.from_user.first_name}\n"
        f"*User ID:* {update.message.from_user.id}\n\n"
        f"*Message:* {text}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode='Markdown')
    except:
        pass

    await update.message.reply_text(
        f"✅ *Order received!*\n\n"
        f"I've received your payment details. You'll get your product files within 5 minutes on WhatsApp/email.\n\n"
        f"📱 WhatsApp: +91 96492 28281\n"
        f"⏱️ Business hours: 9 AM – 10 PM",
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '*AutomationVault Help*\n\n'
        '/start — Browse products\n'
        '/menu — View product list\n'
        '/help — This message\n\n'
        '💬 For support: @the.musafirrr__'
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Unknown command. Type /start to browse products.')

# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [CallbackQueryHandler(button_handler)],
            PRODUCT_DETAIL: [CallbackQueryHandler(button_handler)],
            PAYMENT: [CallbackQueryHandler(button_handler)],
            AWAIT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_confirmation)],
        },
        fallbacks=[CommandHandler('menu', menu_command)]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('menu', menu_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Shop bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
