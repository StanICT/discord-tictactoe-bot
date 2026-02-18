import discord
from dotenv import load_dotenv
import os

load_dotenv()

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith("hello"):
            await message.channel.send(f"Hi there {message.author}")

    async def on_reaction_add(self, reaction, user: discord.User):
        await reaction.message.channel.send(f"{user.display_name} {user.id}")


intents = discord.Intents.default()
intents.message_content = True


client = Client(intents = intents)
client.run(os.getenv("DISCORD_BOT_TOKEN"))

