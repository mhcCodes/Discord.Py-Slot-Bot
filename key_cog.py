from discord.ext import commands
import discord
from time import sleep
import uuid
import discord
from discord import app_commands

yourrole = 'Buyer'

class KeyCog(commands.Cog):
    def __init__(self, client):
        self.client = client



        @client.tree.command(name="key", description="Generate a key")
        @app_commands.describe(amount="Amount of key(s)")
        async def gen(interaction: discord.Interaction, amount: str):
            key_amt = range(int(amount))
            f = open("keys.txt", "a")
            show_key = ''
            for x in key_amt:
                key = str(uuid.uuid4())
                show_key += "\n" + key
                f.write(key)
                f.write("\n")


            if len(str(show_key)) == 37:
                show_key = show_key.replace('\n', '')
                embed = discord.Embed(
                    title=f"Key:\n`{show_key}`",
                    color=0x2600FF
                )
                await interaction.response.send_message(embed=embed)
                return 0
            if len(str(show_key)) > 37:
                embe = discord.Embed(
                    title=f"Keys:\n`{show_key}`",
                    color=0x2600FF
                )
                await interaction.channel.send(embed=embe)
                guild = interaction.guild
                logchannels = client.get_channel(1227974421172715603)
                log_embed = discord.Embed(
                    title="Key used",
                    description=f"`User`: `{interaction.user.name}`\n`Key`: `{show_key}`\n`Guild`: `{guild.name}|{guild.id}`",
                    color=0x2600FF
                )
                await logchannels.send(embed=log_embed)
            

            
        
        @client.tree.command(name="redeem", description="Redeem a key")
        @app_commands.describe(key="Key")
        async def redeem(interaction: discord.Interaction, key: str):
            emb = discord.Embed(
                title="`Redeem Used`",
                description=f"`User`: {interaction.user.name}\n`Key`: {key}",
                color=0x2600FF
            )
            await interaction.response.send_message(embed=emb)
      

   

async def setup(client):
    await client.add_cog(KeyCog(client))