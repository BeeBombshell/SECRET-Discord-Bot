import discord
import wikipedia
from discord.ext import commands


class Example(commands.Cog):

    def __init__(self, client):
        self.client = client

    # event
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online.')

    # commands
    @commands.command()
    async def Beep(self, message):
        '''
        - Replies "Boop". (Sample function)
        '''
        await message.send(f'Boop!')

    def wiki_summary(self, arg):
        definition = wikipedia.summary(
            arg, sentences=3, chars=1000, auto_suggest=True, redirect=True)
        return definition

    @commands.Cog.listener()
    async def on_message(self, message):
        words = message.content.split()
        important_words = words[1:]

        if message.content.startswith('*define'):
            words = message.content.split()
            important_words = words[1:]
            search = discord.Embed(title="Searching...", description=self.wiki_summary(
                important_words), color=discord.Colour.blue())
            await message.channel.send(content=None, embed=search)


def setup(client):
    client.add_cog(Example(client))
