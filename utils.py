"""
Formatting _mention_war_end embeded
"""
#need to put "\u200E" to read from LEFT to RIGHT. bc we got people we diff names and sometimes read right to left
def formatting_member_stats(members_war_stats: list):
    six_stars = []
    five_stars = []
    three_four_stars = []
    one_two_stars = []
    for members in members_war_stats:
        if int(members['members_total_stars']) == 6:
            six_stars.append(f"**{members['townhall']} {members['members_name']:<1} \u200E⭐ {members['members_total_stars']}** | {members['members_total_attacks']}/2")
            
        elif int(members['members_total_stars']) == 5:
            five_stars.append(f"**{members['townhall']} {members['members_name']:<1} \u200E⭐ {members['members_total_stars']}** | {members['members_total_attacks']}/2")
            
        elif int(members['members_total_stars']) == 3 or 4:
            three_four_stars.append(f"**{members['townhall']} {members['members_name']:<1} \u200E⭐ {members['members_total_stars']}** | {members['members_total_attacks']}/2")
            
        elif int(members['members_total_stars']) <= 2:
            one_two_stars.append(f"**{members['townhall']} {members['members_name']:<1} \u200E⭐ {members['members_total_stars']}** | {members['members_total_attacks']}/2")
            
    
    finalized_six_stars = "\n".join(six_stars) if six_stars else ""
    finalized_five_stars = "\n".join(five_stars) if five_stars else ""
    finalized_three_four_stars = "\n".join(three_four_stars) if three_four_stars else ""
    finalized_one_two_stars = "\n".join(one_two_stars) if one_two_stars else ""
    
    return finalized_six_stars, finalized_five_stars, finalized_three_four_stars, finalized_one_two_stars