"""
Formatting _mention_war_end embeded
"""
#need to put "\u200E" to read from LEFT to RIGHT. bc we got people we diff names and sometimes read right to left
def formatting_member_stats(members_war_stats: list):
    twelve_stars = {"Justin":[],
                     "Eishan":[]
                     }
    six_stars = []
    six_stars_townhall = []
    five_stars = []
    three_four_stars = []
    one_two_stars = []
    
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
    
    return finalized_twelve_stars, finalized_six_stars, finalized_five_stars, finalized_three_four_stars, finalized_one_two_stars