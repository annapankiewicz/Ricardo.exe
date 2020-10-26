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
GUILD = os.getenv('DISCORD_GUILD')

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
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(date.today())
    print('Connected to {0.name} as {1.user}'.format(guild, bot))

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

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

    everyone = discord.utils.get(ctx.guild.roles, name="@everyone")
    ricardo_role = discord.utils.get(ctx.guild.roles, name="Ricardo.exe")
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    testing_role = discord.utils.get(ctx.guild.roles, name="testing")
    student_role = discord.utils.get(ctx.guild.roles, name="Students")
    managed_roles = [r for r in ctx.guild.roles if r.managed]

    unrequestable_roles = [everyone, ricardo_role, admin_role, testing_role, student_role]
    unrequestable_roles.extend(managed_roles)

    if not role:
        await ctx.message.channel.send("Invalid role. !roles to see available roles")
    else:
        if role not in unrequestable_roles:
            try:
                await member.add_roles(role)
                await ctx.message.channel.send("Role added!")
            except:
                await ctx.message.channel.send("Could not add role - something went wrong!")
        else:
            await ctx.message.channel.send("Role not available to add.")

@bot.command(name='removerole', pass_context=True)
async def removerole(ctx, *args):
    member = ctx.message.author
    all_roles = discord.utils.get(ctx.guild.roles)
    role_name = ' '.join(args)
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.message.channel.send("Cannot remove an invalid role. !roles to see available roles")
    else:
        if role not in member.roles:
            await ctx.message.channel.send("Cannot remove role.")
        else:
            try:
                await member.remove_roles(role)
                await ctx.message.channel.send("Role removed.")
            except:
                await ctx.message.channel.send("Could not remove role - something went wrong!")

@bot.command(name='roles', pass_context=True)
async def roles(ctx):
    # exclude roles that shouldn't be requested, like admin or integrated roles
    # clean this up later please, this is ugly
    everyone = discord.utils.get(ctx.guild.roles, name="@everyone")
    ricardo_role = discord.utils.get(ctx.guild.roles, name="Ricardo.exe")
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    testing_role = discord.utils.get(ctx.guild.roles, name="testing")
    student_role = discord.utils.get(ctx.guild.roles, name="Students")
    managed_roles = [r for r in ctx.guild.roles if r.managed]

    unrequestable_roles = [everyone, ricardo_role, admin_role, testing_role, student_role]
    unrequestable_roles.extend(managed_roles)

    description = '- ' + '\n - '.join([role.name for role in ctx.guild.roles if role not in unrequestable_roles])

    embedVar = discord.Embed(title="Available roles", description=description, color=0x546f7a)

    await ctx.message.channel.send(embed=embedVar)

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
    with open(date.today() + '.err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)