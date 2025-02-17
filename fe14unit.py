import copy
import numpy as np
import random
import struct

BASE_FILE = bytearray(b'\x07\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x01\x00!\x00\x00\x00\x8b-\xab\x00mu\x0bVj$cI\x03\x04\x01\x04\x04\x04\x02\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x01\x01\x01\x01\x01\x01\x01\x16\xff\xff\xff\xff\x00\x01\x00\x10\x00\x00\x00\x00\xff\xff\x00\xff\x003\x00Y\x009\x00\x00\x00\x00\x00\x00\x16\x00\x00@\x00\x15\x01\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd9\xee\xeb\xff\x00\xabN\xaa\xc0\xe2JE\x90\x12\x83\x18u\xb7\x00\x00\x00\x02\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x14\x00\x00\x00\x01\x00\x00\x00\x00\x00\x08\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00;\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x04C\x00o\x00l\x00g\x00a\x00t\x00e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x03\t\x00\x00\x00\x01\x0b\xd9\xee\xeb\xff\x00\x01\x00\x01\x01\x00')

IS_FEMALE_FLAG_ADDRESS = 0x1 #Byte, 00 for Male Corrins 01 for Female Corrins I believe
LEVEL_ADDRESS = 0x9 #Byte
INTERNAL_LEVEL_ADDRESS = 0xB #Byte
CLASS_ADDRESS = 0xF #Byte
SEED_ADDRESS = 0x13 #12 Bytes, completely random number?
STATS_ADDRESS = 0x1f #8Bytes in order of HP, Str, Mag, Skl, Spd, Lck, Def, Res. These are true growth stats, so take visible stat and subtract Class base, Corrin Base, AND Boon/Bane base. If base stat is negative and visible stat is zero this is a positive value
WEAPON_RANK_ADDRESS = 0x3F #8Bytes in order of Sword, Lance, Axe, Dagger, Bow, Tome, Staff, Stone
EQUIPPED_SKILLS_ADDRESS = 0x59 #10 Bytes, 5 skills separated by 00
INVENTORY_ADDRESS = 0x64 #25 Bytes. Each item is 5(4) Bytes, first 2 are ID, 3rd/5th is 00, 4th is uses + equipped (Add 0x40 if equipped)
HAIR_COLOR_2_ADDRESS = 0xD3
#0xD3 is 17 Bytes of unknown numbers but 0405 is always FF00, possible this is seed related but seems more based on character creation
LEARNED_SKILLS_ADDRESS = 0x106 #20 Byte bitmask
ACCESSORIES_ADDRESS = 0x11f #4 Bytes in order of hair->face->arm->body ID
NAME_ADDRESS = 0x12e #24 Bytes 12 characters separated by 00
BOON_ADDRESS = 0x148 #Byte
BANE_ADDRESS = 0x149 #Byte
GENDER_ADDRESS = 0x14c #Byte
BUILD_ADDRESS = 0x14d #Byte
FACE_ADDRESS = 0x14e #Byte
HAIR_ADDRESS = 0x14f #Byte
HAIR_COLOR_ADDRESS = 0x150 #3Bytes r, g, b
HAIR_CLIP_ADDRESS = 0x154 #Byte
FACIAL_DETAIL_ADDRESS = 0x155 #Byte
VOICE_ADDRESS = 0x156 #Byte

def write(bytearr, data, offset):
        for i in range(len(data)):
            bytearr[offset + i] = data[i]

def write_halfword(bytearr, data, offset):
    return write(bytearr, struct.pack('<h', data), offset)

def create_fe14unit_bytearray(corrin):
    file = copy.deepcopy(BASE_FILE)
    file[IS_FEMALE_FLAG_ADDRESS] = corrin.gender_value
    file[LEVEL_ADDRESS] = corrin.level
    file[INTERNAL_LEVEL_ADDRESS] = corrin.internal_level
    file[CLASS_ADDRESS] = corrin.current_class_id
    for i in range(12):
        file[SEED_ADDRESS + i] = random.randrange(256)
    for i in range(8):
        file[STATS_ADDRESS + i] = corrin.growth_stats[i]
    for i in range(8):
        file[WEAPON_RANK_ADDRESS + i] = corrin.weapon_ranks[i]
    for i in range(5):
        if len(corrin.equipped_skills) > i:
            file[EQUIPPED_SKILLS_ADDRESS + 2 * i] = corrin.equipped_skills[i]
        else:
            file[EQUIPPED_SKILLS_ADDRESS + 2 * i] = 0
    for i in range(5):
        offset = INVENTORY_ADDRESS + 5 * i
        if len(corrin.items) > i:
            current_item = corrin.items[i]
            write_halfword(file, current_item.id, offset)
            if i == 0:
                file[offset + 3] = current_item.uses + 0x40
            else:
                file[offset + 3] = current_item.uses
        else:
            write_halfword(file, 0, offset)
            file[offset + 3] = 0
    for i in range(20):
        boolmask = corrin.learned_skills[i * 8:i * 8 + 8]
        bitmask = np.packbits(boolmask, bitorder = 'little')
        file[LEARNED_SKILLS_ADDRESS + i] = bitmask[0]
    file[ACCESSORIES_ADDRESS] = corrin.head_accessory_id
    file[ACCESSORIES_ADDRESS + 1] = corrin.face_accessory_id
    file[ACCESSORIES_ADDRESS + 2] = corrin.arm_accessory_id
    file[ACCESSORIES_ADDRESS + 3] = corrin.body_accessory_id
    for i in range(12):
        if len(corrin.corrin_name) > i:
            file[NAME_ADDRESS + 2 * i] = corrin.corrin_name[i].encode('utf-8')[0]
        else:
            file[NAME_ADDRESS + 2 * i] = 0
    file[BOON_ADDRESS] = corrin.boon_id
    file[BANE_ADDRESS] = corrin.bane_id
    file[GENDER_ADDRESS] = corrin.gender_value
    file[BUILD_ADDRESS] = corrin.build_value
    file[FACE_ADDRESS] = corrin.face
    file[HAIR_ADDRESS] = corrin.hairstyle
    file[HAIR_COLOR_ADDRESS] = bytes.fromhex(corrin.hair_color_hex[1:3])[0]
    file[HAIR_COLOR_ADDRESS + 1] = bytes.fromhex(corrin.hair_color_hex[3:5])[0]
    file[HAIR_COLOR_ADDRESS + 2] = bytes.fromhex(corrin.hair_color_hex[5:7])[0]
    file[HAIR_COLOR_2_ADDRESS] = file[HAIR_COLOR_ADDRESS]
    file[HAIR_COLOR_2_ADDRESS + 1] = file[HAIR_COLOR_ADDRESS + 1]
    file[HAIR_COLOR_2_ADDRESS + 2] = file[HAIR_COLOR_ADDRESS + 2]
    file[HAIR_CLIP_ADDRESS] = corrin.hair_decoration
    file[FACIAL_DETAIL_ADDRESS] = corrin.facial_detail
    file[VOICE_ADDRESS] = corrin.voice_id
    return file