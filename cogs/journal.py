import discord
from discord.ext import commands
import json


# New - The Cog class must extend the commands.Cog class
class Journal(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def update_journal(self):
        with open('journal.json', 'r') as file_in:
            self.journal = json.load(file_in)

    def update_file(self):
        with open('journal.json', 'w') as file_out:
            json.dump(self.journal, file_out, indent=2, sort_keys=True)

    @commands.command(
        name='help',
        description='The help command!',
        aliases=['commands', 'command'],
        usage='cog'
    )

    async def help_command(self, ctx, cog='all'):

        # The third parameter comes into play when
        # only one word argument has to be passed by the user

        # Prepare the embed

        help_embed = discord.Embed(
            title='Help',
            color=0x95A5A6
        )
        help_embed.set_thumbnail(url=self.bot.user.avatar_url)
        help_embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=self.bot.user.avatar_url
        )

        # Get a list of all cogs
        cogs = [c for c in self.bot.cogs.keys()]

        # If cog is not specified by the user, we list all cogs and commands

        if cog == 'all':
            for cog in cogs:
                # Get a list of all commands under each cog

                cog_commands = self.bot.get_cog(cog).get_commands()
                commands_list = ''
                for comm in cog_commands:
                    commands_list += f'**{comm.name}** - *{comm.description}*\n'

                # Add the cog's details to the embed.

                help_embed.add_field(
                    name=cog,
                    value=commands_list,
                    inline=False
                ).add_field(
                    name='\u200b', value='\u200b', inline=False
                )

                # Also added a blank field '\u200b' is a whitespace character.
            pass
        else:

            # If the cog was specified

            lower_cogs = [c.lower() for c in cogs]

            # If the cog actually exists.
            if cog.lower() in lower_cogs:

                # Get a list of all commands in the specified cog
                commands_list = self.bot.get_cog_commands(cogs[lower_cogs.index(cog.lower())])
                help_text = ''

                # Add details of each command to the help text
                # Command Name
                # Description
                # [Aliases]
                #
                # Format
                for command in commands_list:
                    help_text += f'```{command.name}```\n' \
                        f'**{command.description}**\n\n'

                    # Also add aliases, if there are any
                    if len(command.aliases) > 0:
                        help_text += f'**Aliases :** `{"`, `".join(command.aliases)}`\n\n\n'
                    else:
                        # Add a newline character to keep it pretty
                        # That IS the whole purpose of custom help
                        help_text += '\n'

                    # Finally the format
                    help_text += f'Format: `@{self.bot.user.name}#{self.bot.user.discriminator}' \
                        f' {command.name} {command.usage if command.usage is not None else ""}`\n\n\n\n'

                help_embed.description = help_text
            else:
                # Notify the user of invalid cog and finish the command
                await ctx.send('Invalid cog specified.\nUse `help` command to list all cogs.')
                return

        await ctx.send(embed=help_embed)

        return

    @commands.command(
        name='register',
        description='Registers you to make entries',
        aliases=['r'],
        usage='<text>'

    )

    async def register_command(self, ctx):
        self.update_journal()
        if str(ctx.message.author.id) in self.journal:
            await ctx.send(content="You have already registered!")
            return
        self.journal.update({str(ctx.message.author.id) : []})
        self.update_file()
        await ctx.send(content="You are now registered and can start making entries!")

    @commands.command(
        name='entry',
        description='Use format of \n!entry ETH 500 sats \n!entry BTC 8500 USD short\n!entry ADA 279 sats long 3x',
        aliases=['in', 'bought', 'enter', 'entered'],
        usage='<text>'
        )
    async def entry_command(self, ctx):
        msg = ctx.message.content
        parts = ''
        ticker = ''
        price = ''
        currency = ''
        try:
            parts = msg.split()
            ticker = parts[1].upper()
            price = parts[2]
            currency = parts[3].upper()
        except IndexError:
            await ctx.send(content="Please use the correct format on your entry and try again")
            return

        if price.isdigit():
            price = int(price)
            #print('it is an int')
        else:
            try:
                price = float(price)
                #print('it is a float')
            except ValueError:
                await ctx.send(content="Please use the correct format on your entry and try again")
                return

        if ticker.isdigit() or currency.isdigit():
            await ctx.send(content="Please use the correct format on your entry and try again")
            return

        self.update_journal()

        if str(ctx.message.author.id) not in self.journal.keys():
            self.journal.update({str(ctx.message.author.id): []})
            await ctx.send(content="Welcome, your first entry automatically has registered you with the bot to record future entries")

        text = 'Your entry into ' + ticker + ' at ' + str(price) + ' ' + currency + ' has been added to the list'

        if len(parts) == 5:
            side = parts[4]
            self.journal[str(ctx.message.author.id)].append({"Cancelled": False, "EntryExit": "Entry", "Timestamp": str(ctx.message.created_at), "Ticker": ticker, "Price": price, "Currency": currency, "Side": side})
            text = 'Your entry into ' + ticker + ' at ' + str(price) + ' ' + currency + ' ' + side + ' has been added to the list'
        elif len(parts) == 6:
            side = parts[4]
            leverage = parts[5]
            self.journal[str(ctx.message.author.id)].append(
                {"Cancelled": False, "EntryExit": "Entry", "Timestamp": str(ctx.message.created_at), "Ticker": ticker, "Price": price, "Currency": currency,
                 "Side": side, "Leverage": leverage})
            text = 'Your entry into ' + ticker + ' at ' + str(
                price) + ' ' + currency + ' ' + leverage + ' ' + side + ' has been added to the list'
        else:
            self.journal[str(ctx.message.author.id)].append(
                {"Cancelled": False, "EntryExit": "Entry", "Timestamp": str(ctx.message.created_at), "Ticker": ticker, "Price": price, "Currency": currency})

        self.update_file()

        await ctx.send(content=f"{text}")



    @commands.command(
        name='exit',
        description='Use format of \n!exit ETH 500 sats \n!exit BTC 8500 USD short\n!exit ADA 279 sats long 3x',
        aliases=['out', 'sold', 'exited'],
        usage='<text>'
        )
    async def exit_command(self, ctx):
        msg = ctx.message.content
        parts = ''
        ticker = ''
        price = ''
        currency = ''
        try:
            parts = msg.split()
            ticker = parts[1].upper()
            price = parts[2]
            currency = parts[3].upper()
        except IndexError:
            await ctx.send(content="Please use the correct format on your entry and try again")
            return

        if price.isdigit():
            price = int(price)
            #print('it is an int')
        else:
            try:
                price = float(price)
                #print('it is a float')
            except ValueError:
                await ctx.send(content="Please use the correct format on your entry and try again")
                return

        if ticker.isdigit() or currency.isdigit():
            await ctx.send(content="Please use the correct format on your entry and try again")
            return

        self.update_journal()

        text = 'Your exit out of ' + ticker + ' at ' + str(price) + ' ' + currency + ' has been added to the list'

        if len(parts) == 5:
            side = parts[4]
            c = 0
            percent = 0
            index = -1
            while c in range(len(self.journal[str(ctx.message.author.id)])):
                if (self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                    "Cancelled"] == False) and ticker == (self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                    "Ticker"]) and currency == (self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                    "Currency"]) and self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"] == "Entry":
                    percent = round((price/(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                        "Price"]) - 1)*100, 2)
                    if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Side"] == "short":
                        percent = percent * (-1)
                    index = len(self.journal[str(ctx.message.author.id)]) - (1 + c)
                    c = len(self.journal[str(ctx.message.author.id)])
                c += 1
            self.journal[str(ctx.message.author.id)].append({"Cancelled": False, "EntryExit": "Exit", "Timestamp": str(ctx.message.created_at), "Ticker": ticker, "Price": price, "Currency": currency, "Side": side, "Percent": percent, "IndexEntry":index})
            text = 'Your exit out of ' + ticker + ' at ' + str(price) + ' ' + currency + ' ' + side + ' has been added to the list for a ' + str(percent) + '% change from entry'
        elif len(parts) == 6:
            side = parts[4]
            leverage = parts[5]
            c = 0
            percent = 0
            index = -1
            while c in range(len(self.journal[str(ctx.message.author.id)])):
                if (self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                        "Cancelled"] == False) and ticker == (
                self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                    "Ticker"]) and currency == (
                self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                    "Currency"]) and self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"] == "Entry":
                    percent = round((price/(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                        "Price"]) - 1)*100, 2)
                    if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Side"] == "short":
                        percent = percent * (-1)
                    lev = int(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Leverage"].replace('x',''))
                    percent = percent * lev
                    index = len(self.journal[str(ctx.message.author.id)]) - (1 + c)
                    c = len(self.journal[str(ctx.message.author.id)])
                c += 1
            self.journal[str(ctx.message.author.id)].append(
                {"Cancelled": False, "EntryExit": "Exit", "Timestamp": str(ctx.message.created_at), "Ticker": ticker, "Price": price, "Currency": currency,
                 "Side": side, "Leverage": leverage, "Percent": percent, "IndexEntry": index})
            text = 'Your exit out of ' + ticker + ' at ' + str(
                price) + ' ' + currency + ' ' + leverage + ' ' + side + ' has been added to the list for ' + str(percent) +'% change from entry'
        else:
            c = 0
            percent = 0
            index = -1
            while c in range(len(self.journal[str(ctx.message.author.id)])):
                if (self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                        "Cancelled"] == False) and ticker == (
                self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                    "Ticker"]) and currency == (
                self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                    "Currency"]) and self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"] == "Entry":
                    percent = round((price/(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1 + c)][
                        "Price"]) - 1)*100, 2)
                    index = len(self.journal[str(ctx.message.author.id)]) - (1 + c)
                    c = len(self.journal[str(ctx.message.author.id)])
                c += 1
            self.journal[str(ctx.message.author.id)].append(
                {"Cancelled": False, "EntryExit": "Exit", "Timestamp": str(ctx.message.created_at), "Ticker": ticker, "Price": price, "Currency": currency, "Percent": percent, "IndexEntry":index})
            text += ' for ' + str(percent) + '% change from entry'

        self.update_file()

        await ctx.send(content=f"{text}")


    @commands.command(
        name='cancel',
        description='THIS IS IRREVERSIBLE Cancels the last order(s) use like:\n !cancel \n!cancel 3',
        usage='<text>'
        )
    async def cancel_command(self, ctx):
        msg = ctx.message.content
        self.update_journal()
        parse = msg.split()
        try:
            #print(parse[2])
            amt = int(parse[1])
        except IndexError:
            #print(len(self.journal[str(ctx.message.author.id)])-1)
            x = 0
            while x < len(self.journal[str(ctx.message.author.id)]):
                if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)])-(1+x)]["Cancelled"] == False:
                    self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)])-(1+x)]["Cancelled"] = True
                    self.update_file()
                    await ctx.send(content="Your last entry has been cancelled")
                    x = len(self.journal[str(ctx.message.author.id)])
                    return
                x += 1
        except ValueError:
            await ctx.send(content="Please use the correct format on your entry and try again")
            return

        if amt > len(self.journal[str(ctx.message.author.id)]):
            await ctx.send(content="You can't cancel more entries than you have")
            return

        for c in range(amt):
            x = 0
            while x < len(self.journal[str(ctx.message.author.id)]):
                if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)])-(1+x)]["Cancelled"] == False:
                    self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)])-(1+x)]["Cancelled"] = True
                    self.update_file()
                    x = len(self.journal[str(ctx.message.author.id)])
                x += 1


        self.update_file()

        await ctx.send(content="Your last "+ str(amt) + " entries have been cancelled")


    @commands.command(
        name='last',
        description='checks your last uncancelled journal entry',
        usage='<text>'
        )
    async def last_command(self, ctx):
        self.update_journal()
        for c in range(len(self.journal[str(ctx.message.author.id)])):
            if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Cancelled"] == False:
                await ctx.send(content='Your last entry was: \n"' +
                                       str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"]) +
                                ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Ticker"]) +
                               ' at ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Price"]) +
                               ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Currency"]) + '"')
                return

        await ctx.send(content="You don't have any entries recorded or they may have all been cancelled.")

    @commands.command(
        name='trades',
        description='checks last 14 uncancelled entries listed top down from newest to oldest',
        aliases=['logs', 'log'],
        usage='<text>'
        )
    async def log_command(self, ctx):
        self.update_journal()
        text='<@' + str(ctx.message.author.id) + '>\n'
        listlength = 0
        for c in range(len(self.journal[str(ctx.message.author.id)])):
            if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Cancelled"] == False:
                text += '•**' + (str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"]) +
                            '** ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Ticker"]))
                if 'Side' in self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)].keys():
                    text += ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Side"])
                if 'Leverage' in self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)].keys():
                    text += ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Leverage"])
                text += ' at ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Price"]) + ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Currency"])
                if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"] == "Exit":
                    text += ' for ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Percent"]) + '%'
                text += '\n'
                listlength += 1
            if listlength == 14:
                await ctx.send(content=f"{text}")
                return

        await ctx.send(content=f"{text}")

    @commands.command(
        name='alltrades',
        description='checks and PM\'s all uncancelled entries listed top down from newest to oldest',
        aliases=['logsfull', 'logfull', 'tradeall', 'tradesall', 'alltrade', ],
        usage='<text>'
        )
    async def logfull_command(self, ctx):
        self.update_journal()
        text=''
        listlength = 0
        for c in range(len(self.journal[str(ctx.message.author.id)])):
            if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Cancelled"] == False:
                text += '•**' + (str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"]) +
                            '** ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Ticker"]))
                if 'Side' in self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)].keys():
                    text += ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Side"])
                if 'Leverage' in self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)].keys():
                    text += ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Leverage"])
                text += ' at ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Price"]) + ' ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Currency"])
                if self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["EntryExit"] == "Exit":
                    text += ' for ' + str(self.journal[str(ctx.message.author.id)][len(self.journal[str(ctx.message.author.id)]) - (1+c)]["Percent"]) + '%'
                text += '\n'
                listlength += 1
            if listlength == 10:
                await ctx.send(content=f"{text}")
                text = ''
                listlength = 0

        await ctx.author.send(content=f"{text}")

def setup(bot):
    bot.add_cog(Journal(bot))
    # Adds the JsonEdit commands to the bot
    # Note: The "setup" function has to be there in every cog file
