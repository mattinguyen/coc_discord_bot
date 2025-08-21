"""
Formatting _mention_war_end embeded
"""
#need to put "\u200E" to read from LEFT to RIGHT. bc we got people we diff names and sometimes read right to left
def formatting_member_stats(members_war_stats: list):
    twelve_stars = []
    six_stars = []
    five_stars = []
    three_four_stars = []
    one_two_stars = []

    double_accounts = [{"Justin": ["KingB", "kingblazen"],
                        "Eishan": ["yolohoboswag", "*_yummy_*"]
                        }]

    for members in members_war_stats:
        stars = int(members['members_total_stars'])
        
        # Format with code block for monospace alignment
        formatted_line = f"\u202D{members['townhall']} `{members['members_name']:<13} ⭐{stars}  {members['members_total_attacks']}/2`\u202C"

        for name, accounts in double_accounts:
            sum_stars = sum(int(stars))
            formatted_line_twelve_stars = f"\u202D{members['townhall']} `{name:<13} ⭐{sum_stars}  {members['members_total_attacks']}/2`\u202C"
            if stars == 6 and accounts:
                twelve_stars.append(formatted_line_twelve_stars)

            elif stars == 6 :
                six_stars.append(formatted_line)
            elif stars == 5:
                five_stars.append(formatted_line)
            elif stars == 3 or stars == 4:
                three_four_stars.append(formatted_line)
            elif stars <= 2:
                one_two_stars.append(formatted_line)

    finalized_twelve_stars = "\n".join(twelve_stars) if twelve_stars else "None"
    finalized_six_stars = "\n".join(six_stars) if six_stars else "None"
    finalized_five_stars = "\n".join(five_stars) if five_stars else "None"
    finalized_three_four_stars = "\n".join(three_four_stars) if three_four_stars else "None"
    finalized_one_two_stars = "\n".join(one_two_stars) if one_two_stars else "None"
    
    return finalized_twelve_stars, finalized_six_stars, finalized_five_stars, finalized_three_four_stars, finalized_one_two_stars