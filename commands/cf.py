import nextcord
from nextcord.ext import commands
from shared import moneyHelper
import random

class cf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="cf", description="Coinflip!")
    async def cf(self,
                interaction : nextcord.Interaction, 
                number: str = nextcord.SlashOption(name="amount")):
        # input box/args if how mnany to wager
        if number != "all":
            wager = moneyHelper.parse_string_to_int(number)

        # check if bal enough, store bal
        data = self.supabase.table('Users').select("coins, coins_wagered, coins_won,coins_lost").eq("id", interaction.user.id).execute().data[0]
        coins = data['coins']
        if wager == "all":
            wager = coins

        coinsWageredStat = data['coins_wagered'] + wager
        updateData = {"coins_wagered": coinsWageredStat}
        if coins >= wager:
            # calculate win/loss
            rand = random.randint(0,1)
            if rand == 0:
                coins += wager
                colour = nextcord.Colour.green()
                result = "Win"
                updateData["coins_won"] = data['coins_won'] + wager
            else:
                coins -= wager
                colour = nextcord.Colour.red()
                result = "Loss"
                updateData["coins_lost"] = data['coins_lost'] + wager

            updateData["coins"] = coins

            # update coins in db with new number
            data = self.supabase.table('Users').update(updateData).eq('id', interaction.user.id).execute()
            
            embed = nextcord.Embed(title="Gamba!", description="", color=colour)
            embed.add_field(name="Wagered:", value=f"{wager:,}", inline=False)
            embed.add_field(name=f"{result} amount:", value=f"{wager:,}", inline=False)
            embed.add_field(name="New Balance:", value=f"{coins:,}", inline=False)
            embed.set_thumbnail(url=interaction.user.avatar)
            await interaction.send(embed=embed)
            return

        embed = nextcord.Embed(title="Gamba!", description="", color=nextcord.Colour.red())
        embed.add_field(name="Wagered:", value=f"{wager:,}", inline=False)
        embed.add_field(name="Result:", value="You do not have enough coins.", inline=False)
        embed.set_thumbnail(url=interaction.user.avatar)
        await interaction.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(cf(bot))