import nextcord
from nextcord.ext import commands

class bal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="bal", description="See your coins!")
    async def bal(self, interaction : nextcord.Interaction, user : nextcord.User = None):
        fetchUser = interaction.user

        if user != None:
            fetchUser = user

        coinsData = self.supabase.table('Users').select("coins").eq("id", fetchUser.id).execute().data
        if len(coinsData) < 1:
            await interaction.send("User not found.", ephemeral=True)
            return

        coinCount = coinsData[0]['coins']

        embed = nextcord.Embed(title="Coin Balance", description="", colour=nextcord.Colour.green())
        embed.add_field(name="User:", value=f"{await self.bot.fetch_user(fetchUser.id)}", inline=False)
        embed.add_field(name="Balance:", value=f"{coinCount:,}", inline=False)
        embed.set_thumbnail(url=fetchUser.avatar)
        await interaction.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(bal(bot))
