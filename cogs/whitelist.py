import discord
from discord.ext import commands

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelist = set()  # Using a set to store whitelisted user IDs

    @commands.command(name="whitelist_add")
    @commands.has_permissions(administrator=True)
    async def whitelist_add(self, ctx, user: discord.User):
        """Add a user to the whitelist."""
        self.whitelist.add(user.id)
        await ctx.send(f"{user.mention} has been added to the whitelist.")

    @commands.command(name="whitelist_remove")
    @commands.has_permissions(administrator=True)
    async def whitelist_remove(self, ctx, user: discord.User):
        """Remove a user from the whitelist."""
        self.whitelist.discard(user.id)
        await ctx.send(f"{user.mention} has been removed from the whitelist.")

    def is_whitelisted(self, user_id):
        return user_id in self.whitelist

async def setup(bot):
    await bot.add_cog(Whitelist(bot))
