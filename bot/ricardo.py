import discord
import os

from bot import Bot
from discord.ext.commands import when_mentioned_or
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

requestable_roles = ['test_role']
verified_role = 'Member'

# welcome to the world Ricardo
intents = discord.Intents().all()
intents.reactions = True
intents.presences = False
intents.dm_typing = False
intents.dm_reactions = False
intents.invites = False
intents.webhooks = False
intents.integrations = False
bot = Bot(
    command_prefix='!',
    case_insensitive=True,
    max_messages=10_000,
    allowed_mentions=discord.AllowedMentions(everyone=False),
    intents=intents,
)

@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(guild)
    print('Connected to {0.name} as {1.user}'.format(guild, bot))

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@bot.command(name='hello')
async def hello(message):
    if message.author == bot.user:
        return
    await message.channel.send('hello {0}!'.format(message.author)) 

@bot.command(name='addrole', pass_context=True)
async def addrole(ctx, role):
    member = ctx.message.author
    role = discord.utils.get(member.guild.roles, name=role)

    if role in requestable_roles:
        await member.add_roles(role)
        await ctx.message.channel.send("Role added!")
    else:
        await ctx.message.channel.send("Role not available to add")

@bot.command(name='verify', pass_context=True)
async def verify(ctx):
    member = ctx.message.author
    print(member.guild.roles)
    await ctx.message.channel.send("yes")

@bot.event
async def on_raw_reaction_add(payload):
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)

    # member role flairing
    start_here = discord.utils.get(guild.channels, name='start-here')
    if payload.channel_id == start_here.id:
        member = discord.utils.get(guild.members, id=payload.user_id)
        verified = discord.utils.get(guild.roles, name=verified_role)
        if verified not in member.roles:
            await member.add_roles(verified)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)