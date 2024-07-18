import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput, Button

class ConfirmButton(Button):
    def __init__(self, label: str, style: discord.ButtonStyle, emoji: str, callback):
        super().__init__(label=label, style=style, emoji=emoji)
        self.callback_function = callback

    async def callback(self, interaction: discord.Interaction):
        await self.callback_function(interaction)

class CloseButton(Button):
    def __init__(self, label: str, style: discord.ButtonStyle, emoji: str, channel: discord.TextChannel, bot: commands.Bot):
        super().__init__(label=label, style=style, emoji=emoji)
        self.channel = channel
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        closed_category = discord.utils.get(guild.categories, name="closed tickets")

        if not closed_category:
            closed_category = await guild.create_category("closed tickets")

        await self.channel.edit(category=closed_category)

        # Set permissions so only the admin can see it
        admin_role = discord.utils.get(guild.roles, name="Admin")  # Adjust role name as needed
        await self.channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
        if admin_role:
            await self.channel.set_permissions(admin_role, read_messages=True, send_messages=True)

        await interaction.response.send_message("This ticket has been moved to closed tickets.", ephemeral=True)

async def yes_callback(interaction: discord.Interaction, bot: commands.Bot, sending: str, receiving: str):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="tickets")

    if not category:
        category = await guild.create_category("tickets")

    ticket_number = len(category.channels) + 1
    channel = await category.create_text_channel(f"exchange-{ticket_number}")

    # Set permissions so only the admin and the user who created the ticket can see it
    admin_role = discord.utils.get(guild.roles, name="Admin")  # Adjust role name as needed
    await channel.set_permissions(guild.default_role, read_messages=False)
    await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    if admin_role:
        await channel.set_permissions(admin_role, read_messages=True, send_messages=True)

    embed = discord.Embed(
        title=f"{sending.split()[1]} Exchange",
        description="Please be patient and wait for a reply as we are not always available.",
        color=0x77B255  # This is within the valid range
    )
    embed.add_field(name="Sending:", value=sending, inline=True)
    embed.add_field(name="Receiving:", value=receiving, inline=True)

    close_button = CloseButton(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", channel=channel, bot=bot)
    view = View(timeout=None)
    view.add_item(close_button)

    await channel.send(embed=embed, view=view)
    await interaction.followup.send(f"Your ticket has been created: {channel.mention}", ephemeral=True)

async def no_callback(interaction: discord.Interaction):
    await interaction.response.edit_message(content="This exchange request has been canceled.", embed=None, view=None)

class ConfirmView(View):
    def __init__(self, bot: commands.Bot, sending: str, receiving: str):
        super().__init__(timeout=None)
        self.add_item(ConfirmButton(label="Continue", style=discord.ButtonStyle.success, emoji="<:Yes:1263193152995459123>", callback=lambda i: yes_callback(i, bot, sending, receiving)))
        self.add_item(ConfirmButton(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌", callback=no_callback))

class CryptoTypeSelect(Select):
    def __init__(self, bot: commands.Bot, sending: str, receiving: str):
        options = [
            discord.SelectOption(label="Bitcoin", description="Send in Bitcoin", emoji="<:BTC:1262616763619610657>"),
            discord.SelectOption(label="Litecoin", description="Send in Litecoin", emoji="<:LTC:1262616772335370341>"),
            discord.SelectOption(label="USDT", description="Send in USDT", emoji="<:USDT:1262616779692445706>"),
            discord.SelectOption(label="Ethereum", description="Send in Ethereum", emoji="<:ETH:1262616771106570280>"),
        ]
        super().__init__(placeholder="Select crypto type", min_values=1, max_values=1, options=options)
        self.bot = bot
        self.sending = sending
        self.receiving = receiving

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        self.sending += f" ({selected_option})"
        embed = discord.Embed(
            title=f"{self.sending.split()[1]} Exchange",
            description="Make sure everything below fits what you're looking for before you open the ticket!",
            color=0xc70000
        )
        embed.add_field(name="Sending:", value=self.sending, inline=True)
        embed.add_field(name="Receiving:", value=self.receiving, inline=True)

        view = ConfirmView(self.bot, self.sending, self.receiving)
        await interaction.response.edit_message(embed=embed, view=view)

class AmountModal(Modal):
    def __init__(self, bot: commands.Bot, sending_option: str, receiving_option: str):
        super().__init__(title="Exchange Sending Amount")
        self.bot = bot
        self.sending_option = sending_option
        self.receiving_option = receiving_option

        self.amount_input = TextInput(
            label="How much will you be sending?",
            placeholder="Format Example: 50 OR 53.80",
            min_length=2,
            max_length=10,
            required=True
        )
        self.add_item(self.amount_input)

    def calculate_fee(self, sending_option: str, amount: float) -> float:
        # Define fees
        fees = {
            "Crypto": 0.05,
            "PayPal": 0.10,
            "Cashapp": 0.08,
            "Zelle": 0.10,
            "Apple Pay": 0.08,
        }

        if amount < 30:
            # Double the fee if sending amount is under $30, except for crypto to crypto
            if sending_option == "Crypto":
                fee_percentage = 0.05
            else:
                fee_percentage = fees[sending_option] * 2
        else:
            fee_percentage = fees[sending_option]

        return fee_percentage

    async def on_submit(self, interaction: discord.Interaction):
        sending_amount = float(self.amount_input.value)
        sending = f"${sending_amount} {self.sending_option}"

        # Calculate fee
        fee_percentage = self.calculate_fee(self.sending_option, sending_amount)

        receiving_amount = sending_amount * (1 - fee_percentage)
        receiving = f"${receiving_amount:.2f} {self.receiving_option}"

        if self.sending_option == "Crypto":
            select = CryptoTypeSelect(self.bot, sending, receiving)
            view = View(timeout=None)
            view.add_item(select)
            await interaction.response.edit_message(embed=None, view=view)
        else:
            embed = discord.Embed(
                title=f"{self.sending_option} Exchange",
                description="Make sure everything below fits what you're looking for before you open the ticket!",
                color=0xc70000
            )
            embed.add_field(name="Sending:", value=sending, inline=True)
            embed.add_field(name="Receiving:", value=receiving, inline=True)

            view = ConfirmView(self.bot, sending, receiving)
            await interaction.response.edit_message(embed=embed, view=view)

class ReceivingSelect(Select):
    def __init__(self, bot: commands.Bot, sending_option: str):
        self.bot = bot
        self.sending_option = sending_option
        options = self.get_options(sending_option)
        super().__init__(placeholder="Select receiving option", min_values=1, max_values=1, options=options)

    def get_options(self, sending_option: str):
        options_map = {
            "Crypto": [
                discord.SelectOption(label="Cashapp", description="Receive in Cashapp", emoji="<:Cashapp:1263197850356027483>"),
                discord.SelectOption(label="Apple Pay", description="Receive in Apple Pay", emoji="<:ApplePay:1263197854038757426>"),
                discord.SelectOption(label="PayPal", description="Receive in PayPal", emoji="<:Paypal:1263197851664515132>"),
                discord.SelectOption(label="Crypto", description="Receive in Crypto", emoji="<:Cryptos:1263197855150112860>")
            ],
            "Cashapp": [
                discord.SelectOption(label="PayPal", description="Receive in PayPal", emoji="<:Paypal:1263197851664515132>"),
                discord.SelectOption(label="Crypto", description="Receive in Crypto", emoji="<:Cryptos:1263197855150112860>"),
                discord.SelectOption(label="Apple Pay", description="Receive in Apple Pay", emoji="<:ApplePay:1263197854038757426>")
            ],
            "PayPal": [
                discord.SelectOption(label="Cashapp", description="Receive in Cashapp", emoji="<:Cashapp:1263197850356027483>"),
                discord.SelectOption(label="Crypto", description="Receive in Crypto", emoji="<:Cryptos:1263197855150112860>"),
                discord.SelectOption(label="Apple Pay", description="Receive in Apple Pay", emoji="<:ApplePay:1263197854038757426>")
            ],
            "Apple Pay": [
                discord.SelectOption(label="Cashapp", description="Receive in Cashapp", emoji="<:Cashapp:1263197850356027483>"),
                discord.SelectOption(label="Crypto", description="Receive in Crypto", emoji="<:Cryptos:1263197855150112860>"),
                discord.SelectOption(label="PayPal", description="Receive in PayPal", emoji="<:Paypal:1263197851664515132>")
            ],
            "Zelle": [
                discord.SelectOption(label="PayPal", description="Receive in PayPal", emoji="<:Paypal:1263197851664515132>"),
                discord.SelectOption(label="Cashapp", description="Receive in Cashapp", emoji="<:Cashapp:1263197850356027483>"),
                discord.SelectOption(label="Crypto", description="Receive in Crypto", emoji="<:Cryptos:1263197855150112860>"),
                discord.SelectOption(label="Apple Pay", description="Receive in Apple Pay", emoji="<:ApplePay:1263197854038757426>")
            ]
        }
        return options_map.get(sending_option, [
            discord.SelectOption(label="PayPal", description="Receive in PayPal", emoji="<:Paypal:1263197851664515132>"),
            discord.SelectOption(label="Cashapp", description="Receive in Cashapp", emoji="<:Cashapp:1263197850356027483>"),
            discord.SelectOption(label="Crypto", description="Receive in Crypto", emoji="<:Cryptos:1263197855150112860>"),
            discord.SelectOption(label="Apple Pay", description="Receive in Apple Pay", emoji="<:ApplePay:1263197854038757426>")
        ])

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        modal = AmountModal(self.bot, sending_option=self.sending_option, receiving_option=selected_option)
        await interaction.response.send_modal(modal)

class ExchangeSelect(Select):
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(label="PayPal", description="10% fee", emoji="<:Paypal:1263197851664515132>"),
            discord.SelectOption(label="Cashapp", description="8% fee", emoji="<:Cashapp:1263197850356027483>"),
            discord.SelectOption(label="Apple Pay", description="8% fee", emoji="<:ApplePay:1263197854038757426>"),
            discord.SelectOption(label="Zelle", description="10% fee", emoji="<:Zelle:1263197853036056789>"),
            discord.SelectOption(label="Crypto", description="5% fee", emoji="<:Cryptos:1263197855150112860>"),
        ]
        super().__init__(placeholder="Select option", min_values=1, max_values=1, options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        embed = discord.Embed(
            title="Receiving Payment",
            description=f"You have selected **{selected_option}** as your sending payment. What would you like to **receive**?",
            color=0xc70000
        )
        select = ReceivingSelect(self.bot, sending_option=selected_option)
        view = View(timeout=None)
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class Exchange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="exchange", description="Request an exchange")
    async def exchange(self, interaction: discord.Interaction):
        if interaction.user.id not in self.bot.owners:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Request an Exchange",
            description=(
                "You can request an exchange by selecting the appropriate option below for the payment type you'll be sending with. "
                "Follow the instructions and fill out the fields as requested.\n\n"
                "- **Reminder**\n\n"
                "Please read our <#1263204206861488229> before creating an Exchange.\n\n"
                "- **Minimum Fees**\n\n"
                "Unlike other exchangers, we have no minimum fee, but exchanges under $30 may be subject to doubled fees to maintain the integrity of our server."
            ),
            color=0xc70000
        )

        select = ExchangeSelect(self.bot)
        view = View(timeout=None)
        view.add_item(select)

        await interaction.response.send_message("Exchange request message has been sent.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Exchange(bot))
