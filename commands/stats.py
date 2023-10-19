import nextcord
from nextcord.ext import commands

class stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="stats", description="Coinflip!")
    async def stats(self,
                  interaction : nextcord.Interaction, 
                  user : nextcord.User = None):
        fetchUser = interaction.user
        if user != None:
            fetchUser = user

        data = self.supabase.table('Users').select("*").eq("id", fetchUser.id).execute().data[0]
        embed = nextcord.Embed(title="Gamba Stats!", description="", color=nextcord.Colour.green())
        embed.add_field(name="Total Coins Wagered:", value=f"{data['coins_wagered']:,}", inline=False)
        embed.add_field(name="Total Coins Won:", value=f"{data['coins_won']:,}", inline=False)
        embed.add_field(name="Total Coins Lost:", value=f"{data['coins_lost']:,}", inline=False)
        embed.add_field(name="Total Coins Paid:", value=f"{data['coins_paid']:,}", inline=False)
        embed.set_thumbnail(url=fetchUser.avatar)
        await interaction.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(stats(bot))