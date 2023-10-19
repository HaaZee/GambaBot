import nextcord
from nextcord.ext import commands

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="help", description="List available commands")
    async def help(self, interaction : nextcord.Interaction):
        embed = nextcord.Embed(title="Gama Bot's Help", description="See a list of commands")
        for command in self.bot.walk_commands():
            print(command.name)
            desc = command.description
            if not desc or desc is None or desc == "":
                desc = "No Description Provided."
            embed.add_field(name=f"/{command.name}{command.signature if command.signature is not None else ''}`", value=desc)
        await interaction.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(help(bot))