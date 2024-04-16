import discord
from discord.ext import commands
from discord import app_commands



class Calculator(commands.Cog):
    def __init__(self, client):
        self.client = client

        
        @client.tree.command(name="calculate", description="Calculator command")
        @app_commands.describe(expression="Question")
        async def calculate(interaction: discord.Interaction, expression: str):
            try:
                result = eval(expression)
                emb = discord.Embed(
                    title="`Successfully Used Calculate Command`",
                    description=f"`Question`: `{expression}`",
                    color=0x2600FF
                )
                emb.add_field(name="`Result`", value=f"`{result}`", inline=False)
                await interaction.response.send_message(embed=emb)
            except Exception as e:
                embed = discord.Embed(
                    title="Error",
                    description=f"{e}",
                    color=discord.Color.red()
                )
                await interaction.response.send_message("Err", embed=embed)
   


async def setup(client):
    await client.add_cog(Calculator(client))