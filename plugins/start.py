import asyncio
import os
import random
import sys
import time
import string
import logging
import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid

from bot import Bot
from config import ADMINS, CHANNEL_ID, START_MSG, FORCE_MSG, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, OWNER_TAG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, OWNER_ID, USE_PAYMENT, USE_SHORTLINK, VERIFY_EXPIRE, TIME, TUT_VID, U_S_E_P, REQUEST1, REQUEST2, PHOTO_URL, LOG_CHANNEL, PINNED
from helper_func import encode, get_readable_time, increasepremtime, subscribed, subscribed2, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time
from database.database import add_admin, add_user, del_admin, del_user, bulk_del_users, full_adminbase, full_userbase, gen_new_count, get_clicks, inc_count, new_link, present_admin, present_hash, present_user

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
            if (len(argument) == 5 ) or (len(argument) == 4):
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
                    link = await get_shortlink(newLink)            
                    await client.send_message(
    chat_id=LOG_CHANNEL,
    text=f"""<b>#NEW_LINK: 
<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name} {message.from_user.last_name}</a>

Username: @{message.from_user.username} • <a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>
Bot Username: @{client.username}

New Link: {newLink}

Shorten Link: {link}</b></blockquote>""",
    parse_mode=ParseMode.HTML
)
  
                    if USE_PAYMENT:
                        btn = [
                        [InlineKeyboardButton("↪️ Get Download Link ↩️", url=link)],
                        [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)],
                        [InlineKeyboardButton("Premium Membership", callback_data="premium")]
                        ]
                    else:
                        btn = [
                        [InlineKeyboardButton("↪️ Get Download Link ↩️", url=link)],
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
            verification_link = f"https://t.me/{client.username}?start=verify_{token}"
            link = await get_shortlink(verification_link)
            await client.send_message(
    chat_id=LOG_CHANNEL,
    text=f"""<b>#VERIFICATION_LINK: 
<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name} {message.from_user.last_name}</a>

Username: @{message.from_user.username} • <a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>
Bot Username: @{client.username}

Verification Link: {verification_link}

Shorten Link: {link}</b></blockquote>""",
    parse_mode=ParseMode.HTML
)
            
            if USE_PAYMENT:
                btn = [
                [InlineKeyboardButton("↪️ Get token for free access ↩️", url=link)],
                [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)],
                [InlineKeyboardButton("Premium Membership", callback_data="premium")]
                ]
            else:
                btn = [
                [InlineKeyboardButton("↪️ Get token for free access ↩️", url=link)],
                [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)]
                ]
            await message.reply_photo(photo=random.choice(PHOTO_URL), caption=f"<blockquote><b>ℹ️ Hi @{message.from_user.username}\nYour verification is expired, click on below button and complete the verification to\n<u>Get File DownLoad Link</u></b></blockquote>", reply_markup=InlineKeyboardMarkup(btn), quote=True)
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


@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, m: Message):
    all_users = await full_userbase()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("📢 Broadcast starting..!")
    done = 0
    failed = 0
    success = 0
    blocked = 0
    start_time = time.time()
    total_users = len(all_users)
    batch_size = 50
    blocked_users = []

    async def process_batch(batch):
        nonlocal success, failed, blocked, blocked_users
        tasks = []
        for user_id in batch:
            tasks.append(send_msg(client, user_id, broadcast_msg))  # Pass client correctly

        results = await asyncio.gather(*tasks)
        for user_id, result in zip(batch, results):
            if result == 200:
                success += 1
            elif result == 400:
                failed += 1
            elif result == 403:
                blocked += 1
                blocked_users.append(user_id)
            else:
                failed += 1

    for i in range(0, total_users, batch_size):
        batch = all_users[i:i + batch_size]
        await process_batch(batch)
        done += len(batch)

        await sts_msg.edit(f"""<blockquote><b>📊 Broadcast in progress:</b>
👥 Total users: {total_users}
✅ Completed: {done} / {total_users}
🎯 Success: {success}
❌ Failed: {failed}
🚫 Blocked: {blocked}</b></blockquote>""")

    if blocked_users:
        await bulk_del_users(blocked_users)

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"""<blockquote><b>📢 Broadcast completed:</b>
⏱️ Completed in {completed_in}.
👥 Total users: {total_users}
✅ Success: {success}
❌ Failed: {failed}
🚫 Blocked: {blocked}</b></blockquote>""")

# Helper function for sending messages with optional pinning
async def send_msg(client: Bot, user_id, message):
    try:
        sent_msg = await message.copy(chat_id=int(user_id))
        if PINNED:  # Check if pinning is enabled
            try:
                await client.pin_chat_message(chat_id=int(user_id), message_id=sent_msg.message_id)
            except Exception as pin_error:
                logging.error(f"Error pinning message for {user_id}: {str(pin_error)}")
        return 200

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(client, user_id, message)
    except (InputUserDeactivated, PeerIdInvalid):
        return 400
    except UserIsBlocked:
        return 403
    except Exception as e:
        logging.error(f"Error sending message to {user_id}: {str(e)}")
        return 500




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

@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def command_add_admin(client: Bot, message: Message):
    while True:
        try:
            # Ask the owner for the user ID they want to add as admin
            admin_id = await client.ask(text="Enter user ID to add as admin\nHit /cancel to cancel", chat_id=message.from_user.id, timeout=60)
        except Exception as e:
            print(e)
            return
        
        # If the user cancels the process
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        
        # Validate if the input is a valid numeric user ID
        if not admin_id.text.isdigit():
            await admin_id.reply("❌ Error 😖\n\nPlease enter a valid numeric user ID.", quote=True)
            continue
        
        try:
            # Check if the user exists using Pyrogram's get_users method
            await client.get_users(user_ids=admin_id.text)
            break  # Exit loop if the user ID is valid
        except Exception:
            await admin_id.reply("❌ Error 😖\n\nThe user ID is incorrect.", quote=True)
            continue
    
    # Now, check if the user is already an admin in the MongoDB database
    if not await present_admin(int(admin_id.text)):
        try:
            # Add the user as admin in the MongoDB database
            await add_admin(int(admin_id.text))
            await message.reply(f"<b>Admin {admin_id.text} added successfully</b>")
            
            # Notify the new admin
            try:
                await client.send_message(
                    chat_id=admin_id.text,
                    text="You are now an admin! Ask the owner to add you to the required channels. 😁"
                )
            except Exception:
                await message.reply("Failed to notify the user. Ensure they have started the bot. 🥲")
        except Exception as e:
            print(f"Error adding admin: {e}")
            await message.reply("Failed to add admin. 😔\nSome error occurred.")
    else:
        await message.reply("Admin already exists. 💀")
    return


@Bot.on_message(filters.command('del_admin') & filters.private & filters.user(OWNER_ID))
async def delete_admin_command(client: Bot, message: Message):
    while True:
        try:
            # Ask the owner for the user ID they want to remove as admin
            admin_id = await client.ask(text="Enter user ID to remove as admin\nHit /cancel to cancel", chat_id=message.from_user.id, timeout=60)
        except Exception as e:
            print(e)
            return
        
        # If the user cancels the process
        if admin_id.text == "/cancel":
            await admin_id.reply("Cancelled 😉!")
            return
        
        # Validate if the input is a valid numeric user ID
        if not admin_id.text.isdigit():
            await admin_id.reply("❌ Error 😖\n\nPlease enter a valid numeric user ID.", quote=True)
            continue
        
        try:
            # Check if the user exists using Pyrogram's get_users method
            await client.get_users(user_ids=admin_id.text)
            break  # Exit loop if the user ID is valid
        except Exception:
            await admin_id.reply("❌ Error 😖\n\nThe user ID is incorrect.", quote=True)
            continue
    
    # Check if the user is an admin in the MongoDB database
    if await present_admin(int(admin_id.text)):
        try:
            # Remove the user as admin from MongoDB
            await del_admin(int(admin_id.text))
            await message.reply(f"<b>Admin {admin_id.text} removed successfully 😀</b>")
        except Exception as e:
            print(f"Error removing admin: {e}")
            await message.reply("Failed to remove admin. 😔\nSome error occurred.")
    else:
        await message.reply("Admin doesn't exist. 💀")
    return


@Bot.on_message(filters.command('admins')  & filters.private & filters.user(ADMINS))
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
    await rm.edit(f"Ping 🔥!\n{time_taken_s:.3f} ms")
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
                user_id = await client.ask(text="Enter user ID for premium membership\nHit /cancel to cancel", chat_id=message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return  
            if user_id.text == "/cancel":
                await user_id.reply("Cancelled 😉!")  # Changed edit() to reply()
                return
            
            # Validate if the input is a valid numeric user ID
            if not user_id.text.isdigit():
                await user_id.reply("❌ Error\n\nThe user ID is incorrect. Please enter a valid numeric user ID.", quote=True)
                continue
            
            # Attempt to get user details
            try:
                await client.get_users(user_ids=int(user_id.text))  # Ensure user_id is an integer
                break
            except Exception:
                await user_id.reply("❌ Error\n\nThe user ID is incorrect.", quote=True)
                continue

        user_id = int(user_id.text)
        while True:
            try:
                timeforprem = await client.ask(text="""<blockquote><b>👛 Enter the amount of time you want to provide the premium user</b></blockquote>
<b>(Note: Choose correctly, it's not reversible.)

Enter 1 for One-time verification
Enter 2 for One week
Enter 3 for One month
Enter 4 for Three months
Enter 5 for Six months</b>""", chat_id=message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return

            if not timeforprem.text.isdigit() or int(timeforprem.text) not in [1, 2, 3, 4, 5]:
                await message.reply("You have given wrong input. 😖")
                continue
            else:
                break
        
        timeforprem = int(timeforprem.text)
        timestring = {
            1: "One time verified",
            2: "One week",
            3: "One month",
            4: "Three months",
            5: "Six months"
        }[timeforprem]

        try:
            await increasepremtime(user_id, timeforprem)  # Function to increase premium time
            await message.reply("Premium added! 🤫")
            await client.send_message(
                chat_id=user_id,
                text=f"<b>👑 Update for you\n\nYou are added as a premium member for ({timestring}) 😃\n\nFeedback: @StupidBoi69</b>",
            )
        except Exception as e:
            print(e)
            await message.reply("Some error occurred.\nCheck logs.. 😖\nIf you got a premium added message, then it's ok.")
        return

