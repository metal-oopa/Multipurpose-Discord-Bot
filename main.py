from sqlalchemy import BigInteger
import discord
import os
import dotenv
import requests
import json
import random
from discord.ext import tasks, commands
from itertools import cycle
from replit import db
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True

ENV = dotenv.load_dotenv()
my_secret = os.environ["TOKEN"]

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="~")
# await bot.process_commands( message )

sad_words = ["sad", "depress", "unhappy", "angry", "miserable", "sed lyf", "dukhi"]
starter_encouragements = ["Cheer up!", "Hang in there.", "You are a great person!"]

status = cycle(
    [
        "Jan Ken Pon",
        "Hanetsuki",
        "Keidoro",
        "Beigoma",
        "Menko",
        "Karuta",
        "Ayatori",
        "Daruma Otoshi",
    ]
)

fight = cycle(
    [
        "I wanna fight with you, **Amanojaku**",
        "Come out, *Amanojaku*. Are you afraid?",
        "Oi. Dete ke. Khorra. De nai to omae wo ***korosu***",
        "Omae wa Uriko hime wo koroshitan da. Ima wa omae wo korosu.",
        "Do you again want to be put to sleep for centuries? If you don't come out."
        "I will ~~not~~ kill you if you grant me my desires.",
        "Yuki onna desu. Watashi ni sukiatte nai kana.",
    ]
)

if "responding" not in db.keys():
    db["responding"] = True

# Back-ground Task
@tasks.loop(seconds=60 * 60)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@tasks.loop(seconds=60 * 60)
async def pick_fight():
    channel = client.get_channel(int(dotenv.dotenv_values()["channel_id1"]))
    await channel.send(next(fight))


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return quote


def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements

    else:
        db["encouragements"] = [encouraging_message]


def delete_encouragement(index):
    encouragements = db["encouragements"]
    if len(encouragements) > index:
        del encouragements[index]
        db["encouragements"] = encouragements


@client.event
async def on_ready():
    change_status.start()
    pick_fight.start()
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    msg = message.content.lower()
    chan = message.channel
    auth = message.author
    # await chan.send(message.author.id)

    if msg.startswith("hello"):
        await chan.send("Hello {0.mention} :wave:".format(auth))

    elif msg.startswith("~inspire"):
        quote = get_quote()
        await chan.send(quote)

    elif msg.startswith("~new"):
        encouraging_message = message.content.split("~new ", 1)[1]
        update_encouragements(encouraging_message)
        await chan.send("New encouraging message added")

    elif msg.startswith("~del"):
        encouragements = []
        if "encouragements" in db.keys():
            index = int(msg.split("~del", 1)[1])
            delete_encouragement(index)
            encouragements = db["encouragements"].value
        await chan.send(encouragements)

    elif msg.startswith("~list"):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = db["encouragements"].value
        await chan.send(encouragements)

    elif msg.startswith("~responding"):
        value = msg.split("~responding ", 1)[1]

        if value == "true":
            db["responding"] = True
            await chan.send("Responding is on.")
        else:
            db["responding"] = False
            await chan.send("Responding is off.")

    elif msg.startswith("~clear"):  # ~clear 100
        amt = int(message.content.split("~clear ")[1]) + 1
        deleted = await chan.purge(limit=amt)
        await chan.send("{} messages cleared.".format(len(deleted) - 1))

    elif msg.startswith("~write"):  # ~write general This is the message
        a = message.content.split(" ", 2)
        ch_name = a[1]
        output = a[2]
        chnl = client.get_channel(int(dotenv.dotenv_values()["channel_id2"]))
        if ch_name == "general":
            chnl = client.get_channel(int(dotenv.dotenv_values()["channel_id2"]))
        elif ch_name == "amano":
            chnl = client.get_channel(int(dotenv.dotenv_values()["channel_id1"]))
        elif ch_name == "music":
            chnl = client.get_channel(int(dotenv.dotenv_values()["channel_id3"]))
        elif ch_name == "confess":
            chnl = client.get_channel(int(dotenv.dotenv_values()["channel_id4"]))
        elif ch_name == "vc":
            chnl = client.get_channel(int(dotenv.dotenv_values()["channel_id5"]))
        elif ch_name == "anime":
            chnl = client.get_channel(int(dotenv.dotenv_values()["channel_id6"]))

        await chnl.send(output)
        deleted = await message.delete()

    elif msg.startswith("~profile"):  # ~profile
        usr = auth
        if len(message.mentions) > 0:
            usr = message.mentions[0]
        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url="{}".format(usr.avatar_url))
        embed.set_author(
            name="{}".format(usr.name), icon_url="{}".format(usr.avatar_url)
        )
        embed.set_thumbnail(url="{}".format(usr.avatar_url))
        embed.add_field(
            name="About {}".format(usr.display_name),
            value="{}".format(usr.avatar),
            inline=False,
        )

        await chan.send(embed=embed)

    elif msg.startswith("~help"):  # ~help
        embed = discord.Embed(color=discord.Color.random())
        embed.set_author(
            name="__HELP__",
            icon_url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/scroll_1f4dc.png",
        )  # Scroll emoji
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/285/scroll_1f4dc.png"
        )
        embed.add_field(
            name="__Commands__",
            value=":wave: **Hello** : responds with Hello\n**~profile** : diplays profile\n**~list** : diplays list of Encouragements\n**~add <Message>** : new Encouragement\n**~del <index>** : delete Encouragement at index\n**responding true** : turns response to messages on\n**responding <anything else>** : turns off response to messages\n**~write <channel> <Message>** : writes Message in channel.\n**~clear <integer n>** : deletes n messages.",
            inline=False,
        )

        await auth.send(embed=embed)

    elif db["responding"]:  # check
        options = starter_encouragements
        if "encouragements" in db.keys():
            options = options + db["encouragements"].value

        if any(word in msg for word in sad_words):
            emoji = "\U0001F62D"
            await message.add_reaction(emoji)
            await message.channel.send(random.choice(options))


# ON MESSAGE DELETION   WORKING PROPERLY
@client.event
async def on_message_delete(message):
    await message.channel.send("{0.author} deleted: {0.content}".format(message))


# autorole NOT WORKING YET
@client.event
async def on_member_join(member):
    role = discord.utils.get(
        member.guild.roles, id=BigInteger(dotenv.dotenv_values()["role_id1"])
    )  # name = "otaku"
    await member.add_roles(role)
    channel = client.get_channel(BigInteger(dotenv.dotenv_values()["channel_id2"]))
    await channel.send(
        "Congrats {0.mention}.\nYou have been assigned the role of Otaku.".format(
            member
        )
    )


@client.event
async def on_reaction_add(reaction, user):
    msg = reaction.message
    await msg.add_reaction(reaction.emoji)


keep_alive()
client.run(my_secret)

# TO BE ADDED
# 1. display about me of mentioned user/author
# 2. play audio and video
# 3. AI Chat feature
