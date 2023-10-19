import nextcord
from nextcord.ext import commands
from nextcord.ui import *
from shared import moneyHelper
import random

class cf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="cf", description="Coinflip!")
    async def cf(self,
                 interaction : nextcord.Interaction, 
                 betamount: str = nextcord.SlashOption(name="amount")):

        coinflipOwner = interaction.user
        ownerData = self.supabase.table('Users').select("coins, coins_wagered, coins_won,coins_lost").eq("id", interaction.user.id).execute().data[0]
        ownerCoins = ownerData['coins']

        # Parse the wager into an int
        wager = moneyHelper.parse_string_to_int(betamount)
        if betamount == "all":
            wager = moneyHelper.parse_string_to_int(ownerCoins)

        # Check if the creator has enough balance for the coinflip
        if ownerCoins < wager:
            embed = nextcord.Embed(title="Gamba!", description="", color=nextcord.Colour.red())
            embed.add_field(name="Wagered:", value=f"{wager:,}", inline=False)
            embed.add_field(name="Result:", value="You do not have enough coins.", inline=False)
            embed.set_thumbnail(url=interaction.user.avatar)
            await interaction.send(embed=embed)
            return
        
        # Send message to coinflip channel
        channelId = nextcord.utils.get(interaction.guild.channels, name="public-coinflips")
        newPublicCoinflipEmbed = nextcord.Embed(title="Gamba!", description="New Coinflip", colour=nextcord.Colour.green())
        newPublicCoinflipEmbed.add_field(name="Creator:", value=f"{await self.bot.fetch_user(interaction.user.id)}", inline=False)
        newPublicCoinflipEmbed.add_field(name="Wagered:", value=f"{wager:,}", inline=False)
        newPublicCoinflipEmbed.add_field(name="Joined:", value="Nobody has joined yet.", inline=False)

        # Add Join, Invite Bot button
        joinButton = Button(style=nextcord.ButtonStyle.success, label="Join", disabled=False)
        inviteBotButton = Button(style=nextcord.ButtonStyle.danger, label="Invite Bot", disabled=False)

        view = View()
        view.add_item(joinButton)
        view.add_item(inviteBotButton)

        await channelId.send(embed=newPublicCoinflipEmbed, view=view)

        async def JoinCallback(interaction):
            joiner = interaction.user
            # TODO: Check if they have enough money
            await channelId.send(f"{await self.bot.fetch_user(joiner.id)} Joined {coinflipOwner}'s Coinflip for {wager}!")

            # Update embed with joiner
            newPublicCoinflipEmbed.remove_field(2)
            newPublicCoinflipEmbed.add_field(name="Joined:", value=joiner, inline=False)
            await interaction.message.edit(embed=newPublicCoinflipEmbed)

            # TODO: On player join @ both players and start countdown

            # Generate results
            (winner, loser) = RollCoinflip(joiner)

            # Pay out results
            UpdateWinner(winner)
            UpdateLoser(loser)

            # Send result message 
            await SendResult(winner, loser)

            # Update embed with Winner. TODO: @ the players
            newPublicCoinflipEmbed.add_field(name="Winner:", value=winner, inline=False)
            await interaction.message.edit(embed=newPublicCoinflipEmbed)

        async def InviteBotButtonCallback(interaction):
            await channelId.send("Bot Joe Joined!")

        def RollCoinflip(joiner):
            if bool(random.randint(0,1)):
                return (coinflipOwner, joiner)
            return (joiner, coinflipOwner)
            
        async def SendResult(winner, loser):
            await channelId.send(f"{winner} beat {loser} winning {wager:,}!!")

        def UpdateWinner(winner):
            winnerData = self.supabase.table('Users').select("coins, coins_wagered, coins_won,coins_lost").eq("id", winner.id).execute().data[0]
            updateData = {}
            updateData["coins_won"] = winnerData['coins_won'] + wager
            updateData["coins"] = winnerData['coins'] + wager
            updateData["coins_wagered"] = winnerData['coins_wagered'] + wager
            self.supabase.table('Users').update(updateData).eq('id', winner.id).execute()
        
        def UpdateLoser(loser):
            loserData = self.supabase.table('Users').select("coins, coins_wagered, coins_won,coins_lost").eq("id", loser.id).execute().data[0]
            updateData = {}
            updateData["coins_lost"] = loserData['coins_lost'] + wager
            updateData["coins"] = loserData['coins'] - wager
            updateData["coins_wagered"] = loserData['coins_wagered'] + wager
            self.supabase.table('Users').update(updateData).eq('id', loser.id).execute()

        inviteBotButton.callback = InviteBotButtonCallback
        joinButton.callback = JoinCallback

def setup(bot: commands.Bot):
    bot.add_cog(cf(bot))