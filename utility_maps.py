COLOR_NAME_MAP = {
    frozenset(['W']): 'Mono W', frozenset(['U']): 'Mono U', frozenset(['B']): 'Mono B', 
    frozenset(['R']): 'Mono R', frozenset(['G']): 'Mono G',
    frozenset(['W', 'U']): 'Azorius {UW}', frozenset(['U', 'B']): 'Dimir {UB}', 
    frozenset(['B', 'R']): 'Rakdos {RB}', frozenset(['R', 'G']): 'Gruul {RG}', 
    frozenset(['G', 'W']): 'Selesnya {GW}', frozenset(['W', 'B']): 'Orzhov {BW}', 
    frozenset(['U', 'R']): 'Izzet {UR}', frozenset(['B', 'G']): 'Golgari {BG}', 
    frozenset(['R', 'W']): 'Boros {RW}', frozenset(['G', 'U']): 'Simic {UG}',
    frozenset(['W', 'U', 'B']): 'Esper {BWU}', frozenset(['U', 'B', 'R']): 'Grixis {RBU}', 
    frozenset(['B', 'R', 'G']): 'Jund {RGB}', frozenset(['R', 'G', 'W']): 'Naya {RGW}', 
    frozenset(['G', 'W', 'U']): 'Bant {GWU}', frozenset(['W', 'B', 'G']): 'Abzan {BWG}', 
    frozenset(['U', 'R', 'W']): 'Jeskai {RWU}', frozenset(['B', 'G', 'U']): 'Sultai {BGU}', 
    frozenset(['R', 'W', 'B']): 'Mardu {RWB}', frozenset(['G', 'U', 'R']): 'Temur {RGU}'
}

LAND_DATA_MAP = {
    # Basics
    "Mountain": {"mana": "R", "tags": {"basic"}},
    "Swamp": {"mana": "B", "tags": {"basic"}},
    "Island": {"mana": "U", "tags": {"basic"}},
    "Forest": {"mana": "G", "tags": {"basic"}},
    "Plains": {"mana": "W", "tags": {"basic"}},

    # Snow Basics
    "Snow-Covered Mountain": {"mana": "R", "tags": {"snow", "basic"}},
    "Snow-Covered Swamp": {"mana": "B", "tags": {"snow", "basic"}},
    "Snow-Covered Island": {"mana": "U", "tags": {"snow", "basic"}},
    "Snow-Covered Forest": {"mana": "G", "tags": {"snow", "basic"}},
    "Snow-Covered Plains": {"mana": "W", "tags": {"snow", "basic"}},

    # Artifact Mono
    "Ancient Den": {"mana": "W", "tags": {"artifact"}},
    "Seat of the Synod": {"mana": "U", "tags": {"artifact"}},
    "Vault of Whispers": {"mana": "B", "tags": {"artifact"}},
    "Great Furnace": {"mana": "R", "tags": {"artifact"}},
    "Tree of Tales": {"mana": "G", "tags": {"artifact"}},

    # The Colorless Artifact Lands
    "Darksteel Citadel": {"mana": "C", "tags": {"artifact", "indestructible"}},
    "Treasure Vault": {"mana": "C", "tags": {"artifact", "treasure", "sacrifice"}},

    # Artifact Dual Bridges
    "Darkmoss Bridge": {"mana": "BG", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Drossforge Bridge": {"mana": "RB", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Goldmire Bridge": {"mana": "BW", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Mistvault Bridge": {"mana": "UB", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Razortide Bridge": {"mana": "WU", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Rustvale Bridge": {"mana": "RW", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Silverbluff Bridge": {"mana": "UR", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Slagwoods Bridge": {"mana": "RG", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Tanglepool Bridge": {"mana": "UG", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Thornglint Bridge": {"mana": "GW", "tags": {"dual", "artifact", "indestructible", "tapped"}},

    # Snow Duals
    "Alpine Meadow": {"mana": "RW", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Arctic Treeline": {"mana": "GW", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Glacial Floodplain": {"mana": "WU", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Highland Forest": {"mana": "RG", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Ice Tunnel": {"mana": "UB", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Rimewood Falls": {"mana": "UG", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Snowfield Sinkhole": {"mana": "BW", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Sulfurous Mire": {"mana": "RB", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Volatile Fjord": {"mana": "UR", "tags": {"dual", "snow", "basic_type", "tapped"}},
    "Woodland Chasm": {"mana": "BG", "tags": {"dual", "snow", "basic_type", "tapped"}},

    # Basic Duals
    "Contaminated Aquifer": {"mana": "UB", "tags": {"dual", "basic_type", "tapped"}},
    "Geothermal Bog": {"mana": "BR", "tags": {"dual", "basic_type", "tapped"}},
    "Haunted Mire": {"mana": "BG", "tags": {"dual", "basic_type", "tapped"}},
    "Idyllic Beachfront": {"mana": "WU", "tags": {"dual", "basic_type", "tapped"}},
    "Molten Tributary": {"mana": "UR", "tags": {"dual", "basic_type", "tapped"}},
    "Radiant Grove": {"mana": "GW", "tags": {"dual", "basic_type", "tapped"}},
    "Sacred Peaks": {"mana": "RW", "tags": {"dual", "basic_type", "tapped"}},
    "Sunlit Marsh": {"mana": "WB", "tags": {"dual", "basic_type", "tapped"}},
    "Tangled Islet": {"mana": "UG", "tags": {"dual", "basic_type", "tapped"}},
    "Wooded Ridgeline": {"mana": "RG", "tags": {"dual", "basic_type", "tapped"}},

    # Life-Gain Duals (M21/Kaldheim/Khans - Commons)
    "Bloodfell Caves": {"mana": "RB", "tags": {"dual", "lifegain", "tapped"}},
    "Blossoming Sands": {"mana": "GW", "tags": {"dual", "lifegain", "tapped"}},
    "Dismal Backwater": {"mana": "UB", "tags": {"dual", "lifegain", "tapped"}},
    "Jungle Hollow": {"mana": "BG", "tags": {"dual", "lifegain", "tapped"}},
    "Rugged Highlands": {"mana": "RG", "tags": {"dual", "lifegain", "tapped"}},
    "Scoured Barrens": {"mana": "BW", "tags": {"dual", "lifegain", "tapped"}},
    "Swiftwater Cliffs": {"mana": "UR", "tags": {"dual", "lifegain", "tapped"}},
    "Thornwood Falls": {"mana": "UG", "tags": {"dual", "lifegain", "tapped"}},
    "Tranquil Cove": {"mana": "WU", "tags": {"dual", "lifegain", "tapped"}},
    "Wind-Scarred Crag": {"mana": "RW", "tags": {"dual", "lifegain", "tapped"}},

    # Bounce Lands (Ravnica Karoos)
    "Azorius Chancery": {"mana": "WU", "tags": {"dual", "bounce", "tapped"}},
    "Boros Garrison": {"mana": "RW", "tags": {"dual", "bounce", "tapped"}},
    "Dimir Aqueduct": {"mana": "UB", "tags": {"dual", "bounce", "tapped"}},
    "Golgari Rot Farm": {"mana": "BG", "tags": {"dual", "bounce", "tapped"}},
    "Gruul Turf": {"mana": "RG", "tags": {"dual", "bounce", "tapped"}},
    "Izzet Boilerworks": {"mana": "UR", "tags": {"dual", "bounce", "tapped"}},
    "Orzhov Basilica": {"mana": "BW", "tags": {"dual", "bounce", "tapped"}},
    "Rakdos Carnarium": {"mana": "RB", "tags": {"dual", "bounce", "tapped"}},
    "Selesnya Sanctuary": {"mana": "GW", "tags": {"dual", "bounce", "tapped"}},
    "Simic Growth Chamber": {"mana": "UG", "tags": {"dual", "bounce", "tapped"}},

    # Strixhaven Campuses
    "Lorehold Campus": {"mana": "RW", "tags": {"dual", "scry"}},
    "Prismari Campus": {"mana": "UR", "tags": {"dual", "scry"}},
    "Quandrix Campus": {"mana": "UG", "tags": {"dual", "scry"}},
    "Silverquill Campus": {"mana": "BW", "tags": {"dual", "scry"}},
    "Witherbloom Campus": {"mana": "BG", "tags": {"dual", "scry"}},

    # Dual Desert Pingers
    "Abraded Bluffs": {"mana": "RW", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Bristling Backwoods": {"mana": "RG", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Creosote Heath": {"mana": "GW", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Eroded Canyon": {"mana": "UR", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Festering Gulch": {"mana": "BG", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Forlorn Flats": {"mana": "BW", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Jagged Barrens": {"mana": "RB", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Lonely Arroyo": {"mana": "WU", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Lush Oasis": {"mana": "UG", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Soured Springs": {"mana": "UB", "tags": {"dual", "desert", "pinger", "tapped"}},

    # Check-life Duals
    "Abandoned Campground": {"mana": "RG", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Bleeding Woods": {"mana": "BG", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Etched Cornfield": {"mana": "GW", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Lakeside Shack": {"mana": "UG", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Murky Sewer": {"mana": "UB", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Neglected Manor": {"mana": "WU", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Peculiar Lighthouse": {"mana": "UR", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Raucous Carnival": {"mana": "RB", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Razortrap Gorge": {"mana": "RW", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Strangled Cemetery": {"mana": "BW", "tags": {"dual", "life_check", "conditional_tapped"}},

    # Guildgates
    "Azorius Guildgate": {"mana": "WU", "tags": {"dual", "gate", "tapped"}},
    "Boros Guildgate": {"mana": "RW", "tags": {"dual", "gate", "tapped"}},
    "Dimir Guildgate": {"mana": "UB", "tags": {"dual", "gate", "tapped"}},
    "Golgari Guildgate": {"mana": "BG", "tags": {"dual", "gate", "tapped"}},
    "Gruul Guildgate": {"mana": "RG", "tags": {"dual", "gate", "tapped"}},
    "Izzet Guildgate": {"mana": "UR", "tags": {"dual", "gate", "tapped"}},
    "Orzhov Guildgate": {"mana": "BW", "tags": {"dual", "gate", "tapped"}},
    "Rakdos Guildgate": {"mana": "RB", "tags": {"dual", "gate", "tapped"}},
    "Selesnya Guildgate": {"mana": "GW", "tags": {"dual", "gate", "tapped"}},
    "Simic Guildgate": {"mana": "UG", "tags": {"dual", "gate", "tapped"}},

    # Dual Choice Gates
    "Citadel Gate": {"mana": "W", "tags": {"gate", "dual", "choice", "tapped"}},
    "Sea Gate": {"mana": "U", "tags": {"gate", "dual", "choice", "tapped"}},
    "Black Dragon Gate": {"mana": "B", "tags": {"gate", "dual", "choice", "tapped"}},
    "Cliffgate": {"mana": "R", "tags": {"gate", "dual", "choice", "tapped"}},
    "Manor Gate": {"mana": "G", "tags": {"gate", "dual", "choice", "tapped"}},

    # Avatar Duals Sac Draw
    "Foggy Bottom Swamp": {"mana": "BG", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Airship Engine Room": {"mana": "UR", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Boiling Rock Prison": {"mana": "RB", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Kyoshi Village": {"mana": "GW", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Misty Palms Oasis": {"mana": "BW", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Meditation Pools": {"mana": "UG", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "North Pole Gates": {"mana": "UW", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Omashu City": {"mana": "RG", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Serpent's Pass": {"mana": "UB", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Sub-blessed Peak": {"mana": "RW", "tags": {"dual", "draw", "sacrifice", "tapped"}},

    # Avatar Scry Fix
    "Rumble Arena": {"mana": "C", "tags": {"scry", "etb", "fixer"}},

    # Final Fantasy Duals
    "Baron, Airship Kingdom": {"mana": "UR", "tags": {"town", "dual", "tapped"}},
    "Gohn, Town of Ruin": {"mana": "BG", "tags": {"town", "dual", "tapped"}},
    "Gongaga, Reactor Town": {"mana": "RG", "tags": {"town", "dual", "tapped"}},
    "Guadosalam, Farplane Gateway": {"mana": "UG", "tags": {"town", "dual", "tapped"}},
    "Insomnia, Crown City": {"mana": "BW", "tags": {"town", "dual", "tapped"}},
    "Rabanastre, Royal City": {"mana": "RW", "tags": {"town", "dual", "tapped"}},
    "Sharlayan, Nation of Scholars": {"mana": "UW", "tags": {"town", "dual", "tapped"}},
    "Treno, Dark City": {"mana": "UB", "tags": {"town", "dual", "tapped"}},
    "Vector, Imperial Capital": {"mana": "RB", "tags": {"town", "dual", "tapped"}},
    "Windurst, Federation Center": {"mana": "GW", "tags": {"town", "dual", "tapped"}},

    # Final Fantasy Others
    "Adventurer's Inn": {"mana": "C", "tags": {"town", "etb", "lifegain"}},
    "Crossroads Village": {"mana": "WUBRG", "tags": {"town", "fixer", "tapped"}},

    # Spiderman
    "Savage Mansion": {"mana": "RG", "tags": {"utility", "surveil", "dual", "tapped"}},
    "University Campus": {"mana": "UW", "tags": {"utility", "surveil", "dual", "tapped"}},
    "Sinister Hideout": {"mana": "UB", "tags": {"utility", "surveil", "dual", "tapped"}},
    "Ominous Asylum": {"mana": "RB", "tags": {"utility", "surveil", "dual", "tapped"}},
    "Suburban Sanctuary": {"mana": "GW", "tags": {"utility", "surveil", "dual", "tapped"}},

    # Utility Gates
    "Basilisk Gate": {"mana": "C", "tags": {"gate", "utility", "buff"}},
    "Baldur's Gate": {"mana": "C", "tags": {"gate", "utility", "ramp"}},
    "Gond Gate": {"mana": "C", "tags": {"gate", "utility", "fixer"}},
    "Heap Gate": {"mana": "C", "tags": {"gate", "utility", "treasure", "fixer"}},
    "Gateway Plaza": {"mana": "WUBRG", "tags": {"gate", "fixer", "tapped"}},
    "Plaza of Harmony": {"mana": "C", "tags": {"utility", "fixer", "lifegain"}}, # Not a gate itself, but fits the search
    "Maze's End": {"mana": "C", "tags": {"utility", "fetch", "win_con"}},
    
    # ETB Mono conditional_tapped Eldrain
    "Idyllic Grange": {"mana": "W", "tags": {"etb", "buff", "conditional_tapped"}},
    "Mystic Sanctuary": {"mana": "U", "tags": {"etb", "recursion", "conditional_tapped"}},
    "Witch's Cottage": {"mana": "B", "tags": {"etb", "recursion", "conditional_tapped"}},
    "Dwarven Mine": {"mana": "R", "tags": {"etb", "token", "conditional_tapped"}},
    "Gingerbread Cabin": {"mana": "G", "tags": {"etb", "food", "conditional_tapped"}},

    # Worldwake One-time spell ETB
    "Bojuka Bog": {"mana": "B", "tags": {"etb", "graveyard", "tapped"}},
    "Halimar Depths": {"mana": "U", "tags": {"etb", "top_deck", "tapped"}},
    "Khalni Garden": {"mana": "G", "tags": {"etb", "token", "tapped"}},
    "Smoldering Spires": {"mana": "R", "tags": {"etb", "combat", "tapped"}},
    "Sejiri Steppe": {"mana": "W", "tags": {"etb", "protection", "tapped"}},

    # "Kabira Crossroads": {"mana": "W", "tags": {"mono", "etb", "lifegain", "tapped"}},
    "Skyline Cascade": {"mana": "U", "tags": {"etb", "freeze", "tapped"}},
    "Mortuary Mire": {"mana": "B", "tags": {"etb", "recursion", "tapped"}},
    "Looming Spires": {"mana": "R", "tags": {"etb", "buff", "tapped"}},
    "Fertile Thicket": {"mana": "G", "tags": {"etb", "filter_top", "tapped"}},

    # Mono Depletion
    "Hickory Woodlot": {"mana": "G", "tags": {"depletion", "tapped"}},
    "Peat Bog": {"mana": "B", "tags": {"depletion", "tapped"}},
    "Remote Farm": {"mana": "W", "tags": {"depletion", "tapped"}},
    "Sandstone Needle": {"mana": "R", "tags": {"depletion", "tapped"}},
    "Saprazzan Skerry": {"mana": "U", "tags": {"depletion", "tapped"}},

    # Mono Cyclers
    "Secluded Steppe": {"mana": "W", "tags": {"cycler","pure_cycler", "tapped"}},
    "Lonely Sandbar": {"mana": "U", "tags": {"cycler","pure_cycler", "tapped"}},
    "Barren Moor": {"mana": "B", "tags": {"cycler","pure_cycler", "tapped"}},
    "Forgotten Cave": {"mana": "R", "tags": {"cycler","pure_cycler", "tapped"}},
    "Tranquil Thicket": {"mana": "G", "tags": {"cycler","pure_cycler", "tapped"}},
    "Ash Barrens": {"mana": "C", "tags": {"cycler", "basic_land_cycler"}},

    # Mono Tapped Card Draw
    "The Fair Basilica": {"mana": "W", "tags": {"sacrifice", "draw", "tapped"}},
    "The Surgical Bay": {"mana": "U", "tags": {"sacrifice", "draw", "tapped"}},
    "The Dross Pits": {"mana": "B", "tags": {"sacrifice", "draw", "tapped"}},
    "The Autonomous Furnace": {"mana": "R", "tags": {"sacrifice", "draw", "tapped"}},
    "The Hunter Maze": {"mana": "G", "tags": {"sacrifice", "draw", "tapped"}},
    
    # Tapped Pure Cyclers
    "Blasted Landscape": {"mana": "C", "tags": {"cycler", "pure_cycler"}},
    "Drifting Meadow": {"mana": "W", "tags": {"cycler", "pure_cycler", "tapped"}},
    "Remote Isle": {"mana": "U", "tags": {"cycler", "pure_cycler", "tapped"}},
    "Polluted Mire": {"mana": "B", "tags": {"cycler", "tapped"}},
    "Smoldering Crater": {"mana": "R", "tags": {"cycler", "pure_cycler", "tapped"}},
    "Slippery Karst": {"mana": "G", "tags": {"cycler", "pure_cycler", "tapped"}},

    # Desert Cyclers
    "Desert of the True": {"mana": "W", "tags": {"desert", "cycler", "pure_cycler", "tapped"}},
    "Desert of the Mindful": {"mana": "U", "tags": {"desert", "cycler", "pure_cycler", "tapped"}},
    "Desert of the Glorified": {"mana": "B", "tags": {"desert", "cycler", "pure_cycler", "tapped"}},
    "Desert of the Fervent": {"mana": "R", "tags": {"desert", "cycler", "pure_cycler", "tapped"}},
    "Desert of the Indomitable": {"mana": "G", "tags": {"desert", "cycler", "pure_cycler", "tapped"}},

    # Fetch
    "Terramorphic Expanse": {"mana": "", "tags": {"fetch", "basic_fecth", "tapped"}},
    "Evolving Wilds": {"mana": "", "tags": {"fetch", "basic_fecth", "tapped"}},
    "Warped Landscape": {"mana": "C", "tags": {"fetch", "basic_fecth", "tapped"}},
    "Vibrant Cutyscape": {"mana": "", "tags": {"fetch", "basic_fecth", "tapped"}},

    # Thriving Lands (Jumpstart - Uncommons) - "Choice" lands
    "Thriving Bluff": {"mana": "R", "tags": {"choice", "tapped"}},
    "Thriving Heath": {"mana": "W", "tags": {"choice", "tapped"}},
    "Thriving Isle": {"mana": "U", "tags": {"choice", "tapped"}},
    "Thriving Moor": {"mana": "B", "tags": {"choice", "tapped"}},
    "Thriving Grove": {"mana": "G", "tags": {"choice", "tapped"}},

    # Ixilan Caves
    "Hidden Courtyard": {"mana": "W", "tags": {"sacrifice", "discover", "tapped"}},
    "Hidden Cataract": {"mana": "U", "tags": {"sacrifice", "discover", "tapped"}},
    "Hidden Necropolis": {"mana": "B", "tags": {"sacrifice", "discover", "tapped"}},
    "Hidden Volcano": {"mana": "R", "tags": {"sacrifice", "discover", "tapped"}},
    "Hidden Nursery": {"mana": "G", "tags": {"sacrifice", "discover", "tapped"}},

    # Landscapes
    "Shattered Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Bountiful Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Contaminated Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Deceptive Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Foreboding Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Perilous Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}}, # 4-color fetch
    "Seething Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Sheltering Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Tranquil Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},
    "Twisted Landscape": {"mana": "C", "tags": {"landscape", "fetch", "basic_fecth", "cycler", "pure_cycler"}},

    # New Capenna Fetch Lifegain
    "Brokers Hideout": {"mana": "GWU", "tags": {"fetch", "basic_fecth", "lifegain"}},
    "Obscura Storefront": {"mana": "WUB", "tags": {"fetch", "basic_fecth", "lifegain"}},
    "Maestros Theater": {"mana": "UBR", "tags": {"fetch", "basic_fecth", "lifegain"}},
    "Riveteers Overlook": {"mana": "BRG", "tags": {"fetch", "basic_fecth", "lifegain"}},
    "Cabaretti Courtyard": {"mana": "RGW", "tags": {"fetch", "basic_fecth", "lifegain"}},

    # New Capenna Sac-Draw Duals
    "Botanical Plaza": {"mana": "GW", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Racers' Ring": {"mana": "RG", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Skybridge Towers": {"mana": "UW", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Tramway Station": {"mana": "RB", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Waterfront District": {"mana": "UB", "tags": {"dual", "draw", "sacrifice", "tapped"}},

    "Foggy Bottom Swamp": {"mana": "BG", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Airship Engine Room": {"mana": "UR", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Misty Palms Oasis": {"mana": "BW", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Meditation Pools": {"mana": "UG", "tags": {"dual", "draw", "sacrifice", "tapped"}},
    "Sub-blessed Peak": {"mana": "RW", "tags": {"dual", "draw", "sacrifice", "tapped"}},

    # Tron Lands
    "Urza's Mine": {"mana": "C", "tags": {"tron", "ramp"}},
    "Urza's Power Plant": {"mana": "C", "tags": {"tron", "ramp"}},
    "Urza's Tower": {"mana": "C", "tags": {"tron", "ramp"}},

    # The Castles (Eldraine - Rares)
    "Castle Ardenvale": {"mana": "W", "tags": {"utility", "castle", "token"}},
    "Castle Vantress": {"mana": "U", "tags": {"utility", "castle", "scry"}},
    "Castle Locthwain": {"mana": "B", "tags": {"utility", "castle", "draw"}},
    "Castle Embereth": {"mana": "R", "tags": {"utility", "castle", "buff"}},
    "Castle Garenbrig": {"mana": "G", "tags": {"utility", "castle", "ramp"}},

    # Zendikar Rising Land // Spell Double Sided
    "Blackbloom Rogue // Blackbloom Bog": {"mana": "B", "tags": {"double_sided", "land_spell", "tapped"}},
    "Jwari Disruption // Jwari Ruins": {"mana": "U", "tags": {"double_sided", "land_spell", "tapped"}},
    "Kabira Takedown // Kabira Plateau": {"mana": "W", "tags": {"double_sided", "land_spell", "tapped"}},
    "Kazuul's Fury // Kazuul's Cliffs": {"mana": "R", "tags": {"double_sided", "land_spell", "tapped"}},
    "Khalni Ambush // Khalni Territory": {"mana": "G", "tags": {"double_sided", "land_spell", "tapped"}},
    "Malakir Rebirth // Malakir Mire": {"mana": "B", "tags": {"double_sided", "land_spell", "tapped"}},
    "Pelakka Predation // Pelakka Caverns": {"mana": "B", "tags": {"double_sided", "land_spell", "tapped"}},
    "Sejiri Shelter // Sejiri Glacier": {"mana": "W", "tags": {"double_sided", "land_spell", "tapped"}},
    "Silundi Vision // Silundi Isle": {"mana": "U", "tags": {"double_sided", "land_spell", "tapped"}},
    "Spikefield Hazard // Spikefield Cave": {"mana": "R", "tags": {"double_sided", "land_spell", "tapped"}},
    "Tangled Florahedron // Tangled Vale": {"mana": "G", "tags": {"double_sided", "land_spell", "tapped"}},
    "Umara Wizard // Umara Skyfalls": {"mana": "U", "tags": {"double_sided", "land_spell", "tapped"}},
    "Vastwood Fortification // Vastwood Thicket": {"mana": "G", "tags": {"double_sided", "land_spell", "tapped"}},
    "Zof Consumption // Zof Bloodbog": {"mana": "B", "tags": {"double_sided", "land_spell", "tapped"}},

    # Kaldheim Uncommon utility lands
    "Bretagard Stronghold": {"mana": "G", "tags": {"sacrifice", "buff", "tapped"}},
    "Gates of Istfell": {"mana": "W", "tags": {"sacrifice", "draw", "lifegain", "tapped"}},
    "Great Hall of Starnheim": {"mana": "B", "tags": {"sacrifice", "token", "creature", "tapped"}},
    "Immersturm Skullcairn": {"mana": "B", "tags": {"sacrifice", "discard", "burn" "tapped"}},
    "Littjara Mirrorlake": {"mana": "U", "tags": {"sacrifice", "copy", "token", "creature", "tapped"}},
    "Port of Karfell": {"mana": "U", "tags": {"sacrifice", "mill", "recursion", "tapped"}},
    "Skemfar Elderhall": {"mana": "G", "tags": {"sacrifice", "destruction", "token", "creature", "tapped"}},
    "Surtland Frostpyre": {"mana": "R", "tags": {"sacrifice", "scry", "board_wipe", "tapped"}},
    "Gnottvold Slumbermound": {"mana": "R", "tags": {"sacrifice", "land_destruction", "token", "creature", "tapped"}},
    "Axgard Armory": {"mana": "R", "tags": {"sacrifice", "tutor", "tapped"}},

    "Edgewall Inn": {"mana": "WUBRG", "tags": {"fixer", "utility", "recursion", "tapped"}},
    "Access Tunnel": {"mana": "C", "tags": {"utility", "unblockable"}},
    "Cave of Temptation": {"mana": "C", "tags": {"fixer", "sacrifice", "buff"}},
    "Cryptic Caves": {"mana": "C", "tags": {"sacrifice", "pure_cycler"}},
    "Crystal Grotto": {"mana": "C", "tags": {"fixer", "etb", "scry"}},
    "Emergence Zone": {"mana": "C", "tags": {"sacrifice", "utility"}},
    "Encroaching Wastes": {"mana": "C", "tags": {"sacrifice", "land_destruction"}},
    "Escape Tunnel": {"mana": "C", "tags": {"fetch", "basic_fetch", "utility" "sacrifice", "unblockable"}},
    "Faceless Haven": {"mana": "C", "tags": {"snow", "creature"}},
    "Field of Ruin": {"mana": "C", "tags": {"utility", "sacrifice", "land_destruction", "fetch", "basic_fetch"}},
    "Gargoyle Castle": {"mana": "C", "tags": {"sacrifice", "token"}},
    "Mishra's Factory": {"mana": "C", "tags": {"creature"}},
    "Mishra's Foundry": {"mana": "C", "tags": {"creature"}},
    "Promising Vein": {"mana": "C", "tags": {"cave" "fetch", "basic_fetch" "sacrifice"}},
    "Radiant Fountain": {"mana": "C", "tags": {"etb", "lifegain"}},
    "Seraph Sanctuary": {"mana": "C", "tags": {"etb", "lifegain"}},
    "Zhalfirin Void": {"mana": "C", "tags": {"etb", "scry"}},

    "Desert": {"mana": "C", "tags": {"desert", "utility"}},
    "Sunscorched Desert": {"mana": "C", "tags": {"desert", "etb", "pinger"}},
    "Archway Commons": {"mana": "WUBRG", "tags": {"fixer", "tapped"}},
    "Command Bridge": {"mana": "WUBRG", "tags": {"fixer", "tapped"}},
    "Great Hall of the Citadel": {"mana": "C", "tags": {"fixer", "legendary"}},
    "Interplanar Beacon": {"mana": "C", "tags": {"fixer", "lifegain"}},
    "Spawning Pool": {"mana": "B", "tags": {"creature", "tapped"}},
    "Throne of Makindi": {"mana": "C", "tags": {"utility", "ramp"}},
    "Tocasia's Dig Site": {"mana": "C", "tags": {"utility", "surveil"}},
    "Voldaren Estate": {"mana": "C", "tags": {"fixer", "token"}},
    "Shimmerdrift Vale": {"mana": "WUBRG", "tags": {"snow", "fixer", "tapped"}},

    
    "Tournament Grounds": {"mana": "RWBC", "tags": {"fixer", "utility"}},
    "Mystic Monastery": {"mana": "URW", "tags": {"tri", "tapped"}},
}