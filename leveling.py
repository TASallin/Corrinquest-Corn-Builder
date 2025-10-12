import pandas as pd
import math
from corrin import Corrin, Item

CLASSES_DF = pd.read_csv("data/Classes.csv")
BOON_BANE_DF = pd.read_csv("data/Boon Bane.csv")
CHAPTER_DF = pd.read_csv("data/Chapter Levels.csv")
PROMOTIONS_DF = pd.read_csv("data/Promotion Bonuses.csv")
SKILLS_DF = pd.read_csv("data/Skills.csv")
ITEMS_DF = pd.read_csv("data/Items.csv")
CORRIN_GROWTHS = [45, 45, 30, 40, 45, 45, 35, 25]
CORRIN_BASES = [2, 0, 1, 3, 1, 3, 1, 0]
WEAPON_TYPES = ["Sword", "Lance", "Axe", "Dagger", "Bow", "Tome", "Staff", "Stone"]
HOSHIDAN_WEAPONS = ["Katana", "Naginata", "Club", "Shuriken", "Yumi"]
STANDARD_METALS = ["Bronze", "Iron", "Steel", "Silver"]
STANDARD_TOMES = ["Fire", "Thunder", "Fimbulvetr", "Ragnarok"]
STANDARD_SPIRITS = ["Rat Spirit", "Ox Spirit", "Tiger Spirit", "Rabbit Spirit"]
CLASSES_DF["Weapon1"] = CLASSES_DF["Weapon1"].fillna('').astype(str)
CLASSES_DF["Weapon2"] = CLASSES_DF["Weapon2"].fillna('').astype(str)
CLASSES_DF["Weapon3"] = CLASSES_DF["Weapon3"].fillna('').astype(str)
SILVER_THRESHOLD = 25
SILVER_PROMO_THRESHOLD = 27
RUNE_THRESHOLD = 15
STAFF_THRESHOLD = 12
STAFF_PROMO_THRESHOLD = 21
C_RANK_REQUIREMENT = 51

def level_corrin(chapter, corrin):
    level = int(CHAPTER_DF.loc[CHAPTER_DF["Chapter"] == chapter, "Level"].iloc[0])
    level_corrin_stats(level, corrin)
    level_corrin_skills(level, corrin)
    set_weapon_ranks(chapter, corrin)
    assign_items(chapter, corrin)

def level_corrin_stats(level, corrin):
    current_class = corrin.base_class_name
    class_row = CLASSES_DF.loc[CLASSES_DF["Name"] == current_class]
    current_stats = get_base_stats(class_row, corrin)
    growths = get_growths(class_row, corrin)
    caps = get_caps(class_row, corrin)
    max_unpromoted_level = min(level, 20)
    current_level = 1
    while current_level < max_unpromoted_level:
        current_stats = fixed_growths_level(current_stats, growths, caps)
        current_level += 1
    if level > 20:
        current_stats = promote_corrin(corrin, current_stats)
        current_class = corrin.promoted_class_name
        class_row = CLASSES_DF.loc[CLASSES_DF["Name"] == current_class]
        growths = get_growths(class_row, corrin)
        caps = get_caps(class_row, corrin)
        current_level = 1
        max_promoted_level = level-20
        while current_level < max_promoted_level:
            current_stats = fixed_growths_level(current_stats, growths, caps)
            current_level += 1
        corrin.current_class_id = corrin.promoted_class_id
        corrin.level = level - 20
        corrin.internal_level = 20
    else:
        corrin.current_class_id = corrin.base_class_id
        corrin.level = level
        corrin.internal_level = 0
    for i in range(len(current_stats)):
        current_stats[i] = math.floor(current_stats[i] + 0.5)
    corrin.current_class_name = current_class
    corrin.stats = current_stats
    base_stats = get_base_stats(class_row, corrin)
    corrin.growth_stats = [0] * len(current_stats)
    for i in range(len(current_stats)):
        corrin.growth_stats[i] = corrin.stats[i] - base_stats[i]

def get_base_stats(df_row, corrin):
    base_stats = [int(df_row["HPBase"].iloc[0]), int(df_row["StrengthBase"].iloc[0]), int(df_row["MagicBase"].iloc[0]), int(df_row["SkillBase"].iloc[0]),
            int(df_row["SpeedBase"].iloc[0]), int(df_row["LuckBase"].iloc[0]), int(df_row["DefenseBase"].iloc[0]), int(df_row["ResistanceBase"].iloc[0])]
    boon_row = get_boon_row(corrin)
    boon_stats = [int(boon_row["HPBase"].iloc[0]), int(boon_row["StrengthBase"].iloc[0]), int(boon_row["MagicBase"].iloc[0]), int(boon_row["SkillBase"].iloc[0]),
            int(boon_row["SpeedBase"].iloc[0]), int(boon_row["LuckBase"].iloc[0]), int(boon_row["DefenseBase"].iloc[0]), int(boon_row["ResistanceBase"].iloc[0])]
    bane_row = get_bane_row(corrin)
    bane_stats = [int(bane_row["HPBase"].iloc[0]), int(bane_row["StrengthBase"].iloc[0]), int(bane_row["MagicBase"].iloc[0]), int(bane_row["SkillBase"].iloc[0]),
            int(bane_row["SpeedBase"].iloc[0]), int(bane_row["LuckBase"].iloc[0]), int(bane_row["DefenseBase"].iloc[0]), int(bane_row["ResistanceBase"].iloc[0])]
    final_stats = []
    for i in range(len(base_stats)):
        final_stats.append(base_stats[i] + boon_stats[i] + bane_stats[i] + CORRIN_BASES[i])
    return final_stats

def get_growths(df_row, corrin):
    class_growths = [int(df_row["HPGrowth"].iloc[0]), int(df_row["StrengthGrowth"].iloc[0]), int(df_row["MagicGrowth"].iloc[0]), int(df_row["SkillGrowth"].iloc[0]),
            int(df_row["SpeedGrowth"].iloc[0]), int(df_row["LuckGrowth"].iloc[0]), int(df_row["DefenseGrowth"].iloc[0]), int(df_row["ResistanceGrowth"].iloc[0])]
    boon_row = get_boon_row(corrin)
    boon_growths = [int(boon_row["HPGrowth"].iloc[0]), int(boon_row["StrengthGrowth"].iloc[0]), int(boon_row["MagicGrowth"].iloc[0]), int(boon_row["SkillGrowth"].iloc[0]),
            int(boon_row["SpeedGrowth"].iloc[0]), int(boon_row["LuckGrowth"].iloc[0]), int(boon_row["DefenseGrowth"].iloc[0]), int(boon_row["ResistanceGrowth"].iloc[0])]
    bane_row = get_bane_row(corrin)
    bane_growths = [int(bane_row["HPGrowth"].iloc[0]), int(bane_row["StrengthGrowth"].iloc[0]), int(bane_row["MagicGrowth"].iloc[0]), int(bane_row["SkillGrowth"].iloc[0]),
            int(bane_row["SpeedGrowth"].iloc[0]), int(bane_row["LuckGrowth"].iloc[0]), int(bane_row["DefenseGrowth"].iloc[0]), int(bane_row["ResistanceGrowth"].iloc[0])]
    final_growths = []
    for i in range(len(class_growths)):
        final_growths.append(class_growths[i] + boon_growths[i] + bane_growths[i] + CORRIN_GROWTHS[i])
    return final_growths

def get_caps(df_row, corrin):
    class_caps = [int(df_row["HPCap"].iloc[0]), int(df_row["StrengthCap"].iloc[0]), int(df_row["MagicCap"].iloc[0]), int(df_row["SkillCap"].iloc[0]),
            int(df_row["SpeedCap"].iloc[0]), int(df_row["LuckCap"].iloc[0]), int(df_row["DefenseCap"].iloc[0]), int(df_row["ResistanceCap"].iloc[0])]
    boon_row = get_boon_row(corrin)
    boon_caps = [int(boon_row["HPCap"].iloc[0]), int(boon_row["StrengthCap"].iloc[0]), int(boon_row["MagicCap"].iloc[0]), int(boon_row["SkillCap"].iloc[0]),
            int(boon_row["SpeedCap"].iloc[0]), int(boon_row["LuckCap"].iloc[0]), int(boon_row["DefenseCap"].iloc[0]), int(boon_row["ResistanceCap"].iloc[0])]
    bane_row = get_bane_row(corrin)
    bane_caps = [int(bane_row["HPCap"].iloc[0]), int(bane_row["StrengthCap"].iloc[0]), int(bane_row["MagicCap"].iloc[0]), int(bane_row["SkillCap"].iloc[0]),
            int(bane_row["SpeedCap"].iloc[0]), int(bane_row["LuckCap"].iloc[0]), int(bane_row["DefenseCap"].iloc[0]), int(bane_row["ResistanceCap"].iloc[0])]
    final_caps = []
    for i in range(len(class_caps)):
        final_caps.append(class_caps[i] + boon_caps[i] + bane_caps[i])
    return final_caps

def get_boon_row(corrin):
    boon = '+' + corrin.boon_name
    return BOON_BANE_DF.loc[BOON_BANE_DF["Name"] == boon]

def get_bane_row(corrin):
    bane = '-' + corrin.bane_name
    return BOON_BANE_DF.loc[BOON_BANE_DF["Name"] == bane]

def fixed_growths_level(stats, growths, caps):
    for i in range(len(stats)):
        stats[i] = min(stats[i] + growths[i] / 100, caps[i])
    return stats

def promote_corrin(corrin, stats):
    promotion_row = PROMOTIONS_DF.loc[PROMOTIONS_DF["Base Class"] == corrin.base_class_name]
    promotion_row = promotion_row.loc[promotion_row["Promoted Class"] == corrin.promoted_class_name]
    promotion_bonuses = [int(promotion_row["HP"].iloc[0]), int(promotion_row["Str"].iloc[0]), int(promotion_row["Mag"].iloc[0]), int(promotion_row["Skl"].iloc[0]),
            int(promotion_row["Spd"].iloc[0]), int(promotion_row["Lck"].iloc[0]), int(promotion_row["Def"].iloc[0]), int(promotion_row["Res"].iloc[0])]
    for i in range(len(stats)):
        stats[i] = stats[i] + promotion_bonuses[i]
    return stats

def get_skill_ID(skill_name):
    return int(SKILLS_DF.loc[SKILLS_DF["Skill"] == skill_name, "ID"].iloc[0])

def level_corrin_skills(level, corrin):
    corrin.equipped_skills = []
    corrin.learned_skills = [False] * 160
    corrin.learned_skills[0] = True
    if corrin.personal_skill_1_id:
        corrin.equipped_skills.append(corrin.personal_skill_1_id)
    else:
        corrin.equipped_skills.append(0)
    if corrin.personal_skill_2_id:
        corrin.equipped_skills.append(corrin.personal_skill_2_id)
    else:
        corrin.equipped_skills.append(0)
    base_class_row = CLASSES_DF.loc[CLASSES_DF["Name"] == corrin.base_class_name]
    promoted_class_row = CLASSES_DF.loc[CLASSES_DF["Name"] == corrin.promoted_class_name]
    if get_skill_ID(str(base_class_row["Skill1"].iloc[0])) not in corrin.equipped_skills:
        corrin.equipped_skills.append(get_skill_ID(str(base_class_row["Skill1"].iloc[0])))
    if level >= 10:
        if get_skill_ID(str(base_class_row["Skill2"].iloc[0])) not in corrin.equipped_skills:
            corrin.equipped_skills.append(get_skill_ID(str(base_class_row["Skill2"].iloc[0])))
    if level >= 25:
        if get_skill_ID(str(promoted_class_row["Skill1"].iloc[0])) not in corrin.equipped_skills:
            corrin.equipped_skills.append(get_skill_ID(str(promoted_class_row["Skill1"].iloc[0])))
    for skill_id in corrin.equipped_skills:
        corrin.learned_skills[skill_id] = True
    if level >= 35:
        corrin.learned_skills[get_skill_ID(str(promoted_class_row["Skill2"].iloc[0]))] = True
        if len(corrin.equipped_skills) < 5 and get_skill_ID(str(promoted_class_row["Skill2"].iloc[0])) not in corrin.equipped_skills:
            corrin.equipped_skills.append(get_skill_ID(str(promoted_class_row["Skill2"].iloc[0])))

def set_weapon_ranks(chapter, corrin):
    corrin.weapon_ranks = [0, 0, 0, 0, 0, 0, 0, 0]
    chapter_row = CHAPTER_DF.loc[CHAPTER_DF["Chapter"] == chapter]
    level = int(chapter_row["Level"].iloc[0])
    base_class = corrin.base_class_name
    promoted_class = corrin.promoted_class_name
    if level >= 20:
        current_class = promoted_class
    else:
        current_class = base_class
    weapons = get_class_weapons(current_class)
    for weapon_type in weapons:
        weapon_index = WEAPON_TYPES.index(weapon_type)
        wxp_column = get_wxp_column(corrin, base_class, promoted_class, current_class, weapon_type)
        corrin.weapon_ranks[weapon_index] = int(chapter_row[wxp_column].iloc[0])

def get_wxp_column(corrin, base_class, promoted_class, current_class, weapon_type):
    wxp_column = "Main WXP"
    base_weapons = get_class_weapons(base_class)
    promoted_weapons = get_class_weapons(promoted_class)
    if current_class == "Butler/Maid" and weapon_type == "Lance":
        wxp_column = "Maid WXP"
    elif base_class == "Villager" and weapon_type == "Lance":
        wxp_column = "Villager WXP"
    elif promoted_class == current_class and len(promoted_weapons) == 1:
        wxp_column = "S Rank WXP"
    elif promoted_class == current_class and weapon_type not in base_weapons:
        wxp_column = "Promoted WXP"
    elif len(base_weapons) == 2:
        other_weapon = base_weapons[1 - base_weapons.index(weapon_type)]
        if other_weapon in promoted_weapons and weapon_type not in promoted_weapons:
            wxp_column = "Secondary WXP"
        elif other_weapon not in promoted_weapons and weapon_type in promoted_weapons:
            wxp_column = "Main WXP"
        elif "Stone" in base_weapons:
            if weapon_type == "Stone":
                wxp_column = "Secondary WXP"
            else:
                wxp_column = "Main WXP"
            #if corrin.boon_name == "Mag" or corrin.bane_name == "Str":
            #    if weapon_type == "Stone":
            #        wxp_column = "Main WXP"
            #    else:
            #        wxp_column = "Secondary WXP"
            #else:
            #    if weapon_type == "Stone":
            #        wxp_column = "Secondary WXP"
            #    else:
            #        wxp_column = "Main WXP"
        elif weapon_type == "Lance":
            wxp_column = "Main WXP"
        else:
            wxp_column = "Secondary WXP"
    return wxp_column


def get_class_weapons(current_class):
    class_row = CLASSES_DF.loc[CLASSES_DF["Name"] == current_class]
    weapons = []
    for i in range(1, 4):
        weapon_type = str(class_row["Weapon" + str(i)].iloc[0])
        if not weapon_type or len(weapon_type) < 1:
            continue
        weapons.append(weapon_type)
    return weapons

def assign_items(chapter, corrin):
    corrin.items = []
    base_class = corrin.base_class_name
    promoted_class = corrin.promoted_class_name
    for i in range(len(corrin.weapon_ranks)):
        if corrin.weapon_ranks[i] > 0 and chapter == 7 and get_wxp_column(corrin, base_class, promoted_class, base_class, WEAPON_TYPES[i]) == "Secondary WXP" and WEAPON_TYPES[i] not in ["Staff", "Stone"]:
            continue
        weapons = get_items_for_weapon_type(i, corrin.weapon_ranks[i], chapter, corrin)
        for weapon in weapons:
            corrin.items.append(weapon)
    if chapter == 7: # Give Bronze
        base_weapons = get_class_weapons(base_class)
        if len(base_weapons) == 1:
            if base_weapons[0] in ["Staff", "Stone"]:
                pass
            else:
                bronze = get_item_from_name(construct_weapon_name("Bronze", base_weapons[0], base_class))
                corrin.items.append(bronze)
        else:
            for weapon_type in base_weapons:
                if get_wxp_column(corrin, base_class, promoted_class, base_class, weapon_type) == "Secondary WXP":
                    if weapon_type in ["Staff", "Stone"]:
                        pass
                    else:
                        bronze = get_item_from_name(construct_weapon_name("Bronze", weapon_type, base_class))
                        corrin.items.append(bronze)
                    break
    corrin.items.append(get_item_from_name("Vulnerary"))
    level = int(CHAPTER_DF.loc[CHAPTER_DF["Chapter"] == chapter, "Level"].iloc[0])
    if level == 20:
        corrin.items.append(get_item_from_name("Master Seal"))

def get_item_from_name(item_name):
    item = Item()
    df_row = ITEMS_DF.loc[ITEMS_DF["Name"] == item_name]
    item.name = item_name
    item.id = int(df_row["ID"].iloc[0])
    item.uses = int(df_row["Uses"].iloc[0])
    return item

def get_items_for_weapon_type(weapon_index, rank, chapter, corrin):
    if rank <= 0:
        return []
    weapon_type = WEAPON_TYPES[weapon_index]
    base_class = corrin.base_class_name
    promoted_class = corrin.promoted_class_name
    level = int(CHAPTER_DF.loc[CHAPTER_DF["Chapter"] == chapter, "Level"].iloc[0])
    if level >= 20:
        current_class = promoted_class
    else:
        current_class = base_class
    base_weapons = get_class_weapons(base_class)
    weapons = []
    if weapon_type == "Stone":
        isBeast = len(get_class_weapons(current_class)) == 1
        if isBeast:
            weapons.append(get_item_from_name("Beaststone"))
            if chapter >= RUNE_THRESHOLD:
                weapons.append(get_item_from_name("Beastrune"))
            if chapter >= SILVER_THRESHOLD:
                weapons.append(get_item_from_name("Beaststone+"))
        else:
            weapons.append(get_item_from_name("Dragonstone"))
            if chapter >= SILVER_THRESHOLD:
                weapons.append(get_item_from_name("Dragonstone+"))
    elif weapon_type == "Staff":
        rank = "E"
        if chapter >= STAFF_PROMO_THRESHOLD or (chapter >= STAFF_THRESHOLD and weapon_type in base_weapons):
            rank = "D"
        staff_name = construct_weapon_name(rank, weapon_type, current_class)
        weapons.append(get_item_from_name(staff_name))
    else:
        prefix = "Iron"
        if chapter >= SILVER_PROMO_THRESHOLD or chapter >= SILVER_THRESHOLD and weapon_type in base_weapons:
            prefix = "Silver"
        elif rank + corrin.internal_level * 1.5 >= C_RANK_REQUIREMENT:
            prefix = "Steel"
        weapon_name = construct_weapon_name(prefix, weapon_type, current_class)
        weapons.append(get_item_from_name(weapon_name))
    return weapons

def construct_weapon_name(prefix, weapon_type, current_class):
    class_row = CLASSES_DF.loc[CLASSES_DF["Name"] == current_class]
    hoshidan = bool(class_row["Hoshidan"].iloc[0])
    if weapon_type == "Tome":
        if hoshidan:
            return STANDARD_SPIRITS[STANDARD_METALS.index(prefix)]
        else:
            return STANDARD_TOMES[STANDARD_METALS.index(prefix)]
    elif weapon_type == "Staff":
        if hoshidan:
            if prefix == "E":
                return "Bloom Festival"
            else:
                return "Sun Festival"
        else:
            if prefix == "E":
                return "Heal"
            else:
                return "Mend"
    else:
        if hoshidan:
            if prefix == "Bronze":
                prefix = "Brass"
            suffix = HOSHIDAN_WEAPONS[WEAPON_TYPES.index(weapon_type)]
        else:
            suffix = weapon_type
        return prefix + " " + suffix