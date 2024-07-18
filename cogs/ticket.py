import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

class TicketButton(Button):
    def __init__(self):
        super().__init__(label="📧", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        # Check if a category named "tickets" exists, if not, create it
        category = discord.utils.get(guild.categories, name="tickets")
        if category is None:
            category = await guild.create_category("tickets")

        # Create a new text channel for the ticket under the "tickets" category
        ticket_channel = await category.create_text_channel(f'ticket-{member.display_name}', overwrites={
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        })

        # Create the embed for the ticket
        embed = discord.Embed(
            description="Welcome to ExchangeW! To get started check out your options below.",
            color=3066993
        )
        embed.set_footer(text="Close this ticket by reacting with 🔒.")

        # Define the payment buttons
        buttons = [
            Button(label="Cashapp", style=discord.ButtonStyle.success, custom_id="cashapp"),
            Button(label="Apple Pay", style=discord.ButtonStyle.secondary, custom_id="apple_pay"),
            Button(label="Zelle", style=discord.ButtonStyle.secondary, custom_id="zelle"),
            Button(label="Swish", style=discord.ButtonStyle.secondary, custom_id="swish"),
            Button(label="Paypal", style=discord.ButtonStyle.primary, custom_id="paypal"),
            Button(label="Revolut", style=discord.ButtonStyle.primary, custom_id="revolut"),
            Button(label="Crypto", style=discord.ButtonStyle.danger, custom_id="crypto"),
        ]

        # Create a view and add the buttons to it
        view = View()
        for button in buttons:
            view.add_item(button)

        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f'Ticket created: {ticket_channel.mention}', ephemeral=True)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create_ticket", description="Create a new ticket")
    async def create_ticket(self, interaction: discord.Interaction):
        # Check if the user has the manage_channels permission
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You can't do this!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Exchange here",
            description="Start a new exchange by clicking 📧 below.",
            color=0x1E1F22
        )
        embed.set_footer(
            text="ExchangeW",
            icon_url="https://cdn.discordapp.com/icons/1208319723201232916/a_9d9a307113e919b68d6a6cc000a8bf48.gif?size=1024"
        )

        button = TicketButton()
        view = View()
        view.add_item(button)

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Ticket creation message has been sent.", ephemeral=True)

    @app_commands.command(name="close_ticket", description="Close the ticket")
    async def close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel

        if "ticket-" in channel.name:
            await channel.delete()
            await interaction.response.send_message("Ticket closed.", ephemeral=True)
        else:
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ticket(bot))
