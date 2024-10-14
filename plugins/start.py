import asyncio
import os
import random
import sys
import time
import string
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, CHANNEL_ID, FORCE_MSG, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, OWNER_TAG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, OWNER_ID, SHORTLINK_URL, SHORTLINK_API, USE_PAYMENT, USE_SHORTLINK, VERIFY_EXPIRE, TIME, TUT_VID, U_S_E_P, REQUEST1, REQUEST2, PHOTO_URL, LOG_CHANNEL
from helper_func import encode, get_readable_time, increasepremtime, subscribed, subscribed2, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time
from database.database import add_admin, add_user, del_admin, del_user, full_adminbase, full_userbase, gen_new_count, get_clicks, inc_count, new_link, present_admin, present_hash, present_user

WAIT_MSG = """"<b>Processing ...</b>"""
REPLY_ERROR = """<blockquote><b>Use this command as a reply to any telegram message without any spaces.</b></blockquote>"""
SECONDS = TIME 
TUT_VID = f"{TUT_VID}"


@Bot.on_message(filters.command('start') & filters.private & subscribed & subscribed2)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    verify_status = await get_verify_status(id)
    if USE_SHORTLINK and (not U_S_E_P):
        for i in range(1):
            if id in ADMINS:
                continue
            if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
                await update_verify_status(id, is_verified=False)
            if "verify_" in message.text:
                _, token = message.text.split("_", 1)
                if verify_status['verify_token'] != token:
                    return await message.reply("<blockquote><b>🔴 Your token verification is invalid or Expired, Hit /start command and try again.<b></blockquote>")
                await update_verify_status(id, is_verified=True, verified_time=time.time())
                if verify_status["link"] == "":
                    reply_markup = None
                await message.reply(f"<blockquote><b>Your token verification was successful\n\nNow you can access all files for 24-hrs...</b></blockquote>", reply_markup=reply_markup, protect_content=False, quote=True)
    if len(message.text) > 7:
        for i in range(1):
            if USE_SHORTLINK and (not U_S_E_P):
                if USE_SHORTLINK: 
                    if id not in ADMINS:
                        try:
                            if not verify_status['is_verified']:
                                continue
                        except:
                            continue
            try:
                base64_string = message.text.split(" ", 1)[1]
            except:
                return
            _string = await decode(base64_string)
            argument = _string.split("-")
            if (len(argument) == 5 )or (len(argument) == 4):
                if not await present_hash(base64_string):
                    try:
                        await gen_new_count(base64_string)
                    except:
                        pass
                await inc_count(base64_string)
                if len(argument) == 5:
                    try:
                        start = int(int(argument[3]) / abs(client.db_channel.id))
                        end = int(int(argument[4]) / abs(client.db_channel.id))
                    except:
                        return
                    if start <= end:
                        ids = range(start, end+1)
                    else:
                        ids = []
                        i = start
                        while True:
                            ids.append(i)
                            i -= 1
                            if i < end:
                                break
                elif len(argument) == 4:
                    try:
                        ids = [int(int(argument[3]) / abs(client.db_channel.id))]
                    except:
                        return
                temp_msg = await message.reply("Please wait... 🫷")
                try:
                    messages = await get_messages(client, ids)
                except:
                    await message.reply_text("Something went wrong..! 🥲")
                    return
                await temp_msg.delete()
                snt_msgs = []
                for msg in messages:
                    if bool(CUSTOM_CAPTION) & bool(msg.document):
                        caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html,    filename=msg.document.file_name)
                    else:   
                        caption = "" if not msg.caption else msg.caption.html   
                    reply_markup = None 
                    try:    
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                        await asyncio.sleep(0.5)    
                        snt_msgs.append(snt_msg)    
                    except FloodWait as e:  
                        await asyncio.sleep(e.x)    
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode= ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                        snt_msgs.append(snt_msg)    
                    except: 
                        pass
                if (SECONDS == 0):
                    return
                notification_msg = await message.reply(f"<blockquote><b><blockquote><b>🔴 This file will be  deleted in {get_exp_time(SECONDS)}. Please save or forward it to your saved messages before it gets deleted.</b></blockquote>.")
                await asyncio.sleep(SECONDS)    
                for snt_msg in snt_msgs:    
                    try:    
                        await snt_msg.delete()  
                    except: 
                        pass    
                await notification_msg.edit(f"<blockquote><b>Your file has been successfully deleted! 😼</b></blockquote>")  
                return
            if (U_S_E_P):
                if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
                    await update_verify_status(id, is_verified=False)

            if (not U_S_E_P) or (id in ADMINS) or (verify_status['is_verified']):
                if len(argument) == 3:
                    try:
                        start = int(int(argument[1]) / abs(client.db_channel.id))
                        end = int(int(argument[2]) / abs(client.db_channel.id))
                    except:
                        return
                    if start <= end:
                        ids = range(start, end+1)
                    else:
                        ids = []
                        i = start
                        while True:
                            ids.append(i)
                            i -= 1
                            if i < end:
                                break
                elif len(argument) == 2:
                    try:
                        ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                    except:
                        return
                temp_msg = await message.reply("Please wait... 🫷")
                try:
                    messages = await get_messages(client, ids)
                except:
                    await message.reply_text("Something went wrong..! 🥲")
                    return
                await temp_msg.delete()
                snt_msgs = []
                for msg in messages:
                    if bool(CUSTOM_CAPTION) & bool(msg.document):
                        caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
                    else:   
                        caption = "" if not msg.caption else msg.caption.html   
                    reply_markup = None 
                    try:    
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                        await asyncio.sleep(0.5)    
                        snt_msgs.append(snt_msg)    
                    except FloodWait as e:  
                        await asyncio.sleep(e.x)    
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode= ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                        snt_msgs.append(snt_msg)    
                    except: 
                        pass    
            try:
                if snt_msgs:
                    if (SECONDS == 0):
                        return
                    notification_msg = await message.reply(f"<blockquote><b>🔴 This file will be  deleted in  {get_exp_time(SECONDS)}. Please save or forward it to your saved messages before it gets deleted.</b></blockquote>")
                    await asyncio.sleep(SECONDS)    
                    for snt_msg in snt_msgs:    
                        try:    
                            await snt_msg.delete()  
                        except: 
                            pass    
                    await notification_msg.edit("<blockquote><b>Your file has been successfully deleted! 😼</b></blockquote>")  
                    return
            except:
                    newbase64_string = await encode(f"sav-ory-{_string}")
                    if not await present_hash(newbase64_string):
                        try:
                            await gen_new_count(newbase64_string)
                        except:
                            pass
                    clicks = await get_clicks(newbase64_string)
                    newLink = f"https://t.me/{client.username}?start={newbase64_string}"
                    link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API,f'{newLink}')            
                    
                    await client.send_message(chat_id=LOG_CHANNEL, text=f"""<b>#NEW_LINK: {message.from_user.first_name}
User: @{message.from_user.username} • {message.from_user.id}

New Link: {newLink}</b>""")
                
                    if USE_PAYMENT:
                        btn = [
                        [InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=link)],
                        [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)],
                        [InlineKeyboardButton("Premium Membership", callback_data="premium")]
                        ]
                    else:
                        btn = [
                        [InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=link)],
                        [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)]
                        ]
                    await message.reply_photo(photo=random.choice(PHOTO_URL), caption=f"<blockquote><b>Total clicks: {clicks}. Here is your link </b></blockquote>.", reply_markup=InlineKeyboardMarkup(btn), quote=True)
                    return

    for i in range(1):
        if USE_SHORTLINK and (not U_S_E_P):
            if USE_SHORTLINK : 
                if id not in ADMINS:
                    try:
                        if not verify_status['is_verified']:
                            continue
                    except:
                        continue
        reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("☎️ Contact Developer", callback_data="about")],
                [InlineKeyboardButton("📴 Close", callback_data="close")]]
        )
        await message.reply_photo(
            photo=random.choice(PHOTO_URL),
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            quote=True
        )
        return

    if USE_SHORTLINK and (not U_S_E_P): 
        if id in ADMINS:
            return
        verify_status = await get_verify_status(id)
        if not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(id, verify_token=token, link="")
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API,f'https://t.me/{client.username}?start=verify_{token}')
            
            await client.send_message(chat_id=LOG_CHANNEL, text=f"""<b>#VERIFICATION_LINK: {message.from_user.first_name}
User: @{message.from_user.username} • • {message.from_user.id}

Verification Link: https://t.me/{client.username}?start=verify_{token}

Shorten Link: {link}</b>""")
                    
            if USE_PAYMENT:
                btn = [
                [InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=link)],
                [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)],
                [InlineKeyboardButton("Premium Membership", callback_data="premium")]
                ]
            else:
                btn = [
                [InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=link)],
                [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)]
                ]
            await message.reply_photo(photo=random.choice(PHOTO_URL), caption=f"<blockquote><b>ℹ️ Hi @{message.from_user.username}\nYour verification is expired, click on below button and complete the verification to\n <u>Get free access for 24-hrs</u></b></blockquote>", reply_markup=InlineKeyboardMarkup(btn), quote=True)
            return
    return


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = []
    row_buttons = []

    # Add buttons for the first row
    if FORCE_SUB_CHANNEL and int(FORCE_SUB_CHANNEL) != 0:
        row_buttons.append(InlineKeyboardButton("Join 1", url=client.invitelink))

    if REQUEST1 and REQUEST1.strip():
        row_buttons.append(InlineKeyboardButton("Join 2", url=REQUEST1))
    
    if FORCE_SUB_CHANNEL2 and int(FORCE_SUB_CHANNEL2) != 0:
        row_buttons.append(InlineKeyboardButton("Join 3", url=client.invitelink2))

    if REQUEST2 and REQUEST2.strip():
        row_buttons.append(InlineKeyboardButton("Join 4", url=REQUEST2))
    
    # Add the first row of buttons
    if row_buttons:
        buttons.append(row_buttons)
    
    # Add retry button to a new row if applicable
    try:
        buttons.append([InlineKeyboardButton(text="🔃 Try Again", url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except IndexError:
        pass

    # Send the reply with the formatted message and buttons
    await message.reply_photo(
        photo=random.choice(PHOTO_URL),
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )


@Bot.on_message(filters.command('ch2l') & filters.private)
async def gen_link_encoded(client: Bot, message: Message):
    try:
        hash = await client.ask(text="Enter the code here\nHit /cancel to cancel the operation", chat_id = message.from_user.id, timeout=60)
    except Exception as e:
        print(e)
        await hash.reply(f"😔 some error occurred {e}")
        return
    if hash.text == "/cancel":
        await hash.reply("Cancelled 😉!")
        return
    link = f"https://t.me/{client.username}?start={hash.text}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hash Link", url=link)]])
    await hash.reply_text(f"** Here is your generated link:\n\n{link}**", quote=True, reply_markup=reply_markup)
    return
        

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot 👥")
    return



@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, m: Message):
    all_users = await full_userbase()  # Fetch all user IDs once (list of users)
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Broadcast starting..!") 
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = len(all_users)  # Calculate total users from the fetched list

    # Use a regular for loop to iterate through all_users since it's a list
    for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
            if sts == 400:
                await del_user(user['_id'])  # Delete user if necessary
        done += 1

        if done % 20 == 0:
            await sts_msg.edit(f"Broadcast in progress: \nTotal users: {total_users} \nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Broadcast completed: \nCompleted in {completed_in}.\n\nTotal users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")

async def send_msg(user_id, message):
    while True:
        try:
            await message.copy(chat_id=int(user_id))
            return 200
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except InputUserDeactivated:
            return 400
        except UserIsBlocked:
            return 400
        except PeerIdInvalid:
            return 400
        except Exception as e:
            logging.error(f"Error sending message to {user_id}: {str(e)}")
            return 500


@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def command_add_admin(client: Bot, message: Message):
    while True:
        try:
            admin_id = await client.ask(text="Enter userid to add admin\nHit /cancel to cancel",chat_id = message.from_user.id, timeout=60)
        except Exception as e:
            print(e)
            return
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        try:
            await Bot.get_users(user_ids=admin_id.text, self=client)
            break
        except:
            await admin_id.reply("❌ Error 😖\n\nThe userid is incorrect.", quote = True)
            continue
    if not await present_admin(admin_id.text):
        try:
            await add_admin(admin_id.text)
            await message.reply(f"<b>Admin {admin_id.text} added successfully")
            try:
                await client.send_message(
                    chat_id=admin_id.text,
                    text=f"You are verified, ask the owner to add them to db channels. 😁"
                )
            except:
                await message.reply("Failed to send invite. Please ensure that they have started the bot. 🥲")
        except:
            await message.reply("Failed to add admin. 😔\nSome error occurred.")
    else:
        await message.reply("Admin already exist. 💀")
    return


@Bot.on_message(filters.command('del_admin') & filters.private  & filters.user(OWNER_ID))
async def delete_admin_command(client: Bot, message: Message):
    while True:
        try:
            admin_id = await client.ask(text="Enter userid to remove admin\nHit /cancel to cancel",chat_id = message.from_user.id, timeout=60)
        except:
            return
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        try:
            await Bot.get_users(user_ids=admin_id.text, self=client)
            break
        except:
            await admin_id.reply("❌ Error\n\nThe userid is incorrect.", quote = True)
            continue
    if await present_admin(admin_id.text):
        try:
            await del_admin(admin_id.text)
            await message.reply(f"<b>Admin {admin_id.text} removed successfully 😀</b>")
        except Exception as e:
            print(e)
            await message.reply("Failed to remove admin. 😔\nSome error occurred.")
    else:
        await message.reply("admin doesn't exist. 💀")
    return

@Bot.on_message(filters.command('admins')  & filters.private & filters.private)
async def admin_list_command(client: Bot, message: Message):
    admin_list = await full_adminbase()
    await message.reply(f"<b>Full admin list 📃\n\n{admin_list}</b>")
    return

@Bot.on_message(filters.command('ping')  & filters.private)
async def check_ping_command(client: Bot, message: Message):
    start_t = time.time()
    rm = await message.reply_text("Pinging....", quote=True)
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"**Ping 🔥!\n{time_taken_s:.3f} ms**")
    return


@Client.on_message(filters.private & filters.command('restart') & filters.user(ADMINS))
async def restart(client, message):
    msg = await message.reply_text(
        text="<b>🔃 Trying To Restarting</b>",
        quote=True
    )
    await asyncio.sleep(5)
    await msg.edit("<b>🔃 Server Restarted Successfully</b>")
    try:
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(e)


if USE_PAYMENT:
    @Bot.on_message(filters.command('add_prem') & filters.private & filters.user(ADMINS))
    async def add_user_premium_command(client: Bot, message: Message):
        while True:
            try:
                user_id = await client.ask(text="Enter userid for premium membership\nHit /cancel to cancel", chat_id = message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return  
            if user_id.text == "/cancel":
                await user_id.edit("Cancelled 😉!")
                return
            try:
                await Bot.get_users(user_ids=user_id.text, self=client)
                break
            except:
                await user_id.edit("❌ Error\n\nThe user id is incorrect.", quote = True)
                continue
        user_id = int(user_id.text)
        while True:
            try:
                timeforprem = await client.ask(text="""<blockquote><b>👛 Enter the amount of time you want to provide the premium user</b></blockquote>
<b>(Note: Choose correctly, its not reversible.)

Enter 1 for One time verification
Enter 2 for One week
Enter 3 for One month
Enter 4 for Three months
Enter 5 for Six months</b>""", chat_id=message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return
            if not int(timeforprem.text) in [1, 2, 3, 4, 5]:
                await message.reply("You have given wrong input. 😖")
                continue
            else:
                break
        timeforprem = int(timeforprem.text)
        if timeforprem==1:
            timestring = "One time verified"
        elif timeforprem==2:
            timestring = "One week"
        elif timeforprem==3:
            timestring = "One month"
        elif timeforprem==4:
            timestring = "Three month"
        elif timeforprem==5:
            timestring = "Six months"
        try:
            await increasepremtime(user_id, timeforprem)
            await message.reply("Premium added! 🤫")
            await client.send_message(
            chat_id=user_id,
            text=f"<b>👑 Update for you\n\nYou are added as premium member for ({timestring}) 😃\n\nFeedback: @StupidBoi69</b>",
        )
        except Exception as e:
            print(e)
            await message.reply("Some error occurred.\nCheck logs.. 😖\nIf you got premium added message then its ok.")
        return

        
