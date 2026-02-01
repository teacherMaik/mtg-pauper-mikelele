COLOR_NAME_MAP = {
    frozenset(['W']): 'White', frozenset(['U']): 'Blue', frozenset(['B']): 'Black', 
    frozenset(['R']): 'Red', frozenset(['G']): 'Green',
    frozenset(['W', 'U']): 'Azorius', frozenset(['U', 'B']): 'Dimir', 
    frozenset(['B', 'R']): 'Rakdos', frozenset(['R', 'G']): 'Gruul', 
    frozenset(['G', 'W']): 'Selesnya', frozenset(['W', 'B']): 'Orzhov', 
    frozenset(['U', 'R']): 'Izzet', frozenset(['B', 'G']): 'Golgari', 
    frozenset(['R', 'W']): 'Boros', frozenset(['G', 'U']): 'Simic',
    frozenset(['W', 'U', 'B']): 'Esper', frozenset(['U', 'B', 'R']): 'Grixis', 
    frozenset(['B', 'R', 'G']): 'Jund', frozenset(['R', 'G', 'W']): 'Naya', 
    frozenset(['G', 'W', 'U']): 'Bant', frozenset(['W', 'B', 'G']): 'Abzan', 
    frozenset(['U', 'R', 'W']): 'Jeskai', frozenset(['B', 'G', 'U']): 'Sultai', 
    frozenset(['R', 'W', 'B']): 'Mardu', frozenset(['G', 'U', 'R']): 'Temur'
}

LAND_DATA_MAP = {
    # Basics
    "Mountain": {"mana": "R", "tags": {}},
    "Swamp": {"mana": "B", "tags": {}},
    "Island": {"mana": "U", "tags": {}},
    "Forest": {"mana": "G", "tags": {}},
    "Plains": {"mana": "W", "tags": {}},

    # Snow Basics
    "Snow-Coverend Mountain": {"mana": "R", "tags": {"Snow"}},
    "Snow-Coverend Swamp": {"mana": "B", "tags": {"Snow"}},
    "Snow-Coverend Island": {"mana": "U", "tags": {"Snow"}},
    "Snow-Coverend Forest": {"mana": "G", "tags": {"Snow"}},
    "Snow-Coverend Plains": {"mana": "W", "tags": {"Snow"}},

    # Artifact Mono
    "Ancient Den": {"mana": "W", "tags": {"artifact"}},
    "Seat of the Synod": {"mana": "U", "tags": {"artifact"}},
    "Vault of Whispers": {"mana": "B", "tags": {"artifact"}},
    "Great Furnace": {"mana": "R", "tags": {"artifact"}},
    "Tree of Tales": {"mana": "G", "tags": {"artifact"}},

    # The Colorless Artifact Lands
    "Darksteel Citadel": {"mana": "C", "tags": {"artifact", "indestructible"}},
    "Treasure Vault": {"mana": "C", "tags": {"artifact", "treasure", "sacrifice"}},

    "Abandoned Campground": {"mana": "RG", "tags": {"dual", "surveil", "tapped"}},
    "Bleeding Woods": {"mana": "BG", "tags": {"dual", "surveil", "tapped"}},
    "Etched Cornfield": {"mana": "GW", "tags": {"dual", "surveil", "tapped"}},
    "Lakeside Shack": {"mana": "UG", "tags": {"dual", "surveil", "tapped"}},
    "Murky Sewer": {"mana": "UB", "tags": {"dual", "surveil", "tapped"}},
    "Neglected Manor": {"mana": "WU", "tags": {"dual", "surveil", "tapped"}},
    "Peculiar Lighthouse": {"mana": "UR", "tags": {"dual", "surveil", "tapped"}},
    "Raucous Carnival": {"mana": "BR", "tags": {"dual", "surveil", "tapped"}},
    "Razortrap Gorge": {"mana": "RW", "tags": {"dual", "surveil", "tapped"}},
    "Strangled Cemetery": {"mana": "WB", "tags": {"dual", "surveil", "tapped"}},

    # Artifact Dual Bridges
    "Darkmoss Bridge": {"mana": "BG", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Drossforge Bridge": {"mana": "BR", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Goldmire Bridge": {"mana": "WB", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Mistvault Bridge": {"mana": "UB", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Razortide Bridge": {"mana": "WU", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Rustvale Bridge": {"mana": "RW", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Silverbluff Bridge": {"mana": "UR", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Slagwoods Bridge": {"mana": "RG", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Tanglepool Bridge": {"mana": "UG", "tags": {"dual", "artifact", "indestructible", "tapped"}},
    "Thornglint Bridge": {"mana": "GW", "tags": {"dual", "artifact", "indestructible", "tapped"}},

    # Life-Gain Duals (M21/Kaldheim/Khans - Commons)
    "Bloodfell Caves": {"mana": "BR", "tags": {"dual", "lifegain", "tapped"}},
    "Blossoming Sands": {"mana": "GW", "tags": {"dual", "lifegain", "tapped"}},
    "Dismal Backwater": {"mana": "UB", "tags": {"dual", "lifegain", "tapped"}},
    "Jungle Hollow": {"mana": "BG", "tags": {"dual", "lifegain", "tapped"}},
    "Rugged Highlands": {"mana": "RG", "tags": {"dual", "lifegain", "tapped"}},
    "Scoured Barrens": {"mana": "WB", "tags": {"dual", "lifegain", "tapped"}},
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
    "Orzhov Basilica": {"mana": "WB", "tags": {"dual", "bounce", "tapped"}},
    "Rakdos Carnarium": {"mana": "BR", "tags": {"dual", "bounce", "tapped"}},
    "Selesnya Sanctuary": {"mana": "GW", "tags": {"dual", "bounce", "tapped"}},
    "Simic Growth Chamber": {"mana": "UG", "tags": {"dual", "bounce", "tapped"}},

    # Strixhaven Campuses
    "Lorehold Campus": {"mana": "RW", "tags": {"Dual", "scry"}},
    "Prismari Campus": {"mana": "UR", "tags": {"Dual", "scry"}},
    "Quandrix Campus": {"mana": "UG", "tags": {"Dual", "scry"}},
    "Silverquill Campus": {"mana": "BW", "tags": {"Dual", "scry"}},
    "Witherbloom Campus": {"mana": "BG", "tags": {"Dual", "scry"}},

    # Dual Desert Pingers
    "Abraded Bluffs": {"mana": "RW", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Bristling Backwoods": {"mana": "RG", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Creosote Heath": {"mana": "GW", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Eroded Canyon": {"mana": "UR", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Festering Gulch": {"mana": "BG", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Forlorn Flats": {"mana": "WB", "tags": {"dual", "desert", "pinger", "tapped"}},
    "Jagged Barrens": {"mana": "BR", "tags": {"dual", "desert", "pinger", "tapped"}},
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
    "Raucous Carnival": {"mana": "BR", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Razortrap Gorge": {"mana": "RW", "tags": {"dual", "life_check", "conditional_tapped"}},
    "Strangled Cemetery": {"mana": "WB", "tags": {"dual", "life_check", "conditional_tapped"}},

    # Horizon Dual Sac Draw
    "Horizon Canopy": {"mana": "GW", "tags": {"pain", "dual", "draw", "sacrifice"}},
    "Fiery Islet": {"mana": "UR", "tags": {"pain", "dual", "draw", "sacrifice"}},
    "Nurturing Peatland": {"mana": "BG", "tags": {"pain", "dual", "draw", "sacrifice"}},
    "Silent Clearing": {"mana": "WB", "tags": {"pain", "dual", "draw", "sacrifice"}},
    "Sunbaked Canyon": {"mana": "RW", "tags": {"pain", "dual", "draw", "sacrifice"}},
    "Waterlogged Grove": {"mana": "UG", "tags": {"pain", "dual", "draw", "sacrifice"}},

    # Guildgates
    "Azorius Guildgate": {"mana": "WU", "tags": {"dual", "gate", "tapped"}},
    "Boros Guildgate": {"mana": "RW", "tags": {"dual", "gate", "tapped"}},
    "Dimir Guildgate": {"mana": "UB", "tags": {"dual", "gate", "tapped"}},
    "Golgari Guildgate": {"mana": "BG", "tags": {"dual", "gate", "tapped"}},
    "Gruul Guildgate": {"mana": "RG", "tags": {"dual", "gate", "tapped"}},
    "Izzet Guildgate": {"mana": "UR", "tags": {"dual", "gate", "tapped"}},
    "Orzhov Guildgate": {"mana": "WB", "tags": {"dual", "gate", "tapped"}},
    "Rakdos Guildgate": {"mana": "BR", "tags": {"dual", "gate", "tapped"}},
    "Selesnya Guildgate": {"mana": "GW", "tags": {"dual", "gate", "tapped"}},
    "Simic Guildgate": {"mana": "UG", "tags": {"dual", "gate", "tapped"}},

    # Dual Choice Gates
    "Citadel Gate": {"mana": "W", "tags": {"gate", "dual", "choice", "tapped"}},
    "Sea Gate": {"mana": "U", "tags": {"gate", "dual", "choice", "tapped"}},
    "Black Dragon Gate": {"mana": "B", "tags": {"gate", "dual", "choice", "tapped"}},
    "Cliffgate": {"mana": "R", "tags": {"gate", "dual", "choice", "tapped"}},
    "Manor Gate": {"mana": "G", "tags": {"gate", "dual", "choice", "tapped"}},

    # Avatar Duals Sac Draw
    "Foggy Bottom Swamp": {"mana": "BG", "tags": {"dual", "draw", "sacrifice"}},
    "Airship Engine Room": {"mana": "UR", "tags": {"dual", "draw", "sacrifice"}},
    "Boiling Rock Prison": {"mana": "BR", "tags": {"dual", "draw", "sacrifice"}},
    "Kyoshi Village": {"mana": "GW", "tags": {"dual", "draw", "sacrifice"}},
    "Misty Palms Oasis": {"mana": "BW", "tags": {"dual", "draw", "sacrifice"}},
    "Meditation Pools": {"mana": "UG", "tags": {"dual", "draw", "sacrifice"}},
    "North Pole Gates": {"mana": "UW", "tags": {"dual", "draw", "sacrifice"}},
    "Omashu City": {"mana": "RG", "tags": {"dual", "draw", "sacrifice"}},
    "Serpent's Pass": {"mana": "UB", "tags": {"dual", "draw", "sacrifice"}},
    "Sub-blessed Peak": {"mana": "RW", "tags": {"dual", "draw", "sacrifice"}},

    # Avatar Scry Fix
    "Rumble Arena": {"mana": "C", "tags": {"scry", "etb", "fixer"}},

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
    "Halimar Depths": {"mana": "U", "tags": {"etb", "top-deck", "tapped"}},
    "Khalni Garden": {"mana": "G", "tags": {"etb", "token", "tapped"}},
    "Smoldering Spires": {"mana": "R", "tags": {"etb", "combat", "tapped"}},
    "Sejiri Steppe": {"mana": "W", "tags": {"etb", "protection", "tapped"}},

    # Zendikar Rising Mono ETB tapped
    # "Kabira Crossroads": {"mana": "W", "tags": {"mono", "etb", "lifegain", "tapped"}},
    "Skyline Cascade": {"mana": "U", "tags": {"etb", "freeze", "tapped"}},
    "Mortuary Mire": {"mana": "B", "tags": {"etb", "recursion", "tapped"}},
    "Looming Spires": {"mana": "R", "tags": {"etb", "buff", "tapped"}},
    "Fertile Thicket": {"mana": "G", "tags": {"etb", "fixer", "tapped"}},

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
    "Ash Barrens": {"mana": "C", "tags": {"fetch", "fixer", "cycler", "basic_land_cycler"}},

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
    "Terramorphic Expanse": {"mana": "C", "tags": {"fetch", "fixer", "tapped"}},
    "Evolving Wilds": {"mana": "C", "tags": {"fetch", "fixer", "tapped"}},
    "Warped Landscape": {"mana": "C", "tags": {"fetch", "fixer", "utility"}},

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
    "Ancient Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Bountiful Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Contaminated Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Deceptive Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Foreboding Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Perilous Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}}, # 4-color fetch
    "Seething Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Sheltering Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Tranquil Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},
    "Twisted Landscape": {"mana": "C", "tags": {"landscape", "fetch", "cycler", "pure_cycler"}},

    # New Capenna Fetch Lifegain
    "Brokers Hideout": {"mana": "GWU", "tags": {"fetch", "lifegain"}},
    "Obscura Storefront": {"mana": "WUB", "tags": {"fetch", "lifegain"}},
    "Maestros Theater": {"mana": "UBR", "tags": {"fetch", "lifegain"}},
    "Riveteers Overlook": {"mana": "BRG", "tags": {"fetch", "lifegain"}},
    "Cabaretti Courtyard": {"mana": "RGW", "tags": {"fetch", "lifegain"}},

    # TTron Lands
    "Urza's Mine": {"mana": "C", "tags": {"tron", "ramp"}},
    "Urza's Power Plant": {"mana": "C", "tags": {"tron", "ramp"}},
    "Urza's Tower": {"mana": "C", "tags": {"tron", "ramp"}},

    # The Castles (Eldraine - Rares)
    "Castle Ardenvale": {"mana": "W", "tags": {"utility", "castle", "token"}},
    "Castle Vantress": {"mana": "U", "tags": {"utility", "castle", "scy"}},
    "Castle Locthwain": {"mana": "B", "tags": {"utility", "castle", "draw"}},
    "Castle Embereth": {"mana": "R", "tags": {"utility", "castle", "buff"}},
    "Castle Garenbrig": {"mana": "G", "tags": {"utility", "castle", "ramp"}},
}