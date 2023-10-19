from typing import Optional
import nextcord
from nextcord.ext import commands

class baltop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="baltop", description="See the top users balances!")
    async def baltop(self,
                     interaction : nextcord.Interaction, 
                     number: Optional[int] = nextcord.SlashOption(name="fetch", default=10)):
        amountToFetch = number
        embed = nextcord.Embed(title=f"Bal top {amountToFetch}!", description="", color=nextcord.Colour.green())
        
        if amountToFetch > 10:
            embed.add_field(name=f"Only showing:", value="10 results", inline=False)    

        data = self.supabase.table('Users').select("id, coins").order('coins', desc=True).limit(amountToFetch).execute()
        for i in data.data:
            embed.add_field(name=f"{await self.bot.fetch_user(i['id'])}", value=f"{i['coins']:,}", inline=False)    
        
        embed.set_thumbnail(url=interaction.user.avatar)
        await interaction.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(baltop(bot))