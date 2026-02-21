import os

import discord
from commands import tree, client

@client.event
async def on_ready():
    for guild_id in client.guild_ids:
        await tree.sync(guild=discord.Object(id=guild_id))

    print(f"Logged on as {client.user}!")

client.run(os.getenv("DISCORD_BOT_TOKEN"))
