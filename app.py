#=================================================================================================
# Copyright (C) 2022 by szsupunma@Github, < https://github.com/szsupunma >.
# Released under the "GNU v3.0 License Agreement".
# All rights reserved.
#=================================================================================================

import os
import asyncio
import requests
import random
import bs4

from pykeyboard import InlineKeyboard
from pyrogram.errors import UserNotParticipant
from pyrogram import filters, Client
from RandomWordGenerator import RandomWord
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, bad_request_400


from database import (
    get_served_users,
    add_served_user,
    remove_served_user,
    get_served_chats,
    add_served_chat,
    remove_served_chat
)


API_HASH = ""
API_ID = ""
BOT_TOKEN = ""
CHANNEL_ID = ""
CHANNEL = ""
OWNER = ""

app = Client(
    "Fake_mail_bot",
    api_hash= os.environ["API_HASH"],
    api_id= int(os.environ["API_ID"]),
    bot_token=os.environ["BOT_TOKEN"]
)

#********************************************************************************
start_text = """
Hello! {}, 
I can create **Temporary Emails** for you.

On this bot you can create a temporary (disposable) email in a second, that self-destructs after some time. Stay safe, avoid spam - take care of your anonymity. You can select from many domains and create own nick. Smart, huh?


**Advantages**
   • None Blacklisted Domains.
   • (Fresh Domains).
   • 24 hours Active.

Send /new to set-up your MailBox!.
"""

CHANNEL_ID = int(os.environ['CHANNEL_ID'])
CHANNEL = os.environ['CHANNEL']
OWNER = int(os.environ['OWNER'])


start_button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👥 Group", url="https://t.me/NAKAMA_ASL"),
                    InlineKeyboardButton("🗣 Channel", url="t.me/nakamaop")
                ],
		        [
                    InlineKeyboardButton("🔹 Other Botz", url="https://t.me/azureod_robot/86"),
                ]    
            ]
)



@app.on_message(filters.private & filters.command("start"))
async def start_message(bot, message):
       await message.reply_chat_action("Typing")                 
       await message.reply_text(
           text = start_text.format(message.from_user.mention),    
           reply_markup=start_button)


#@app.on_message(filters.private & filters.command("start"))
#async def start(_, message: Message):
#    await message.reply_text(
#        text = start_text.format(message.from_user.mention),
#        reply_markup = start_button)
#    return await add_served_user(message.from_user.id)
#    chnl = await app.create_chat_invite_link(int(CHANNEL_ID))

    
#********************************************************************************
API1='https://www.1secmail.com/api/v1/?action=getDomainList'
API2='https://www.1secmail.com/api/v1/?action=getMessages&login='
API3='https://www.1secmail.com/api/v1/?action=readMessage&login='
#********************************************************************************

create = InlineKeyboardMarkup(
            [[InlineKeyboardButton("BETA BOTZ", url="https://t.me/nakama_asl")]])

#********************************************************************************
@app.on_message(filters.command("new"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    m =  await app.send_message(name,text=f"📧 Creating  temp email....",reply_markup = create)
    rp = RandomWord(max_word_size=8, include_digits=True)
    email = rp.generate()
    xx = requests.get(API1).json()
    domain = random.choice(xx)
    #print(email)
    mes = await app.send_message(
    name, 
    text = f"""
**📬Done,Your Email Address Created!**
📧 **Email** : `{email}@{domain}`
📨 **Mail BOX** : `empty`
**Powered By** @TEMP_EMAILSBOT""",
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ Update Mail BOX ♻️", callback_data = f"mailbox |{email}|{domain}")]]))
    pi = await mes.pin(disable_notification=True, both_sides=True)
    await m.delete()
    await pi.delete()

async def gen_keyboard(mails, email, domain):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    for mail in mails:
        id = mail['id']
        data.append(
            InlineKeyboardButton(f"{mail['subject']}", f"mail |{email}|{domain}|{id}")
        )
        num += 1
    data.append(
        InlineKeyboardButton(f"♻️ Update Mail BOX ♻️", f"mailbox |{email}|{domain}")
    )
    i_kbd.add(*data)
    return i_kbd
 
#********************************************************************************

@app.on_callback_query(filters.regex("mailbox"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain = callback_request.split("|")
    mails = requests.get(f'{API2}{email}&domain={domain}').json()
    if mails == []:
            await query.answer("🤷‍♂️ No Mails found! 🤷‍♂️")
    else:
        try:
            smail = f"{email}@{domain}"
            mbutton = await gen_keyboard(mails,email, domain)
            await query.message.edit(f""" 
**📬Done,Your Email Address Created!**
📧 **Email** : `{smail}`
📨 **Mail BOX** : ✅""",
reply_markup = mbutton
)   
        except bad_request_400.MessageNotModified as e:
            await query.answer("🤷‍♂️ No New Mails found! 🤷‍♂️")

#********************************************************************************

@app.on_callback_query(filters.regex("mail"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain, id = callback_request.split("|")
    mail = requests.get(f'{API3}{email}&domain={domain}&id={id}').json()
    froms = mail['from']
    subject = mail['subject']
    date = mail['date']
    if mail['textBody'] == "":
        kk = mail['htmlBody']
        body = bs4.BeautifulSoup(kk, 'lxml')
        txt = body.get_text()
        text = " ".join(txt.split())
        url_part = body.find('a')
        link = url_part['href']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔗 Open Link", url=link)
                ],
                [
                    InlineKeyboardButton("◀️ Back", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{text}
""",
reply_markup = mbutton
)
    else:
        body = mail['textBody']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("◀️ Back", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{body}
""",
reply_markup = mbutton
)
#********************************************************************************

@app.on_message(filters.command("domains"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    x = requests.get(f'https://www.1secmail.com/api/v1/?action=getDomainList').json()
    xx = str(",".join(x))
    email = xx.replace(",", "\n")
    await app.send_message(
    name, 
    text = f"""
**{email}**
""",
    reply_markup = create)



#============================================================================================
#Owner commands pannel here
#user_count, broadcast_tool

@app.on_message(filters.command("stats") & filters.user(OWNER))
async def stats(_, message: Message):
    name = message.from_user.id
    served_chats = len(await get_served_chats())
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    served_users = len(await get_served_users())
    served_users = []
    users = await get_served_users()
    for user in users:
        served_users.append(int(user["bot_users"]))

    await app.send_message(
        name,
        text=f"""
🍀 Chats Stats 🍀
🙋‍♂️ Users : `{len(served_users)}`
👥 Groups : `{len(served_chats)}`
🚧 Total users & groups : {int((len(served_chats) + len(served_users)))} """)

async def broadcast_messages(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await remove_served_user(user_id)
        return False, "Deleted"
    except UserIsBlocked:
        await remove_served_user(user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await remove_served_user(user_id)
        return False, "Error"
    except Exception as e:
        return False, "Error"

@app.on_message(filters.private & filters.command("bcast") & filters.user(OWNER) & filters.reply)
async def broadcast_message(_, message):
    b_msg = message.reply_to_message
    chats = await get_served_users() 
    m = await message.reply_text("Broadcast in progress")
    for chat in chats:
        try:
            await broadcast_messages(int(chat['bot_users']), b_msg)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass  
    await m.edit(f"""
Broadcast Completed:.""")    

@app.on_message(filters.command("ads"))
async def ads_message(_, message):
    await message.reply_text(
"""     📮Advertise On Telegram 🚀

Want to promote anything ? 

Beta Bot is here with your basic needs.

Want to promote your online business ? Want to get people engagement? We are here!

Promote whatever you want at lowest and affordable price

Contact @ASSISTANT_BETABOT To Get More Info""")

print("I'm Alive Now!")
app.run()
