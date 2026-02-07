import random

class Corrin:
    def __init__(self):
        # Basic Info
        self.corrin_name = ""
        self.twitch_name = ""
        self.timestamp = ""
        self.wr_seed = random.randint(1,2) #1 = Lance Main Weapon, 2 = Not Lance Main Weapon
        
        # Appearance
        self.build = ""
        self.gender = ""
        self.build_value = 0
        self.gender_value = 0
        self.face = 0
        self.hairstyle = 0
        self.hair_decoration = 0
        self.facial_detail = 0
        self.voice_type = ""
        self.voice_id = None
        
        # Hair Color
        self.hair_color_value = None
        self.hair_color_hex = None
        self.is_custom_color = False
        
        # Accessories
        self.head_accessory_name = ""
        self.head_accessory_id = None
        self.face_accessory_name = ""
        self.face_accessory_id = None
        self.arm_accessory_name = ""
        self.arm_accessory_id = None
        self.body_accessory_name = ""
        self.body_accessory_id = None
        
        # Stats
        self.boon_name = ""
        self.boon_id = None
        self.bane_name = ""
        self.bane_id = None
        self.stats = [0, 0, 0, 0, 0, 0, 0, 0] #HP, Str, Mag, Skl, Spd, Lck, Def, Res
        self.growth_stats = [0, 0, 0, 0, 0, 0, 0, 0]
        self.weapon_ranks = [0, 0, 0, 0, 0, 0, 0, 0] #Sword, Lance, Axe, Shuriken, Bow, Tome, Staff, Stone
        self.level = 1
        self.internal_level = 0
        
        # Classes
        self.base_class_name = ""
        self.base_class_id = None
        self.promoted_class_name = ""
        self.promoted_class_id = None
        self.current_class_name = ""
        self.current_class_id = None
        
        # Skills
        self.personal_skill_1_name = ""
        self.personal_skill_1_id = None
        self.personal_skill_2_name = ""
        self.personal_skill_2_id = None
        self.equipped_skills = []
        self.learned_skills = [False] * 160
        self.learned_skills[0] = True

        #Items
        self.items = []

    def to_csv_row(self):
        """Convert character data to a row for the CSV export"""
        return {
            'Corrin Name': self.corrin_name,
            'Twitch Name': self.twitch_name,
            'Build': self.build,
            'Hair': self.hairstyle,
            'Hair Clip': self.hair_decoration,
            'Hair Color': 'Custom' if self.is_custom_color else self.hair_color_value,
            'Color Hex Code': self.hair_color_hex,
            'Face': self.face,
            'Facial Feature': self.facial_detail,
            'Voice': self.voice_type,
            'Hair Accessory': self.head_accessory_name,
            'Face Accessory': self.face_accessory_name,
            'Arm Accessory': self.arm_accessory_name,
            'Body Accessory': self.body_accessory_name,
            'Boon': self.boon_name,
            'Bane': self.bane_name,
            'Base Class': self.base_class_name,
            'Promoted Class': self.promoted_class_name,
            'Personal Skill 1': self.personal_skill_1_name,
            'Personal Skill 2': self.personal_skill_2_name,
            'Timestamp': self.timestamp
        }

class Item:
    def __init__(self):
        self.name = ""
        self.id = 0
        self.uses = 0

def json_to_character(json_data):
    """Convert JSON data to a Character object"""
    char = Corrin()
    
    # Basic Info
    char.corrin_name = json_data.get('name', '').replace("â€™", "'")
    char.twitch_name = json_data.get('twitchUsername', '').replace("â€™", "'")
    char.timestamp = json_data.get('creationDate', '1_1_1_1')
    
    # Appearance
    appearance = json_data.get('appearance', {})
    build = appearance.get('build', {})
    char.build = build.get('name', '')
    char.gender = build.get('gender', '')
    char.build_value = build.get('buildValue', 0)
    char.gender_value = build.get('genderValue', 0)
    
    char.face = appearance.get('face', 0)
    char.hairstyle = appearance.get('hairstyle', 0)
    char.hair_decoration = appearance.get('hairDecoration', 0)
    char.facial_detail = appearance.get('facialDetail', 0)
    
    voice = appearance.get('voice', {})
    char.voice_type = voice.get('name', '')
    char.voice_id = voice.get('id')
    
    # Hair Color
    hair_color = appearance.get('hairColor', {})
    if isinstance(hair_color, dict):
        char.hair_color_value = hair_color.get('value', '')
        char.hair_color_hex = hair_color.get('hex', '')
        char.is_custom_color = hair_color.get('value') == 'custom'
    
    # Accessories
    accessories = appearance.get('accessories', {})
    
    head = accessories.get('head', {})
    char.head_accessory_name = head.get('name', '') if head else ''
    char.head_accessory_id = head.get('id') if head else 0
    
    face = accessories.get('face', {})
    char.face_accessory_name = face.get('name', '') if face else ''
    char.face_accessory_id = face.get('id') if face else 0
    
    arm = accessories.get('arm', {})
    char.arm_accessory_name = arm.get('name', '') if arm else ''
    char.arm_accessory_id = arm.get('id') if arm else 0
    
    body = accessories.get('body', {})
    char.body_accessory_name = body.get('name', '') if body else ''
    char.body_accessory_id = body.get('id') if body else 0
    
    # Stats
    stats = json_data.get('stats', {})
    boon = stats.get('boon', {})
    char.boon_name = boon.get('name', '') if boon else ''
    char.boon_id = boon.get('id') if boon else None
    
    bane = stats.get('bane', {})
    char.bane_name = bane.get('name', '') if bane else ''
    char.bane_id = bane.get('id') if bane else None
    
    # Classes
    classes = json_data.get('classes', {})
    base = classes.get('base', {})
    char.base_class_name = base.get('name', '') if base else ''
    char.base_class_id = base.get('id') if base else None
    
    promoted = classes.get('promoted', {})
    char.promoted_class_name = promoted.get('name', '') if promoted else ''
    char.promoted_class_id = promoted.get('id') if promoted else None
    
    # Skills
    skills = json_data.get('skills', {})
    skill1 = skills.get('personal1', {})
    char.personal_skill_1_name = skill1.get('name', '') if skill1 else ''
    char.personal_skill_1_id = skill1.get('id') if skill1 else 0
    
    skill2 = skills.get('personal2', {})
    char.personal_skill_2_name = skill2.get('name', '') if skill2 else ''
    char.personal_skill_2_id = skill2.get('id') if skill2 else 0
    
    return char