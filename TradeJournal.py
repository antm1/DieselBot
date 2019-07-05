from discord.ext import commands

def get_prefix(client, message):

    prefixes = ['?', '~', '!', '!!']    # sets the prefixes, u can keep it as an array of only 1 item if you need only one prefix

    if not message.guild:
        prefixes = ['!']   # Only allow '==' as a prefix when in DMs, this is optional

    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    # Do `return prefixes` if u don't want to allow mentions instead of prefix.
    return commands.when_mentioned_or(*prefixes)(client, message)


bot = commands.Bot(                             # Create a new bot
    command_prefix=get_prefix,                  # Set the prefix
    description='Entry and Exit price logger',  # Set a description for the bot
    case_insensitive=True                       # Make the commands case insensitive
)

# case_insensitive=True is used as the commands are case sensitive by default

cogs = ['cogs.journal']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    bot.remove_command('help')
    # Removes the help command
    # Make sure to do this before loading the cogs
    for cog in cogs:
        bot.load_extension(cog)
    return


# Finally, login the bot
bot.run('YOURTOKENHERE', bot=True, reconnect=True)
