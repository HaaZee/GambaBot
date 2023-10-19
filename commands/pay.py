import nextcord
from nextcord.ext import commands
from shared import moneyHelper

class pay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="pay", description="Coinflip!")
    async def pay(self,
                  interaction : nextcord.Interaction, 
                  user : nextcord.User,
                  number: str = nextcord.SlashOption(name="amount")):
        amount = moneyHelper.parse_string_to_int(number)
        payee = user

        # Fetch all information
        data = self.supabase.table('Users').select("coins, coins_paid").eq("id", interaction.user.id).execute().data[0]
        senderCoins = data['coins']
        totalCoinsPaid = data['coins_paid']
        if amount > senderCoins:
            embed = nextcord.Embed(title="Pay!", description="", color=nextcord.Colour.red())
            embed.add_field(name="Insufficient Balance:", value=f"{senderCoins:,}", inline=False)
            embed.add_field(name="Failed to pay user:", value=payee, inline=False)
            embed.set_thumbnail(url=interaction.user.avatar)
            await interaction.send(embed=embed)
            return

        # Fetch the coins of the payee (person being paid)
        payeeCoins = self.supabase.table('Users').select("coins").eq("id", payee.id).execute().data[0]['coins']
        payeeCoins += amount

        # Update the coins of the payee
        updateDataPayee = {"coins": payeeCoins}
        data, count = self.supabase.table('Users').update(updateDataPayee).eq('id',payee.id).execute()

        # Update the coins and the coins_paid of the sender
        senderCoins -= amount
        totalCoinsPaid += amount
        updateDataSender = {"coins": senderCoins, "coins_paid": totalCoinsPaid}
        data, count = self.supabase.table('Users').update(updateDataSender).eq('id', interaction.user.id).execute()
        
        embed = nextcord.Embed(title="Pay!", description="", color=nextcord.Colour.green())
        embed.add_field(name="Successfully paid user:", value=payee, inline=False)
        embed.add_field(name="Payee new balance:", value=f"{payeeCoins:,}", inline=False)
        embed.add_field(name="Sender new balance:", value=f"{senderCoins:,}", inline=False)
        embed.set_thumbnail(url=interaction.user.avatar)
        await interaction.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(pay(bot))