import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, time

#Load the Tokens/Keys
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COC_API =os.getenv("COC_API")
COC_TOKEN= os.getenv("COC_TOKEN")
channel_id= os.getenv("channel_id") #Chat channel ID
guild_id= os.getenv("guild_id") #Server ID
role_id= os.getenv("role_id") #Role ID

#Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#Set up intents
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

class ClashOfClans:
    def __init__(self):
        #Define COC request headers
        self.base_api_url = "https://api.clashofclans.com/v1"
        self.header = {"Authorization": f"Bearer {COC_API}"}
        self.request = requests.get(self.base_api_url, headers=self.header)

        #Verify we have connection to COC
        if self.request.status_code == 200:
            print("Success 200!")
        else:
            print(f"Error establishing connection: {self.request.status_code}")

        #Set clan tag
        self.clantag = "#UQ22PVUV"

        #Set Channel ID
        self.channel_id = channel_id #channel server id
        self.channel = bot.get_channel(self.channel_id)
        #Get server ID
        self.guild_id = guild_id
        self.guild = bot.get_guild(self.guild_id)
        #get Role ID
        self.role_id = role_id
        self.role = self.guild.get_role(self.role_id)
        

    #Utils
    def parse_coc_time(self, timestamp):
        if not timestamp or timestamp=='Error':
            return "Unknown Time"
        try:
            parse_time = datetime.strptime(timestamp, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)
            #2025-08-16 10:00:00+00:00
            return parse_time
        
        except ValueError:
            return "Invalid Time"
        
    def parse_start_time(self, parse_time):
        try:
            #Calculate the start time
            now = datetime.now(timezone.utc)
            unformatted_start_time = parse_time - now
            
            total_seconds = int(unformatted_start_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            start_time = f"*Starting in..* \n**Hours:** `{hours}` \n**Minutes:** `{minutes}`"
            
            return start_time
            
        except Exception as e:
            return f"Error: {e}"
        
    def parse_end_time(self, parse_end):
        try:
            now = datetime.now(timezone.utc)
            unformatted_start_time = parse_end - now
            
            total_seconds = int(unformatted_start_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            start_time = f"*Ending in..* \n**Hours:** `{hours}` \n**Minutes:** `{minutes}`"
            
            return start_time
            
        except Exception as e:
            return f"Error: {e}"

    """
    Bot Functions Below    

    """

    #Retrieves the Users info via playertag
    def _get_player_info(self, player_tag):
        self.encoded_tag = player_tag.replace("#", "%23")
        get_players_url = self.base_api_url + "/players/" + self.encoded_tag
        response_get_players = requests.get(get_players_url, headers=self.header)

        if response_get_players.status_code == 200:
            data = response_get_players.json()
            
            #Define the Player data
            #JsonLocalizedName means same text but different language
            #Fallback. Object = {}. Array = []
            name = data.get("name")
            tag = data.get("tag", 0)
            expLevel = data.get("expLevel", 0)
            trophies = data.get("trophies", 0)
            clan = data.get("clan", {}).get("name", "No Clan")
            attackWins = data.get("attackWins", 0)
            defenseWins = data.get("defenseWins")
            townHallLevel = data.get("townHallLevel", 0)

            #JsonLocalizedName
            heroes = data.get("heroes", [])
            heroes_display = []
            for hero in heroes:
                hero_name = hero.get("name", "No Heroes")
                hero_level = hero.get("level", "No Heroes")
                heroes_display.append(f"✪ **{hero_name:<15}** - Level **{hero_level}**")
    

            heroes_final_display = "\n".join(heroes_display)

            embed = discord.Embed(title=f"⚔️ **{name}**",
                                  description=f"🏷️ **{tag}**",  
                                  color=0xFFA500
                                  )
            
            # Add Clan avatar if available
            if 'clan' in data and data['clan'] and 'badgeUrls' in data['clan']:
                embed.set_thumbnail(url=data['clan']['badgeUrls']['medium'])
            
            #All on the left column 
            embed.add_field(
                name="🏠 **TownHall**",
                value=townHallLevel,
                inline=True
            )

            embed.add_field(
                name="🏆 **Trophies**",
                value=trophies,
                inline=False
            )

            embed.add_field(
                name="⭐ **Lvl Experience**",
                value=expLevel,
                inline=False
            )

            embed.add_field(
                name="🏰 **Clan**",
                value=clan,
                inline=False
            )
            
            embed.add_field(
                name="⚔️ **Attack Wins (this szn)**",
                value=attackWins,
                inline=False
            )

            embed.add_field(
                name="🛡️ **Defense Wins (this szn)**",
                value=defenseWins,
                inline=False
            )

            embed.add_field(
                name="🛡️ **Heroes**",
                value=heroes_final_display,
                inline=True
            )
            
            return embed

        else:
            return {
            "error": f"API Error {response_get_players.status_code}",
            "detail": response_get_players.text
        }

    #CLAN WAR INFO
    def _get_clans(self, clantag):
        self.encoded_tag = clantag.replace("#", "%23")
        self.get_clans_url = self.base_api_url + "/clans/" + f"{self.encoded_tag}" + "/currentwar"
        response_get_clans = requests.get(self.get_clans_url, headers=self.header)
        
        if response_get_clans.status_code== 200:
            data = response_get_clans.json()
            
            state = data.get("state", "Not in War")
            teamSize = data.get("teamSize", "Error")
            attacksPerMember = data.get("attacksPerMember", "Error")
            
            #Start / End times
            startTime = data.get("startTime", "Error")
            endTime = data.get("endTime", "Error")
            preparationStartTime = data.get("preparationStartTime")

            #Parse the time
            parse_start = self.parse_coc_time(startTime)
            parse_end = self.parse_coc_time(endTime)
            war_prep = self.parse_coc_time(preparationStartTime)
            
            #Calculate times
            war_start = self.parse_start_time(parse_start)
            war_end = self.parse_end_time(parse_end)
            
            #Utils
            current_state = None
            if state and state=='preparation' or 'inWar' or 'warEnded':
                if state=='preparation':
                    current_state = "🟡 **Preparation** :3"
                if state=='inWar':
                    current_state = "🟢 **In War** :3"
                if state=='warEnded':
                    current_state = "🔴 **War Ended** :3"
                    
            if current_state == None:
                current_state = "*Not in War*"


            embed = discord.Embed(title="**Clan Wars Status**",
                                  description=f"**Status:** {current_state}",
                                  color=0xFFA500 )

            embed.add_field(
                            name=f"🟢 **Start Time**",
                            value=war_start,
                            inline=True
                            )
            
            embed.add_field(
                            name=f"🔴 **End Time**",
                            value=war_end,
                            inline=True
                            )
            embed.add_field(
                            name=f"👥 **War Size**",
                            value=teamSize,
                            inline=False
                            )
            
            embed.add_field(
                            name=f"⚔️ **# of Attacks**",
                            value=attacksPerMember,
                            inline=False
                            )
            embed.set_footer(
                    text="add war percentages here"
            )
            
            return embed
        else:
            return {
            "error": f"API Error {response_get_clans.status_code}",
            "detail": response_get_clans.text
        }

    """
    On event Functions
    """
    #@ COC role when War starts
    def _mention_war_start(self):
        self.encoded_tag = self.clantag.replace("#", "%23")
        self.get_clans_url = self.base_api_url + "/clans/" + f"{self.encoded_tag}" + "/currentwar"
        response_get_clans = requests.get(self.get_clans_url, headers=self.header)


        if response_get_clans.status_code == 200:
            data = response_get_clans.json()

            #Start time
            startTime = data.get("startTime", "Error") #response -> 20250818T230913.000Z
            parse_start = self.parse_coc_time(startTime) #response -> 2025-08-16 10:00:00+00:00
            now = datetime.now(timezone.utc)
            seconds_until_start = (parse_start - now).total_seconds() #need to return timedelta object, not datetime. #timdelta represents a span of time (days, seconds, microseconds)
            if seconds_until_start >= 0:
                embed = discord.Embed(
                    title= "🚨⚔️ **WAR HAS STARTED!!**",
                    description=f"{self.role.mention} \n**War is live! Make sure to plan your attacks and secure those stars!**",
                    color=discord.Color.green()
                )
                return embed
        else:
            return {
                "error": f"API Error {response_get_clans.status_code}",
                "detail": response_get_clans.text
            }
        
    #@ COC role when War Ends
        """
        What do we want to do here?
        perhaps list:
        ULTRA MVP (12 stars)
        - Name: {stars}
        Valevictorian (6 stars)
        - Name: {stars}
        5 stars (happy emoji)
        - Name: {stars}
        4 stars (figure out emoji)
        - Name: {stars}
        etc.
        
        need to grabs stars but uh idk where it is
        """
    def _mention_war_end(self):
        self.encoded_tag = self.clantag.replace("#", "%23")
        self.get_clans_url = self.base_api_url + "/clans/" + f"{self.encoded_tag}" + "/currentwar"
        response_get_clans = requests.get(self.get_clans_url, headers=self.header)  

        if response_get_clans.status_code == 200:
            data = response_get_clans.json()
            startTime = data.get("startTime", 'Error')
            endTime = data.get("endTime", "Error")

            parse_end = self.parse_coc_time(endTime)
            parse_start = self.parse_coc_time(startTime)

            dt = (parse_end - parse_start).total_seconds()
            
            #Add Clan avatar 
            if 'clan' in data and data['clan'] and 'badgeUrls' in data['clan']:
                embed.set_thumbnail(url=data['clan']['badgeUrls']['medium'])
                
            #Grab total star per player
            clan = data.get('clan', [])
            members_war_stats = []
            for item in clan:
                members_name = item.get('members', {}).get('name')
                members_th_lvl = item.get('members', {}).get('townhallLevel') #ok wait, we need to download img of townhalls then map levels to TH image
                members_total_stars = item.get('members', {}.get('attacks')).get('stars')
                members_total_attacks = item.get('members', {}).get(len('attacks')) #count the elements
                
                if members_name and members_th_lvl and members_total_stars:
                    joined_member_stats = " ".join(members_th_lvl, members_name, members_total_stars, members_total_attacks)
                else:
                    pass #idk yet lol 

            #condition is true when war is over
            if dt <= 0:
                embed = discord.Embed(
                    title= "🚨⚔️ **WAR HAS ENDED!!**",
                    description=f"{self.role.mention} \n**War has ended! Great effort from everyone—don’t forget to collect your rewards and review the attacks. Let’s learn from this one and get ready for the next!**",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="**ULTRA MVP** *(12 stars)*",
                    value=,
                    inline=,
                )
                
                embed.add_field(
                    name="**Valedictorian** *(6 stars)*",
                    value=,
                    inline=,
                )
                
                embed.add_field(
                    name="**Honorable** *(5 stars)*",
                    value=,
                    inline=,
                )
                
                embed.add_field(
                    name="**Bums** *(3-4 stars)*",
                    value=,
                    inline=,
                )
                
                embed.add_field(
                    name="**WTF** *(1-2 stars)*",
                    value=,
                    inline=,
                )
            return embed
        else:
            return {
                "error": f"API Error {response_get_clans.status_code}",
                "detail": response_get_clans.text
            }
                
"""
GET Player info and Clan info
"""
        
#Retrieve player info via tag    
@bot.command()
async def ptag(ctx, tag):
    coc = ClashOfClans()
    result = coc._get_player_info(tag)
    if isinstance(result, dict) and "error" in result:
        await ctx.send(f"{result['error']}")
    else:
        await ctx.send(embed=result)

#Retrieve clan info via clan tag
@bot.command()
async def war(ctx, clantag):
    coc = ClashOfClans()
    result = coc._get_clans(clantag)
    if isinstance(result, dict) and "error" in result:
        await ctx.send(f"{result['error']}")
    else:
        await ctx.send(embed=result)

"""
War Start Utils 
"""

#Check every minute if war has started
@tasks.loop(minutes=1)
async def check_war_start():
    print("Checking if war started..")
    war_started = False
    coc = ClashOfClans()
    result = coc._mention_war_start()
    channel = coc.channel

    if isinstance(result, dict) and 'error' in result:
        print(f"Error: {result['error']}")
    elif result is not None and not war_started:
        await channel.send(embed=result)
        war_started = True

#@ Role when War starts
@bot.event
async def on_ready(): #start backgrounds loops with on_ready event
    check_war_start.start() #need .start(), a loop doesnt run until .start() is called


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
    