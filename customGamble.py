from typing import Optional
import nextcord
from nextcord.interactions import Interaction
from nextcord.ui import *
from nextcord.ext import commands





class Gamba(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

            


    @nextcord.slash_command(name="gamba", description="Create a custom bet!")
    async def ex(self, 
                 interaction : nextcord.Interaction,
                 bettitle : str = nextcord.SlashOption(name="bet_title"),
                 outcome1 : str = nextcord.SlashOption(name="outcome_1"),
                 outcome2 : str = nextcord.SlashOption(name="outcome_2"), 
                 outcome3 : Optional[str] = nextcord.SlashOption(name="outcome_3")
                 
                 ):
        

        bet_creator = interaction.user.id
        bet_message_embed = nextcord.Embed(
            title="New Bet",
            description=f"Bet: {bettitle}",
            color=nextcord.Color.blue()
        )

        # Define the Yes and No buttons
        yes_button = Button(style=nextcord.ButtonStyle.success, label=outcome1, disabled=False)
        no_button = Button(style=nextcord.ButtonStyle.danger, label=outcome2, disabled=False)
        lock_button = Button(emoji="🔐", disabled=False)
        
        
        # Create a view that contains the buttons
        view = View(timeout=120)
        view.add_item(yes_button)
        view.add_item(no_button)
        view.add_item(lock_button)

        if outcome3 is not None:
            third_button = Button(style=nextcord.ButtonStyle.blurple, label=outcome3, disabled=False)
            view.add_item(third_button)

        # Send the bet message with the buttons
        await interaction.send(embed=bet_message_embed, view=view)



        
        async def yes_button_callback(interaction):
            # Ask the user how much they want to bet via an ephemeral message
            await interaction.response.send_message(f"You voted '{outcome1}' How much would you like to bet? :", ephemeral=True)
                    
            
            
        async def no_button_callback(interaction):
            await interaction.response.send_message(f"You voted '{outcome2}' How much would you like to bet? :", ephemeral=True)

        async def third_button_callback(interaction):
            await interaction.response.send_message(f"You voted '{outcome3}' How much would you like to bet? :", ephemeral=True)

        async def lock_button_callback():
            yes_button.disabled = not yes_button.disabled
            no_button.disabled = not no_button.disabled
            if outcome3 is not None:
                third_button = not third_button.disabled
        

    
        yes_button.callback = yes_button_callback
        no_button.callback = no_button_callback
        if outcome3 is not None:
            third_button.callback = third_button_callback
        lock_button.callback = lock_button_callback


    



def setup(bot: commands.Bot):
    bot.add_cog(Gamba(bot))
