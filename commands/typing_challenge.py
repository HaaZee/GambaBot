import nextcord
from nextcord.ext import commands

class typingchallenge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()


    @nextcord.slash_command(name="typingchallenge", description="Start a typing challenge")
    async def typingchallenge(self, interaction : nextcord.Interaction):
        print("Typing Challenge")

        
def setup(bot: commands.Bot):
    bot.add_cog(typingchallenge(bot))