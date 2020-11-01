import discord
import os

from bot import Bot
from datetime import date
from discord.ext.commands import when_mentioned_or
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))

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

verified_role = 'Member'

@bot.event
async def on_ready():
    guild = bot.get_guild(GUILD_ID)
    print(date.today())
    print('Connected to {0.name} as {1.user}'.format(guild, bot))

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

    # send the react role message in the appropriate channel if it hasn't already been done
    role_channel = discord.utils.get(guild.channels, name='react-role-testing')
    if role_channel.last_message is None:
        stream_role = discord.utils.get(guild.roles, name='Stream Notification Squad')
        friendlies_role = discord.utils.get(guild.roles, name='Friendlies')
        gacha_role = discord.utils.get(guild.roles, name='Gacha Hell')

        role_matches = {'Stream Notification Squad':'pepetouched', 'Gacha Hell':'pepeooo', 'Friendlies':'pepepunch'}
        role_emojis = {}
        for role in role_matches:
            emoji = discord.utils.get(guild.emojis, name=role_matches[role])
            role_emojis[role] = emoji

        description = ''
        for role in role_emojis:
            description += '{0} {1}\n'.format(role_emojis[role], role)

        embedVar = discord.Embed(title='Available roles', description=description, color=0x546f7a)
        await role_channel.send(embed=embedVar)

@bot.command(name='hello')
async def hello(message):
    if message.author == bot.user:
        return
    await message.channel.send('Hello {0}!'.format(message.author))

@bot.command(name='addrole', pass_context=True)
async def addrole(ctx, *args):
    member = ctx.message.author
    all_roles = discord.utils.get(ctx.guild.roles)
    role_name = ' '.join(args)
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    stream_role = discord.utils.get(ctx.guild.roles, name='Stream Notification Squad')
    friendlies_role = discord.utils.get(ctx.guild.roles, name='Friendlies')
    gacha_role = discord.utils.get(ctx.guild.roles, name='Gacha Hell')

    requestable_roles = [stream_role, friendlies_role, gacha_role]

    if not role:
        await ctx.message.channel.send('Invalid role. !roles to see available roles')
    else:
        if role in requestable_roles:
            try:
                await member.add_roles(role)
                await ctx.message.channel.send('Role added!')
            except:
                await ctx.message.channel.send('Could not add role - something went wrong!')
        else:
            await ctx.message.channel.send('Role not available to add.')

@bot.command(name='removerole', pass_context=True)
async def removerole(ctx, *args):
    member = ctx.message.author
    all_roles = discord.utils.get(ctx.guild.roles)
    role_name = ' '.join(args)
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.message.channel.send('Cannot remove an invalid role. !roles to see available roles')
    else:
        if role not in member.roles:
            await ctx.message.channel.send('Cannot remove role.')
        else:
            try:
                await member.remove_roles(role)
                await ctx.message.channel.send('Role removed.')
            except:
                await ctx.message.channel.send('Could not remove role - something went wrong!')

@bot.command(name='roles', pass_context=True)
async def roles(ctx):
    # TODO(anna): refactor everything into bot.py so it's not doing the same thing a million times
    # explicitly whitelist available roles
    stream_role = discord.utils.get(ctx.guild.roles, name='Stream Notification Squad')
    friendlies_role = discord.utils.get(ctx.guild.roles, name='Friendlies')
    gacha_role = discord.utils.get(ctx.guild.roles, name='Gacha Hell')

    requestable_roles = [stream_role, friendlies_role, gacha_role]
    description = '- ' + '\n - '.join([role.name for role in ctx.guild.roles if role in requestable_roles])

    embedVar = discord.Embed(title='Available roles', description=description, color=0x546f7a)

    await ctx.message.channel.send(embed=embedVar)

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(GUILD_ID)

    # member role flairing
    start_here = discord.utils.get(guild.channels, name='start-here-and-read-the-rules')
    if payload.channel_id == start_here.id:
        member = discord.utils.get(guild.members, id=payload.user_id)
        verified = discord.utils.get(guild.roles, name=verified_role)
        if verified not in member.roles:
            await member.add_roles(verified)

    react_role = discord.utils.get(guild.channels, name='react-role')
    if payload.channel_id == react_role.id:
        # TODO(anna): move this to a config option instead
        role_matches = {'pepetouched':'Stream Notification Squad', 'pepeooo':'Gacha Hell', 'pepepunch':'Friendlies'}
        member = discord.utils.get(guild.members, id=payload.user_id)

        if payload.emoji.name in role_matches:
            role_name = role_matches[payload.emoji.name]
            role = discord.utils.get(guild.roles, name=role_name)
            await member.add_roles(role)
            await member.send('Gave you the {0} role!'.format(role_name))

@bot.event
async def on_message_delete(message):
    guild = bot.get_guild(GUILD_ID)
    logging_channel = discord.utils.get(guild.channels, name='logging')

    description = '{0} \n\n Content:\n {1}\n\n Message ID: {2}\n\n {3}'.format(
        message.author, message.content, message.id, message.created_at)

    embedVar = discord.Embed(title='Message deleted in #{0}'.format(message.channel.name), description=description, color=0x546f7a)

    if message.attachments is not None:
        for item in message.attachments:
            if item.proxy_url is not None:
                embedVar.set_thumbnail(url=item.proxy_url)
            # TODO(anna): need to somehow handle the case where an attachment doesn't have a proxy_url.... hm

    await logging_channel.send(embed=embedVar)

@bot.event
async def on_message_edit(before, after):
    guild = bot.get_guild(GUILD_ID)
    logging_channel = discord.utils.get(guild.channels, name='logging')
    if before.author == bot.user or after.author == bot.user:
        return

    if before.content == after.content:
        return

    description = '{0} \n\n Before:\n {1}\n\nAfter:\n {2}\n\nMessage ID: {3}\n\n {4}'.format(
        before.author, before.content, after.content, before.id, before.edited_at)

    embedVar = discord.Embed(title='Message edited in #{0}'.format(before.channel.name), description=description, color=0x546f7a)
    await logging_channel.send(embed=embedVar)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)