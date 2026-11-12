WIDTH = 1180
HEIGHT = 720

MISSION_DAYS = 20
DOSE_LIMIT = 100.0
SLOT_COUNT = 10
HABITAT_POSITION = 5

CREW_NAMES = ["Amira", "Tomas", "Lena", "Kofi"]

OXYGEN_CAP = 220.0
WATER_CAP = 320.0
FOOD_CAP = 320.0
BASE_BATTERY = 100.0
BATTERY_PER_LEVEL = 120.0

BASE_LOAD = 2.0
SOLAR_KW = 20.0
REACTOR_KW = 12.0
OXYGEN_DEMAND = 5.0
WATER_DEMAND = 6.0
FOOD_DEMAND = 7.0

OXYGEN_RATE = 2.5
OXYGEN_WATER_USE = 0.6
MINER_RATE = 2.4
FARM_FOOD = 0.8
FARM_OXYGEN = 0.3
FARM_WATER_USE = 0.5

CREW_OXYGEN = 0.5
CREW_WATER = 0.4
CREW_FOOD = 0.35

SHIELD_STEP = 0.65
SHELTER_PLAIN = 0.5
SHELTER_BUNKER = 0.1

FLARE_HOURS = 6
FLARE_WARNING = 6
FLARE_DOSE = {"C": 6.0, "M": 18.0, "X": 45.0}

SUPPLY_EVERY = 72
SUPPLY_POINTS = 45
START_POINTS = 70
REPAIR_COST = 6

STEP_SECONDS = 0.5

EASY = {
    "use": 0.6,
    "points": 130,
    "supply": 70,
    "flare_scale": 0.5,
    "flare_classes": ["C", "M", "X"],
    "warning": 10,
    "dust": 0.5,
    "meteors": 0.5,
    "heat": 0.7,
    "harm": 0.5,
    "oxygen": 200.0,
    "water": 280.0,
    "food": 290.0,
    "battery": 160.0,
}

PRIORITY_DEFAULT = ["heat", "oxygen", "water", "food"]

SYSTEM_NAMES = {
    "heat": "Habitat Heating",
    "oxygen": "Oxygen Generators",
    "water": "Ice Miners",
    "food": "Greenhouses",
}

STARTING_LAYOUT = {1: "solar", 2: "solar", 3: "battery", 4: "oxygen", 6: "miner", 7: "farm"}

MODULE_ORDER = ["solar", "battery", "oxygen", "miner", "farm", "shield", "reactor", "shelter"]

MODULES = {
    "solar": {
        "name": "Solar Array",
        "cost": 20,
        "max": 3,
        "blurb": "Turns sunlight into power. Useless at night and weak in dust storms.",
    },
    "battery": {
        "name": "Battery Bank",
        "cost": 15,
        "max": 3,
        "blurb": "Stores spare daytime power for the night. It only holds what you already made.",
    },
    "oxygen": {
        "name": "Oxygen Generator",
        "cost": 25,
        "max": 3,
        "blurb": "Splits water into air to breathe. Needs power and uses up water.",
    },
    "miner": {
        "name": "Ice Miner",
        "cost": 25,
        "max": 3,
        "blurb": "Digs up ice for water. Crew work outside, so it stops during flare shelter.",
    },
    "farm": {
        "name": "Greenhouse",
        "cost": 30,
        "max": 3,
        "blurb": "Grows food and a little oxygen. Needs grow-light power and water.",
    },
    "shield": {
        "name": "Regolith Shield",
        "cost": 20,
        "max": 3,
        "blurb": "Piles of soil soak up radiation. No power needed. Each level cuts dose by 35%.",
    },
    "reactor": {
        "name": "Fission Reactor",
        "cost": 60,
        "max": 3,
        "blurb": "Steady power day and night, but very expensive.",
    },
    "shelter": {
        "name": "Storm Shelter",
        "cost": 25,
        "max": 1,
        "blurb": "Thick-walled cellar. Sheltering inside blocks almost all flare radiation.",
    },
}

MODULE_COLORS = {
    "solar": (60, 120, 230),
    "battery": (90, 200, 110),
    "oxygen": (150, 210, 245),
    "miner": (235, 150, 60),
    "farm": (80, 190, 90),
    "shield": (150, 140, 130),
    "reactor": (235, 210, 80),
    "shelter": (120, 120, 150),
}

PLANETS = {
    "moon": {
        "name": "The Moon",
        "site": "Shackleton Crater Rim",
        "cycle": 72,
        "sun_hours": 48,
        "start_phase": 8,
        "solar_peak": 1.0,
        "bg_dose": 3.0,
        "flare_scale": 1.0,
        "heat": (2.0, 5.0),
        "storm_windows": [],
        "meteors": 6,
        "sky": (3, 3, 8),
        "ground": (150, 148, 145),
        "level": "Medium",
        "challenge": "Long nights: 24 hours of darkness in every 72-hour cycle.",
        "facts": [
            "No air and no magnetic field, so flares hit at full strength.",
            "One lunar day-night cycle takes about 29.5 Earth days. Here it is shortened to 3 days so you can play it.",
            "Sunlight is strong and steady, but the night is very cold.",
        ],
    },
    "mars": {
        "name": "Mars",
        "site": "Jezero Crater",
        "cycle": 24,
        "sun_hours": 13,
        "start_phase": 3,
        "solar_peak": 0.65,
        "bg_dose": 2.0,
        "flare_scale": 0.45,
        "heat": (3.5, 8.0),
        "storm_windows": [(70, 170), (260, 380)],
        "meteors": 3,
        "sky": (196, 120, 88),
        "ground": (176, 98, 62),
        "level": "Hard",
        "challenge": "Weak sunlight, freezing nights, and dust storms that block the Sun for days.",
        "facts": [
            "Mars is farther from the Sun, so panels make only about half the power they would on the Moon.",
            "A thin atmosphere and dust soften flare radiation, but not by much.",
            "Dust storms can cover the whole planet and last for weeks.",
        ],
    },
}

HELP_LINES = [
    "YOUR JOB: keep 4 astronauts alive for 20 days.",
    "",
    "Click an empty slot to build. Click a module to upgrade or repair it.",
    "You earn Build Points from supply drops every 3 days. Spend them wisely.",
    "",
    "POWER: Solar panels only work in daylight. Batteries save power for the night.",
    "If power runs short, the Priority Program decides who goes dark first.",
    "Use the arrows to reorder systems, or switch one off on purpose.",
    "",
    "THE SUN: It powers you, but it also sends solar flares.",
    "Sun Watch warns you hours ahead. Press S to send the crew to shelter.",
    "Shelter is safer, but the ice miners must stop working.",
    "",
    "RADIATION: Dose builds up all mission long. Shields lower it all the time.",
    "Above 100 mSv the crew start to get sick.",
    "",
    "KEYS: SPACE pause   1 2 3 speed   S shelter   H help   ESC back",
]
