import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, time
from utils import formatting_member_stats
from utils_ai import gemini_war_start_message, gemini_war_end_message

#Load the Tokens/Keys
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COC_API =os.getenv("COC_API")
COC_TOKEN= os.getenv("COC_TOKEN")
channel_id= int(os.getenv("channel_id")) #Chat channel ID
guild_id= int(os.getenv("guild_id")) #Server ID
role_id= int(os.getenv("role_id")) #Role ID

#Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    filename='discord.log',
    filemode='a',
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s -  %(message)s"  
)

#Set up intents
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

#Global variables
bot = commands.Bot(command_prefix='!', intents=intents)
coc = None
war_started = False
war_ended = False

class ClashOfClans:
    def __init__(self, bot):
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

        #Set Channel ID, server ID, Role ID
        self.bot = bot
        self.guild = None
        self.channel = None
        self.role = None
        
        #Townhall Discord Emoji Mapping
        self.th_emoji = {
            17: "<:th17:1429257394960994445>",
            16: "<:th16:1407470511273017454>",
            15: "<:th15:1407470509267877979>",
            14: "<:th14:1407470507913379871>",
            13: "<:th13:1407149752625266688>",
            12: "<:th12:1407149758543433869>",
            11: "<:th12:1407149758543433869>",
            10: "<:th11:1407149756844871711>",
            9: "<:th9:1407149761026592900>"
        }

    #Allow bot to connect first
    async def setup(self):
        await bot.wait_until_ready()
        self.guild = bot.get_guild(guild_id)
        self.channel = bot.get_channel(channel_id)
        self.role = self.guild.get_role(role_id)

    """
    Utils Below
    """
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
    
    #Takes the THLVL and returns the formatted emoji ID
    def map_townhall_emojis(self, townhalllvl):
        try:
            return self.th_emoji.get(townhalllvl, "None")
        except Exception as e:
            print(f"Error {e}")
            return("None (except error)")
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
    def _get_war_status(self):
        self.encoded_tag = self.clantag.replace("#", "%23")
        self.get_clans_url = self.base_api_url + "/clans/" + f"{self.encoded_tag}" + "/currentwar"
        response_get_clans = requests.get(self.get_clans_url, headers=self.header)  

        if response_get_clans.status_code == 200:
            data = response_get_clans.json()

            clan = data.get('clan', {}).get('members', [])
            
            #If war hasnt started and theres no stats available
            war_state = data.get('state', "Error")
            startTime = data.get("startTime", "Error")
            parse_start = self.parse_coc_time(startTime)
            finalized_start_time = self.parse_start_time(parse_start)
            
            members_war_stats = []
            for members in clan:
                members_name = members.get('name')
                members_th_lvl = members.get('townhallLevel') #ok wait, we need to download img of townhalls then map levels to TH image
                member_attack = members.get('attacks', [])
                members_total_stars = sum(attack.get('stars', 0) for attack in member_attack)
                members_attacks = len(member_attack)
                
                
                if members_name and members_th_lvl is not None: #include 0 stars
                    #**<:Townhall13:EMOJI_ID_HERE>**
                    th_emoji = self.map_townhall_emojis(members_th_lvl)
                    formatted_members_stats = f"**{th_emoji} - {members_name} - {members_total_stars} - {members_attacks}**"
                    members_war_stats.append({
                        "townhall_level": f"{members_th_lvl}",
                        "townhall": f"{th_emoji}",
                        "members_name": f"{members_name}",
                        "members_total_stars": f"{members_total_stars}",
                        "members_total_attacks": f"{members_attacks}"
                    })
                else:
                    logging.error("Error appending member_war_stats!") 
               
            finalized_twelve_stars, finalized_six_stars, finalized_five_stars, finalized_three_four_stars, finalized_one_two_stars = formatting_member_stats(members_war_stats)
            
            if war_state == 'preparation':
                embed = discord.Embed(
                    title="🚨⚔️ **WAR STATUS**",
                    description="**PREP DAY, WE LOCKED IN! Scope out them ops, call dibs on who you finna smoke, and make sure the homies got troops. We bout to run they whole block tomorrow!**",
                    color=discord.Color.green()
                )
                #Add Clan avatar 
                if 'clan' in data and data['clan'] and 'badgeUrls' in data['clan']:
                        embed.set_thumbnail(url=data['clan']['badgeUrls']['medium'])
                
                embed.add_field(
                    name="🟡 **Preparation** :3",
                    value=finalized_start_time,
                    inline=True
                )
                
                return embed
                    
            elif members_war_stats and not war_state == 'preparation':
                embed = discord.Embed(
                        title= "🚨⚔️ **WAR STATUS**",
                        description=f"{self.role.mention} \n**WAR IS ON! Time to dominate! Plan your attacks, execute flawlessly, and show them why we're the best clan out there!**",
                        color=discord.Color.green()
                    )
                
                    #Add Clan avatar 
                if 'clan' in data and data['clan'] and 'badgeUrls' in data['clan']:
                        embed.set_thumbnail(url=data['clan']['badgeUrls']['medium'])
                
                embed.add_field(
                    name="**ULTRA MVP** *(12 stars)*",
                    value=finalized_twelve_stars, #map this last
                    inline=False,
                )
                
                embed.add_field(
                    name="**Valedictorian** *(6 stars)*",
                    value=finalized_six_stars,
                    inline=True,
                )
                    
                embed.add_field(
                    name="**Honorable** *(5 stars)*",
                    value=finalized_five_stars,
                    inline=True,
                )

                # Add invisible spacer to force new row
                embed.add_field(
                    name="",  # Invisible character
                    value="", # Invisible character  
                    inline=False,
                )
                
                embed.add_field(
                    name="**Bums** *(3-4 stars)*",
                    value=finalized_three_four_stars,
                    inline=False,
                )
                
                embed.add_field(
                    name="**WTF** *(0-2 stars)*",
                    value=finalized_one_two_stars,
                    inline=False,
                )
                   
                return embed
            else:
                return {"error": "error"}   

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
            if isinstance(parse_start, datetime):
                now = datetime.now(timezone.utc)
                seconds_until_start = (parse_start - now).total_seconds() #need to return timedelta object, not datetime. #timdelta represents a span of time (days, seconds, microseconds)
                if seconds_until_start >= 0:
                    embed = discord.Embed(
                        title= "🚨⚔️ **WAR HAS STARTED!!**",
                        description=f"{self.role.mention} \n**{gemini_war_start_message()}**",
                        color=discord.Color.green()
                    )
                    return embed
                else:
                    return None #War no start yet
            else:
                return {
                    "error": f"Failed to parse time",
                    "detail": f"Parse result: {parse_start}"
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

            if isinstance(parse_end, datetime) and isinstance(parse_start, datetime):
                
                #Grab total star per player
                clan = data.get('clan', {}).get('members', [])
                members_war_stats = []
                for members in clan:
                    members_name = members.get('name')
                    members_th_lvl = members.get('townhallLevel') #ok wait, we need to download img of townhalls then map levels to TH image
                    member_attack = members.get('attacks', [])
                    members_total_stars = sum(attack.get('stars', 0) for attack in member_attack)
                    members_total_attacks = len(member_attack)
                    war_result = members.get('state')
                
                    if members_name and members_th_lvl is not None: #include 0 stars
                        #**<:Townhall13:EMOJI_ID_HERE>**
                        th_emoji = self.map_townhall_emojis(members_th_lvl)
                        formatted_members_stats = f"**{th_emoji} - {members_name} - {members_total_stars} - {members_total_attacks}**"
                        members_war_stats.append({
                            "townhall": f"{th_emoji}",
                            "members_name": f"{members_name}",
                            "members_total_stars": f"{members_total_stars}",
                            "members_total_attacks": f"{members_total_attacks}"
                        })
                    else:
                        logging.error("Error appending member_war_stats!") 
               
                fianlized_twelve_stars, finalized_six_stars, finalized_five_stars, finalized_three_four_stars, finalized_one_two_stars = formatting_member_stats(members_war_stats)
                
                current_time = datetime.now(timezone.utc)
                time_remaining = (parse_end - current_time).total_seconds()
                    
                #condition is true when war is over
                #either this or if war_state == 'warEnded'
                if time_remaining <= 0:
                    embed = discord.Embed(
                        title= "🚨⚔️ **WAR HAS ENDED!!**",
                        description=f"{self.role.mention} \n**{gemini_war_end_message(war_result)}**",
                        color=discord.Color.green()
                    )
                
                    #Add Clan avatar 
                    if 'clan' in data and data['clan'] and 'badgeUrls' in data['clan']:
                        embed.set_thumbnail(url=data['clan']['badgeUrls']['medium'])
                
                    embed.add_field(
                        name="**ULTRA MVP** *(12 stars)*",
                        value="placeholder", #map this last
                        inline=False,
                    )
                
                    embed.add_field(
                        name="**Valedictorian** *(6 stars)*",
                        value=finalized_six_stars,
                        inline=False,
                    )
                    
                    embed.add_field(
                        name="**Honorable** *(5 stars)*",
                        value=finalized_five_stars,
                        inline=True,
                    )
                
                    embed.add_field(
                        name="**Bums** *(3-4 stars)*",
                        value=finalized_three_four_stars,
                        inline=True,
                    )
                
                    embed.add_field(
                        name="**WTF** *(0-2 stars)*",
                        value=finalized_one_two_stars,
                        inline=True,
                    )
                   
                    return embed
            else:
                return None    
                
"""
GET Player info and Clan info
"""
        
#Retrieve player info via tag    
@bot.command()
async def ptag(ctx, tag):
    global coc
    result = coc._get_player_info(tag)
    if isinstance(result, dict) and "error" in result:
        await ctx.send(f"{result['error']}")
    else:
        await ctx.send(embed=result)

#Retrieve clan info via clan tag
@bot.command()
async def war(ctx, clantag):
    global coc
    result = coc._get_clans(clantag)
    if isinstance(result, dict) and "error" in result:
        await ctx.send(f"{result['error']}")
    else:
        await ctx.send(embed=result)

#Retrieve War Status & Stats
@bot.command()
async def wstatus(ctx):
    result = coc._get_war_status()
    if isinstance(result, dict) and "error" in result:
        await ctx.send(f"{result['error']}")
    else:
        await ctx.send(embed=result)
"""
War Background Utils 
"""

#Check every minute if war has started
@tasks.loop(minutes=1)
async def check_war_start():
    logging.debug("Checking if war STARTED")
    global war_started, coc
    result = coc._mention_war_start()
    channel = coc.channel

    if isinstance(result, dict) and 'error' in result:
        print(f"Error: {result['error']}")
    elif result is not None and not war_started:
        await channel.send(embed=result)
        war_started = True
    elif result is None and war_started:
        war_started = False
    
@tasks.loop(minutes=1)
async def check_war_end():
    logging.debug("Checking if war ENDED")
    global coc, war_ended
    result = coc._mention_war_end()
    channel = coc.channel
    
    if isinstance(result, dict) and 'error' in result:
        logger.error("Houston we have a problem..")
    elif result is not None and not war_ended: #When war ends
        await channel.send(embed=result)
        war_ended = True
    elif result is None and war_ended: #Reset the logic when war ends
        war_ended = False
    
@bot.command()
async def test_war_end(ctx, clantag):
    global coc
    result = coc._mention_war_end(clantag)
    if isinstance(result, dict) and "error" in result:
        await ctx.send(f"{result['error']}")
    else:
        await ctx.send(embed=result)


if __name__ == '__main__':
    coc = ClashOfClans(bot)
    
    @bot.event
    async def on_ready():
        await coc.setup()
        logging.info("Clash of Clans setup Finished!")
        check_war_start.start() #need .start(), a loop doesnt run until .start() is called
        check_war_end.start()
    
    bot.run(DISCORD_TOKEN)
    