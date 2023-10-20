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

        # Parse the wager into an int and handle all ins
        wager = ownerCoins if betamount == "all" else moneyHelper.parse_string_to_int(betamount)

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
        if channelId == None:
            await interaction.send("This server is missing a `public-coinflips` text channel. Please ask a staff member to create it.")
            return
        newPublicCoinflipEmbed = nextcord.Embed(title="Gamba!", description="New Coinflip", colour=nextcord.Colour.green())
        newPublicCoinflipEmbed.add_field(name="Creator:", value=f"{coinflipOwner.mention}", inline=False)
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
            if interaction.user == coinflipOwner:
                return
            
            # Disable buttons
            joinButton.disabled = True
            inviteBotButton.disabled = True
            await interaction.message.edit(embed=newPublicCoinflipEmbed, view=view)

            # Check joiner can afford
            joiner = interaction.user
            joinerCoins = self.supabase.table('Users').select("coins, coins_wagered, coins_won,coins_lost").eq("id", joiner.id).execute().data[0]['coins']
            if joinerCoins < wager:
                await interaction.send("You do not have enough money!", ephemeral=True)
                joinButton.disabled = False
                inviteBotButton.disabled = False
                await interaction.message.edit(embed=newPublicCoinflipEmbed, view=view)
                return
            
            await channelId.send(f"{joiner.mention} Joined {coinflipOwner.mention}'s Coinflip for {wager:,}!")

            await Run(interaction, joiner)

        async def InviteBotButtonCallback(interaction):
            # Check only owner inviting bot
            if interaction.user != coinflipOwner:
                return
            
            # Disable buttons
            joinButton.disabled = True
            inviteBotButton.disabled = True
            await interaction.message.edit(embed=newPublicCoinflipEmbed, view=view)

            await channelId.send(f"Bot Joe Joined {coinflipOwner.mention}'s Coinflip for {wager}!")

            await Run(interaction, "Bot Joe")

        async def Run(interaction, joiner):
             # Update embed with joiner
            newPublicCoinflipEmbed.remove_field(2)
            newPublicCoinflipEmbed.add_field(name="Joined:", value=joiner.mention if joiner != "Bot Joe" else joiner, inline=False)
            await interaction.message.edit(embed=newPublicCoinflipEmbed)

            # Generate results
            (winner, loser) = RollCoinflip(joiner)

            # Pay out results
            UpdateWinner(winner)
            UpdateLoser(loser)

            # Send result message 
            await SendResult(winner, loser)

            # Update embed with Winner
            newPublicCoinflipEmbed.add_field(name="Winner:", value=winner.mention if winner != "Bot Joe" else winner, inline=False)
            await interaction.message.edit(embed=newPublicCoinflipEmbed)
        
        def RollCoinflip(joiner):
            if bool(random.randint(0,1)):
                return (coinflipOwner, joiner)
            return (joiner, coinflipOwner)
            
        async def SendResult(winner, loser):
            winnerMention = winner.mention if winner != "Bot Joe" else winner
            loserMention = loser.mention if loser != "Bot Joe" else loser
            await channelId.send(f"{winnerMention} beat {loserMention} winning {wager:,}!")

        def UpdateWinner(winner):
            if winner == "Bot Joe":
                return
            winnerData = self.supabase.table('Users').select("coins, coins_wagered, coins_won,coins_lost").eq("id", winner.id).execute().data[0]
            updateData = {}
            updateData["coins_won"] = winnerData['coins_won'] + wager
            updateData["coins"] = winnerData['coins'] + wager
            updateData["coins_wagered"] = winnerData['coins_wagered'] + wager
            self.supabase.table('Users').update(updateData).eq('id', winner.id).execute()
        
        def UpdateLoser(loser):
            if loser == "Bot Joe":
                return
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
