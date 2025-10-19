"""
Formatting _mention_war_end embeded
"""
#need to put "\u200E" to read from LEFT to RIGHT. bc we got people we diff names and sometimes read right to left
def formatting_member_stats(members_war_stats: list):
<<<<<<< HEAD
    twelve_stars = {"Justin":[],
                     "Eishan":[]
                     }
=======
    """
    members_war_stats = [{
                        "townhall_level": f"{members_th_lvl}",
                        "townhall": f"{th_emoji}",
                        "members_name": f"{members_name}",
                        "members_total_stars": f"{members_total_stars}",
                        "members_total_attacks": f"{members_total_attacks}"
                        }]
    """
    #check the highest TH level for 12 star accounts appending
    def check_highest_th_lvl(account_names: list, all_members: list):
        matching_accounts = [member for member in all_members if member['members_name'] in account_names]

        if not matching_accounts:
            return None
        
        def get_th_level(member):
            if isinstance(member.get('townhall_level'), int):
                return member['townhall_level']
            
        return max(matching_accounts, key=get_th_level)
    
    #this at the end. basically take all the stars list and combine them so u can display on discord
    def final_combine_list(stars):
        return "\n".join(stars) if stars else "None"
        

    twelve_stars = []
>>>>>>> b912c9b (Finished utils logic and added ai function)
    six_stars = []
    six_stars_townhall = []
    five_stars = []
    three_four_stars = []
    one_two_stars = []
    
<<<<<<< HEAD
    double_accounts = {"Justin":["KingB", "kingblazen"],
                       "Eishan": ['yolohoboswag', '*_yummy_*']
                       }
    
    #looks so nasty, make variables to make cleans cleaner.
    #work in a mess, produce a mess XD
    
    for members in members_war_stats:
        #looks so nasty, make variables to make cleans cleaner.
        #work in a mess, produce a mess XD
    
        townhall = members['townhall'] 
        members_name = members['members_name']
        total_stars = members['members_total_stars']
        total_attacks = members['members_total_attacks']
        
        if int(total_stars) == 6:
            six_stars.append(members_name)
            six_stars_townhall = 
            
            for person, account_name in double_accounts.items():
                if account_name in six_stars and account_name in double_accounts:
                    if account_name == "KingB" and 'kingblazen':
                        twelve_stars['Justin'].append({'townhall': townhall, "account_name": account_name}) #append the townhall and username of justin and eishan
                    if account_name == 'yolohoboswag' and '*_yummy_*':
                        twelve_stars['Eishan'].append({'townhall': townhall, "account_name": account_name})
                    
                elif account_name not in twelve_stars:
                    six_stars.append(f"\u202D{townhall} `{members_name:<12} \u200E⭐{total_stars} | {total_attacks}/2`\u202D")
            
                                   
                 
        elif int(total_stars) == 5:
            five_stars.append(f"\u202D{townhall} `{members_name:<12} \u200E⭐{total_stars} | {total_attacks}/2`\u202D")
            
        elif int(total_stars) == 3 or 4:
            three_four_stars.append(f"\u202D{townhall} `{members_name:<12} \u200E⭐{total_stars} | {total_attacks}/2`\u202D")
          
        elif int(total_stars) <= 2:
            one_two_stars.append(f"\u202D{townhall} `{members_name:<12} \u200E⭐{total_stars} | {total_attacks}/2`\u202D")
        
    finalized_twelve_stars = "\n".join(twelve_stars) if twelve_stars else "`None! :(`"
    finalized_six_stars = "\n".join(six_stars) if six_stars else "`None! :3`"
    finalized_five_stars = "\n".join(five_stars) if five_stars else "`None! :3`"
    finalized_three_four_stars = "\n".join(three_four_stars) if three_four_stars else "`None! :3`"
    finalized_one_two_stars = "\n".join(one_two_stars) if one_two_stars else "`None! :3`"
=======
    double_accounts = {"Justin": ["KingB", "kingblazen"],
                        "Eishan": ["yolohoboswag", "*_yummy_*"]
                        }
    processed_accounts = set()

    for person, accounts in double_accounts.items():
        #Find all members matching account names
        friends = [member for member in members_war_stats if member['members_name'] in accounts]

        #Calculate total stars
        total_stars = sum(int(member['members_total_stars']) for member in friends)

        if total_stars == 12 and len(friends) == 2:
            #find highest TH
            highest_th_lvl = check_highest_th_lvl(accounts, members_war_stats)

            if highest_th_lvl:
                formatted_line = f"\u202D{highest_th_lvl['townhall']} `{person:<13} ⭐12  4/4`\u202C"
                twelve_stars.append(formatted_line)

                #Mark them as processed
                for member in friends:
                    processed_accounts.add(member['members_name'])


    for members in members_war_stats:
        #Skip if they got 12 stars
        if members['members_name'] in processed_accounts:
            continue

        stars = int(members['members_total_stars'])
        
        formatted_line = f"\u202D{members['townhall']} `{members['members_name']:<13} ⭐{stars}  {members['members_total_attacks']}/2`\u202C"
        if stars == 6:
            six_stars.append(formatted_line)
        elif stars == 5:
            five_stars.append(formatted_line)
        elif stars == 3 or stars == 4:
            three_four_stars.append(formatted_line)
        elif stars <= 2:
            one_two_stars.append(formatted_line)

>>>>>>> b912c9b (Finished utils logic and added ai function)
    
    finalized_twelve_stars = final_combine_list(twelve_stars) 
    finalized_six_stars = final_combine_list(six_stars) 
    finalized_five_stars = final_combine_list(five_stars) 
    finalized_three_four_stars = final_combine_list(three_four_stars) 
    finalized_one_two_stars = final_combine_list(one_two_stars) 
    
    return finalized_twelve_stars, finalized_six_stars, finalized_five_stars, finalized_three_four_stars, finalized_one_two_stars


#Gemini Prompt Utils
from google import genai
from google.genai import types

def gemini_generate():
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a cat. Your name is Neko."),
        contents="Hello there"
    )

    print(response.text)


