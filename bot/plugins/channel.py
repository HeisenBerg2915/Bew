import random
import string
import asyncio

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait

from bot import VERIFY, LOGGER # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.database import Database # pylint: disable=import-error
from bot.plugins.auto_filter import recacher # pylint: disable=import-error

db = Database()
logger = LOGGER(__name__) 

@Client.on_message(filters.command(["add"]) & filters.group, group=1)
async def connect(bot: Bot, update):
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    global VERIFY

    if VERIFY.get(str(chat_id)) is None:
        admin_list = []
        async for member in bot.get_chat_members(
            chat_id=chat_id,
            filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            admin_list.append(member.user.id)

        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if user_id not in VERIFY.get(str(chat_id), []):
        return

    args = (update.text or "").split(maxsplit=1)

    if len(args) < 2:
        await update.reply_text(
            "Usage: /add @ChannelUsername"
        )
        return

    target = args[1].strip()

    try:
        channel = await bot.get_chat(target)
    except Exception as e:
        await update.reply_text(
            f"Please add the bot to the channel as admin first.\n\nError: {e}"
        )
        return

    channel_id = channel.id
    channel_name = channel.title or target

    if await db.in_db(chat_id, channel_id):
        await update.reply_text(
            "This channel is already connected."
        )
        return

    await db.add_chat(chat_id, channel_id, channel_name)
    await recacher(chat_id, True, True, bot, update)

    await update.reply_text(
        f"Channel connected: <code>{channel_name}</code>\n\n"
        "Only new files posted after connecting will be indexed."
    )
                    
@Client.on_message(filters.command(["del"]) & filters.group, group=1)
async def disconnect(bot: Bot, update):
    """
    A Funtion To Handle Incoming /del Command TO Disconnect A Chat With A Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.get_chat_members(chat_id=chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("Invalid Username...!!!")
                return
            target = target_chat[1]
            
        elif not target_chat.startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("Invalid Chat Id...\nChat ID Should Be Something Like This: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Invalid Input...\nYou Should Specify Valid chat_id(-100xxxxxxxxxx) or @username")
        return
    
    try:
        channel_info = await bot.get_chat(target)
        channel_id = channel_info.id
    except Exception:
        await update.reply_text(f"Could not access `{target}`. Make sure the bot is added to that channel and has permission to read messages.")
        return
    
    in_db = await db.in_db(chat_id, channel_id)
    
    if not in_db:
        await update.reply_text("This Channel Is Not Connected With The Group...")
        return
    
    wait_msg = await update.reply_text("Deleting All Files Of This Channel From DB....!!!\n\nPlease Be Patience...Dont Sent Another Command Until This Process Finishes..")
    
    await db.del_filters(chat_id, channel_id)
    await db.del_active(chat_id, channel_id)
    await db.del_chat(chat_id, channel_id)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text("Sucessfully Deleted All Files From DB....")


@Client.on_message(filters.command(["delall"]) & filters.group, group=1)
async def delall(bot: Bot, update):
    """
    A Funtion To Handle Incoming /delall Command TO Disconnect All Chats From A Group
    """
    chat_id=update.chat.id
    user_id = update.from_user.id if update.from_user else None
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.get_chat_members(chat_id=chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    await db.delete_all(chat_id)
    await recacher(chat_id, True, True, bot, update)
    
    await update.reply_text("Sucessfully Deleted All Connected Chats From This Group....")


@Client.on_message(filters.channel & (filters.video | filters.audio | filters.document), group=0)
async def new_files(bot: Bot, update):
    """
    A Funtion To Handle Incoming New Files In A Channel ANd Add Them To Respective Channels..
    """
    channel_id = update.chat.id
    
    # Using 'if elif' instead of 'or' to determine 'file_type'
    # Better Way? Make A PR
    
    try:
        if update.video: 
            file_type = "video" 
            file_id = update.video.file_id
            file_name = update.video.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""
            file_size = update.video.file_size

        elif update.audio:
            file_type = "audio"
            file_id = update.audio.file_id
            file_name = update.audio.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""
            file_size = update.audio.file_size

        elif update.document:
            file_type = "document"
            file_id = update.document.file_id
            file_name = update.document.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""
            file_size = update.document.file_size

        for i in ["_", "|", "-", "."]: # Work Around
            try:
                file_name = file_name.replace(i, " ")
            except Exception:
                pass
    except Exception as e:
        print(e)
        return
        
    
    file_link = update.link
    group_ids = await db.find_group_id(channel_id)
    unique_id = ''.join(
        random.choice(
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits
        ) for _ in range(15)
    )
    
    data = []
    
    if group_ids:
        for group_id in group_ids:
            data_packets = dict(
                    file_id=file_id, # File Id For Future Updates Maybe...
                    unique_id=unique_id,
                    file_name=file_name,
                    file_caption=file_caption,
                    file_size = file_size,
                    file_type=file_type,
                    file_link=file_link,
                    chat_id=channel_id,
                    group_id=group_id,
                )
            
            data.append(data_packets)
        await db.add_filters(data)
    return

