import discord
from discord import app_commands
from discord.ext import commands

class TOS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tos", description="Send the Terms of Service")
    async def tos(self, interaction: discord.Interaction):
        if interaction.user.id not in self.bot.owners:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Terms of Service",
            description=(
                "Safety is our top priority, and have implemented various measures to maintain a secure and protected environment for our clients. "
                "That said, we will continue to uphold these standards in order to ensure trust and satisfactory within our community.\n\n"
                "- **Digital Fraud Policy**\n\n"
                "> We have zero tolerance for any form of fraud and take immediate action to address any suspected fraudulent behavior. "
                "We adhere to all laws and regulations and will not accept any illicit or illegally obtained funds.\n\n"
                "- **PayPal Transactions**\n\n"
                "> We require all PayPal Exchanges to be sent as Friends and Family from Balance, otherwise will not be accepted. "
                "In some cases, the fiat transaction may not be eligible for a refund.\n\n"
                "- **CashApp Transactions**\n\n"
                "> We require all CashApp Exchanges to be sent from CashApp balance, otherwise will not be accepted. "
                "In some cases, the fiat transaction may not be eligible for a refund.\n\n"
                "- **Venmo Transactions**\n\n"
                "> We require all Venmo Exchanges to be sent with Balance and the privacy set to private, otherwise will not be accepted. "
                "In some cases, the fiat transaction may not be eligible for a refund.\n\n"
                "- **Fiat Information**\n\n"
                "> We will not be held liable for any disputes, additional fees, holds, or limitations regarding fiat transactions as this is out of the Exchangers control. "
                "Exchangers will never cover any network, or withdrawal fees for crypto-currency, these fees will be covered by the client.\n\n"
                "- **Service Fees**\n\n"
                "You can see our service fees in [this link](https://discord.com/channels/1208319723201232916/1262899796470140959/1262928825902174218)."
            ),
            color=0xc70000
        )

        await interaction.response.send_message("/tos has been sent", ephemeral=True)
        await interaction.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TOS(bot))
