import discord
import os
import asyncio
import aiohttp
import time
import typing
import string
import random
import sqlite3
from colorama import Fore, Style
from discord import app_commands
from discord.ext import commands, tasks

intents = discord.Intents.all()
client = commands.Bot(command_prefix="?", intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.tree.sync()
    update_presence.start()


conn = sqlite3.connect('database.db')
c = conn.cursor()

# Crea la tabella se non esiste già
c.execute('''CREATE TABLE IF NOT EXISTS Utenti (
             ID INTEGER PRIMARY KEY,
             Nome TEXT NOT NULL,
             Punti INTEGER DEFAULT 0
             )''')
conn.commit()

conn = sqlite3.connect('moderation.db')
c = conn.cursor()

# Crea la tabella se non esiste già
c.execute('''CREATE TABLE IF NOT EXISTS Moderation (
             ID INTEGER PRIMARY KEY,
             MemberID INTEGER,
             ModID INTEGER,
             Reason TEXT
             )''')
conn.commit()


@tasks.loop(seconds=60)  # Update every 60 seconds
async def update_presence():
    guild = client.get_guild(1225910519412691034)  # Replace YOUR_GUILD_ID with your server's ID
    if guild:
        member_count = guild.member_count
        await client.change_presence(activity=discord.Game(name=f"{member_count} members"))


@client.event
async def on_interaction(interaction):
    if isinstance(interaction, discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            command_name = interaction.data['name']
            channel_id = interaction.channel_id
            
            # ID del canale in cui vuoi registrare i log
            log_channel_id = 1227974421172715603
            
            # Verifica se l'ID del canale di log è valido
            log_channel = client.get_channel(log_channel_id)
            if log_channel is None:
                return print('Canale di log non trovato. Assicurati di aver impostato un ID di canale valido.')
            
            # Invia un messaggio di log nel canale di log
            embed = discord.Embed(
                title=f"`User:` `{interaction.user.name}`\n`ID:` `{interaction.user.id}`\n`Channel:` `<#{channel_id}>`",
                description=f"`Executed the Command` `/{command_name}`",
                color=0x2600FF
            )
            await log_channel.send(embed=embed)


@client.tree.command(name="add-warn", description="Warn a user")
@commands.is_owner()
@app_commands.describe(member="The discord Member")
@app_commands.describe(reason="Warn reason")
async def add_warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    # Controlla se l'utente è già stato moderato
    c.execute('SELECT * FROM Moderation WHERE MemberID = ? AND ModID = ?', (member.id, interaction.author.id))
    if c.fetchone() is not None:
        embed = discord.Embed(
            title=f"{member.display_name} `it has already been moderated by you.`",
            color=0x2600FF
        )
        await interaction.channel.send(embed=embed)
    else:
        c.execute('INSERT INTO Moderation (MemberID, ModID, Reason) VALUES (?, ?, ?)', (member.id, interaction.author.id, reason))
        conn.commit()
        emb = discord.Embed(
            title="Warn Added",
            description=f"`User`: `{member.display_name}`\n`Reason`: {reason}",
            color=0x2600FF
        )
        await interaction.channel.send(embed=emb)


@client.tree.command(name="check-warns", description="Check how many time got warned a member")
@commands.is_owner()
@app_commands.describe(member="The discord Member")
async def check_warns(interaction: discord.Interaction, member: discord.Member):
    c.execute('SELECT * FROM Moderation WHERE MemberID = ?', (member.id,))
    infractions = c.fetchall()
    if infractions:
        infraction_list = '\n'.join([f'ModID: {infraction[2]}, Motivo: {infraction[3]}' for infraction in infractions])
        embed = discord.Embed(
            title=f"{member.display_name} `Warns`",
            description=f"`Warns for {member.mention}:\n{infraction_list}`",
            color=0x2600FF
        )
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_author(name="Sql database", icon_url=member.display_icon)
        await interaction.response.send_message(embed=embed)
    else:
        emb = discord.Embed(
            title=f"{member.display_name} `hasn't received a warning yet`",
            color=0x2600FF
        )
        emb.set_thumbnail(url=member.display_avatar)
        emb.set_author(name="Sql database", icon_url=member.display_icon)
        await interaction.channel.send(embed=emb)


@client.tree.command(name="slot", description="Create a Slot")
@commands.is_owner()
@app_commands.describe(name="Slot Name")
@app_commands.describe(duration="Slot duration in S,M,H")
@app_commands.describe(user="Slot user")
async def slot(interaction: discord.Interaction, user: discord.Member, name: str, duration: str):
    guild = interaction.guild
    seconds = 0
    if duration.endswith("s"):
        seconds = int(duration[:-1])
    elif duration.endswith("m"):
        seconds = int(duration[:-1]) * 60
    elif duration.endswith("h"):
        seconds = int(duration[:-1]) * 3600
    
    channel = await guild.create_text_channel(name)
    embed = discord.Embed(
        title="Slot Created!",
        description=f"`Slot User`: {user.mention}",
        color=0x2600FF
    )
    embed.add_field(name="`duration`", value=f"`{duration}`", inline=False)
    embed.add_field(name=f"`slot`", value=f"`{name}`", inline=False)
    await interaction.response.send_message(embed=embed)
    slot_embed = discord.Embed(
        title="Successfully Created Slot",
        description=f"{user.mention}",
        color=0x2600FF
    )
    await channel.send(embed=slot_embed)
    confirm_emb = discord.Embed(
        title="Slot Information's",
        color=0x2600FF
    )
    confirm_emb.add_field(name=f"`Slot Owner`", value=f"`{user.mention}`", inline=False)
    confirm_emb.add_field(name=f"`ends`", value=f"`{duration}`", inline=False)
    await channel.send(embed=confirm_emb)
    print(Fore.BLUE + f"Success Created Slot | Name: `{name}`\nSlot Owner: `{user.name}`\nDuration: `{duration}`")
    await asyncio.sleep(seconds)
    await channel.delete()
    print(Fore.CYAN + f"Slot Deleted With Name: `{name}`\nDuration: `{duration}`\nSlot Owner: `{user.name}`")
    ch = client.get_channel(1227974421172715603)
    log_embed = discord.Embed(
        title="Slot Deleted",
        description=f"User slot: {user.mention}",
        color=discord.Color.red()
    )
    log_embed.add_field(name=f"`duration`", value=f"`{duration}`",  inline=False)
    await ch.send(embed=log_embed)


@client.tree.command(name="slot-revoke", description="Revoke A slot")
@commands.is_owner()
@app_commands.describe(user="The slot owner")
@app_commands.describe(channel="Slot Owner Channel")
async def slot_revoke(interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel):
    guild = interaction.guild
    await channel.delete()
    embed = discord.Embed(
        title="Slot Revoked",
        description=f"`Slot Owner`: {user.mention}`\n SlotName: `{channel.mention}`",
        color=0x2600FF
    )
    await interaction.response.send_message(embed=embed)
    print(Fore.CYAN + f"Slot Revoked\nSlot Owner: `{user.name}`\nSlot Channel: `{channel.name}`")


async def ping_autocompletion(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    data = []
    for ping_choice in ['everyone', 'here']:
        if current.lower() in ping_choice.lower():
            data.append[app_commands.Choice(name=ping_choice, value=ping_choice)]
            return data
        


@client.tree.command(name="auto-ping", description="Send a Ping in a slot channel")
@commands.is_owner()
@app_commands.autocomplete(ping_type=ping_autocompletion)
async def auto_ping(interaction: discord.Interaction, ping_type: str):
    if ping_type == "everyone":
        emb = discord.Embed(
            title="Ping Successfully used",
            description=f"`Ping_type:` {ping_type}",
            color=0x2600FF
        )
        await interaction.response.send_message(embed=emb)
        await interaction.channel.send("@everyone")
        print(Fore.BLUE + f"Successfully sent the `ping`: {ping_type} in {interaction.channel.name}")
    if ping_type == "here":
        embed = discord.Embed(
            title="Ping Successfully used",
            description=f"`Ping_type:` {ping_type}",
            color=0x2600FF
        )
        await interaction.response.send_message(embed=embed)
        await interaction.channel.send("@here")
        print(Fore.BLUE + f"Successfully sent the `ping`: {ping_type} in {interaction.channel.name}")


@client.tree.command(name="clear", description="Clear an amount of message(s)")
@commands.is_owner()
@app_commands.describe(amount="Amount of messages")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    embed = discord.Embed(
        title="Successfully Used Command purge",
        description=f"`by:` `{interaction.user.name}`",
        color=0x2600FF
    )
    embed.add_field(name="`Amount`", value=f"`{amount}`", inline=False)
    await interaction.channel.send(embed=embed)
    print(Fore.CYAN + f"Cleared {amount} messages(s) in {interaction.channel.name}")



async def load():
    for file in os.listdir('./slashcmds'):
        if file.endswith('.py'):
            await client.load_extension(f'slashcmds.{file[:-3]}')
            print(f"Loaded extension {file[:-3]}")


async def main():
    await load()
    await client.start('Paste here ur bot token')


asyncio.run(main())
client.start('TOKEN')