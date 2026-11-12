import math
import random

from . import data


class Module:
    def __init__(self, kind):
        self.kind = kind
        self.level = 1
        self.damaged = False

    @property
    def spec(self):
        return data.MODULES[self.kind]

    @property
    def strength(self):
        return 0.5 if self.damaged else 1.0

    def upgrade_cost(self):
        return int(self.spec["cost"] * (0.8 + 0.4 * self.level))

    def can_upgrade(self):
        return self.level < self.spec["max"]


class Astronaut:
    def __init__(self, name):
        self.name = name
        self.health = 100.0
        self.alive = True


class Outpost:
    def __init__(self, planet_key, rng=None, easy=False):
        self.rng = rng or random.Random()
        self.easy = easy
        mode = data.EASY if easy else {}
        self.use_mul = mode.get("use", 1.0)
        self.flare_mul = mode.get("flare_scale", 1.0)
        self.flare_classes = mode.get("flare_classes", ["C", "M", "M", "X", "X"])
        self.warning = mode.get("warning", data.FLARE_WARNING)
        self.dust_level = mode.get("dust", 0.2)
        self.meteor_mul = mode.get("meteors", 1.0)
        self.heat_mul = mode.get("heat", 1.0)
        self.harm_mul = mode.get("harm", 1.0)
        self.supply = mode.get("supply", data.SUPPLY_POINTS)
        self.key = planet_key
        self.planet = data.PLANETS[planet_key]
        self.end_hour = data.MISSION_DAYS * 24
        self.hour = 0
        self.crew = [Astronaut(n) for n in data.CREW_NAMES]
        self.slots = [None] * data.SLOT_COUNT
        for index, kind in data.STARTING_LAYOUT.items():
            self.slots[index] = Module(kind)

        self.oxygen = mode.get("oxygen", 170.0)
        self.water = mode.get("water", 220.0)
        self.food = mode.get("food", 240.0)
        self.battery = mode.get("battery", 80.0)
        self.points = mode.get("points", data.START_POINTS)
        self.dose = 0.0

        self.priority = list(data.PRIORITY_DEFAULT)
        self.enabled = {key: True for key in self.priority}
        self.eff = {key: 1.0 for key in self.priority}
        self.demand_now = {key: 0.0 for key in self.priority}
        self.production = 0.0
        self.used = 0.0
        self.sheltering = False

        self.log = []
        self.alert_flag = False
        self.finished = False
        self.outcome = None
        self.cause_of_loss = []
        self.stats = {"blackout_hours": 0, "shelter_hours": 0, "cold_hours": 0, "flares_survived": 0}
        self._noted = {}

        self._plan_events()
        self._refresh_power()
        self.say("Mission start. Read the Sun Watch and keep the lights on.", "info")

    def _plan_events(self):
        classes = list(self.flare_classes)
        self.rng.shuffle(classes)
        times = []
        while len(times) < len(classes):
            t = self.rng.randint(30, self.end_hour - 30)
            if all(abs(t - other) >= 40 for other in times):
                times.append(t)
        times.sort()
        self.flares = []
        for start, cls in zip(times, classes):
            self.flares.append({
                "start": start,
                "cls": cls,
                "dose": data.FLARE_DOSE[cls] * self.planet["flare_scale"] * self.flare_mul,
                "watched": False,
                "warned": False,
            })
        self.storms = []
        for low, high in self.planet["storm_windows"]:
            self.storms.append({"start": self.rng.randint(low, high), "length": 60, "warned": False})
        self.meteor_hours = set(self.rng.sample(range(20, self.end_hour - 10), max(1, int(self.planet["meteors"] * self.meteor_mul))))

    def say(self, text, level="info"):
        self.log.append((self.hour, text, level))
        if level == "alert":
            self.alert_flag = True

    def note(self, key, text, level="warn", gap=12):
        last = self._noted.get(key)
        if last is None or self.hour - last >= gap:
            self._noted[key] = self.hour
            self.say(text, level)

    def take_alert(self):
        flag = self.alert_flag
        self.alert_flag = False
        return flag

    def phase(self):
        return (self.hour + self.planet["start_phase"]) % self.planet["cycle"]

    def sunlight(self):
        p = self.phase()
        span = self.planet["sun_hours"]
        if p >= span:
            return 0.0
        return math.sin(math.pi * p / span)

    def hours_to_dusk(self):
        p = self.phase()
        span = self.planet["sun_hours"]
        if p < span:
            return span - p
        return 0

    def is_day(self):
        return self.phase() < self.planet["sun_hours"]

    def storm_active(self):
        for storm in self.storms:
            if storm["start"] <= self.hour < storm["start"] + storm["length"]:
                return storm
        return None

    def dust_factor(self):
        return self.dust_level if self.storm_active() else 1.0

    def flare_active(self):
        for flare in self.flares:
            if flare["start"] <= self.hour < flare["start"] + data.FLARE_HOURS:
                return flare
        return None

    def flare_incoming(self):
        for flare in self.flares:
            lead = flare["start"] - self.hour
            if 0 < lead <= self.warning:
                return flare, lead
        return None

    def sun_status(self):
        active = self.flare_active()
        if active:
            return "FLARE ACTIVE: %s-class" % active["cls"], "alert"
        incoming = self.flare_incoming()
        if incoming:
            flare, lead = incoming
            return "%s-class flare in %d h" % (flare["cls"], lead), "alert"
        for flare in self.flares:
            lead = flare["start"] - self.hour
            if 0 < lead <= 30:
                return "Sunspots growing, flare likely", "warn"
        return "Sun is calm", "good"

    def capacity(self, kind):
        return sum(m.level * m.strength for m in self.slots if m and m.kind == kind)

    def levels(self, kind):
        return sum(m.level for m in self.slots if m and m.kind == kind)

    def battery_cap(self):
        return data.BASE_BATTERY + data.BATTERY_PER_LEVEL * self.capacity("battery")

    def heat_load(self):
        day, night = self.planet["heat"]
        cold = 1.0 - min(1.0, self.sunlight() * 3.0)
        return (day + (night - day) * cold) * self.heat_mul

    def demand(self, key):
        if key == "heat":
            return self.heat_load()
        if key == "oxygen":
            return data.OXYGEN_DEMAND * self.levels("oxygen")
        if key == "water":
            if self.sheltering:
                return 0.0
            return data.WATER_DEMAND * self.levels("miner")
        return data.FOOD_DEMAND * self.levels("farm")

    def solar_output(self):
        return data.SOLAR_KW * self.capacity("solar") * self.sunlight() * self.planet["solar_peak"] * self.dust_factor()

    def _refresh_power(self):
        self.production = self.solar_output() + data.REACTOR_KW * self.capacity("reactor")
        for key in self.priority:
            self.demand_now[key] = self.demand(key) if self.enabled[key] else 0.0

    def radiation_rate(self):
        rate = self.planet["bg_dose"] / 24.0
        flare = self.flare_active()
        if flare:
            rate += flare["dose"] / data.FLARE_HOURS
        multiplier = data.SHIELD_STEP ** min(self.capacity("shield"), 5)
        if self.sheltering:
            has_bunker = any(m and m.kind == "shelter" and not m.damaged for m in self.slots)
            multiplier *= data.SHELTER_BUNKER if has_bunker else data.SHELTER_PLAIN
        return rate * multiplier

    def _events(self):
        for flare in self.flares:
            lead = flare["start"] - self.hour
            if not flare["watched"] and 0 < lead <= 30:
                flare["watched"] = True
                self.say("Sun Watch: a big sunspot group is growing. A flare may come within a day.", "warn")
            if not flare["warned"] and 0 < lead <= self.warning:
                flare["warned"] = True
                self.say("%s-class flare inbound in %d hours! Press S to shelter the crew." % (flare["cls"], lead), "alert")
            if lead == 0:
                self.say("Flare particles are arriving now.", "alert")
            if lead == -data.FLARE_HOURS:
                self.stats["flares_survived"] += 1
                self.say("The flare has passed. Dose so far: %.0f mSv." % self.dose, "good")
        for storm in self.storms:
            lead = storm["start"] - self.hour
            if not storm["warned"] and 0 < lead <= 12:
                storm["warned"] = True
                self.say("Dust storm forecast in %d hours. Solar power will drop by 80%%." % lead, "alert")
            if lead == 0:
                self.say("The dust storm has arrived. Panels are almost blind.", "alert")
            if lead == -storm["length"]:
                self.say("The dust storm is clearing. Sunlight is back.", "good")
        if self.hour in self.meteor_hours:
            targets = [m for m in self.slots if m and not m.damaged]
            if targets:
                hit = self.rng.choice(targets)
                hit.damaged = True
                self.say("Micrometeorite hit the %s! It runs at half power until repaired." % hit.spec["name"], "alert")
            else:
                self.say("A micrometeorite missed the outpost.", "info")
        if self.hour > 0 and self.hour % data.SUPPLY_EVERY == 0:
            self.points += self.supply
            self.say("Supply drop from Earth: +%d Build Points." % self.supply, "good")

    def step(self):
        if self.finished:
            return
        self.hour += 1
        self._events()
        alive = [a for a in self.crew if a.alive]
        count = len(alive)

        self._refresh_power()
        available = self.production + self.battery
        base = min(data.BASE_LOAD, available)
        available -= base
        granted_total = base
        short = base < data.BASE_LOAD
        for key in self.priority:
            want = self.demand_now[key]
            if want <= 0:
                self.eff[key] = 1.0 if self.enabled[key] else 0.0
                continue
            got = min(want, available)
            available -= got
            granted_total += got
            self.eff[key] = got / want
            if got < want:
                short = True
        self.used = granted_total
        cap = self.battery_cap()
        self.battery = max(0.0, min(cap, self.battery + self.production - granted_total))
        if short:
            self.stats["blackout_hours"] += 1
            self.note("blackout", "Power shortage! Low-priority systems are shutting down. Add generation or batteries.", "alert", 8)

        wet = 1.0 if self.water > 0 else 0.0
        eff_o = self.eff["oxygen"] * wet
        eff_f = self.eff["food"] * wet
        eff_w = self.eff["water"]
        self.oxygen += data.OXYGEN_RATE * self.capacity("oxygen") * eff_o
        self.oxygen += data.FARM_OXYGEN * self.capacity("farm") * eff_f
        self.food += data.FARM_FOOD * self.capacity("farm") * eff_f
        self.water += data.MINER_RATE * self.capacity("miner") * eff_w
        self.water -= data.OXYGEN_WATER_USE * self.capacity("oxygen") * eff_o
        self.water -= data.FARM_WATER_USE * self.capacity("farm") * eff_f

        self.oxygen -= count * data.CREW_OXYGEN * self.use_mul
        self.water -= count * data.CREW_WATER * self.use_mul
        self.food -= count * data.CREW_FOOD * self.use_mul
        no_air = self.oxygen <= 0
        no_water = self.water <= 0
        no_food = self.food <= 0
        self.oxygen = max(0.0, min(data.OXYGEN_CAP, self.oxygen))
        self.water = max(0.0, min(data.WATER_CAP, self.water))
        self.food = max(0.0, min(data.FOOD_CAP, self.food))

        if self.sheltering:
            self.stats["shelter_hours"] += 1
        self.dose += self.radiation_rate()

        harm = {}
        if no_air:
            harm["suffocation"] = 6.0
            self.note("air", "OUT OF OXYGEN! The crew is suffocating.", "alert", 4)
        if no_water:
            harm["dehydration"] = 1.5
            self.note("thirst", "Water tanks are empty. Crew health is falling.", "alert", 6)
        if no_food:
            harm["starvation"] = 0.5
            self.note("hunger", "The food store is empty.", "alert", 12)
        cold_gap = 0.7 - self.eff["heat"]
        if cold_gap > 0:
            harm["cold"] = cold_gap * 4.0
            self.stats["cold_hours"] += 1
            self.note("cold", "The habitat is freezing because heating has no power.", "alert", 8)
        if self.dose > data.DOSE_LIMIT:
            harm["radiation sickness"] = 0.4 if self.dose < data.DOSE_LIMIT * 1.4 else 1.5
            self.note("dose", "Radiation dose is above the safe limit. The crew is getting sick.", "alert", 12)
        elif self.dose > data.DOSE_LIMIT * 0.75:
            self.note("dosewarn", "Radiation dose is at %.0f mSv. Build shielding or shelter during flares." % self.dose, "warn", 24)

        if self.oxygen < data.OXYGEN_CAP * 0.2 and not no_air:
            self.note("lowair", "Oxygen is running low.", "warn", 12)
        if self.water < data.WATER_CAP * 0.15 and not no_water:
            self.note("lowwater", "Water is running low. Ice miners or fewer consumers needed.", "warn", 12)
        if self.food < data.FOOD_CAP * 0.15 and not no_food:
            self.note("lowfood", "Food is running low. Greenhouses need power and water.", "warn", 12)

        total_harm = sum(harm.values()) * self.harm_mul
        for astro in alive:
            if total_harm > 0:
                astro.health -= total_harm
            else:
                astro.health = min(100.0, astro.health + 0.15)
            if astro.health <= 0:
                astro.health = 0.0
                astro.alive = False
                worst = max(harm, key=harm.get) if harm else "injuries"
                self.cause_of_loss.append(worst)
                self.say("%s died from %s." % (astro.name, worst), "alert")

        if not any(a.alive for a in self.crew):
            self.finish("lost")
        elif self.hour >= self.end_hour:
            self.finish("won")

    def finish(self, outcome):
        self.finished = True
        self.outcome = outcome

    def alive_count(self):
        return sum(1 for a in self.crew if a.alive)

    def average_health(self):
        living = [a.health for a in self.crew if a.alive]
        return sum(living) / len(living) if living else 0.0

    def stars(self):
        alive = self.alive_count()
        if alive == 0:
            return 0
        if alive == len(self.crew) and self.dose <= data.DOSE_LIMIT and self.average_health() >= 70:
            return 3
        if alive >= 3:
            return 2
        return 1

    def build(self, slot, kind):
        cost = data.MODULES[kind]["cost"]
        if self.slots[slot] is not None or self.points < cost:
            return False
        self.points -= cost
        self.slots[slot] = Module(kind)
        self.say("Built %s." % data.MODULES[kind]["name"], "good")
        return True

    def upgrade(self, slot):
        module = self.slots[slot]
        if module is None or not module.can_upgrade():
            return False
        cost = module.upgrade_cost()
        if self.points < cost:
            return False
        self.points -= cost
        module.level += 1
        self.say("Upgraded %s to level %d." % (module.spec["name"], module.level), "good")
        return True

    def repair(self, slot):
        module = self.slots[slot]
        if module is None or not module.damaged or self.points < data.REPAIR_COST:
            return False
        self.points -= data.REPAIR_COST
        module.damaged = False
        self.say("Repaired %s." % module.spec["name"], "good")
        return True

    def demolish(self, slot):
        module = self.slots[slot]
        if module is None:
            return False
        refund = module.spec["cost"] // 2
        self.points += refund
        self.slots[slot] = None
        self.say("Recycled %s for %d points." % (module.spec["name"], refund), "info")
        return True

    def move_priority(self, key, step):
        i = self.priority.index(key)
        j = i + step
        if 0 <= j < len(self.priority):
            self.priority[i], self.priority[j] = self.priority[j], self.priority[i]

    def toggle_system(self, key):
        self.enabled[key] = not self.enabled[key]

    def toggle_shelter(self):
        self.sheltering = not self.sheltering
        if self.sheltering:
            self.say("Crew moved into shelter. Ice mining paused.", "info")
        else:
            self.say("Crew back outside. Ice mining resumes.", "info")

    def describe(self, module):
        lvl = module.level
        cap = lvl * module.strength
        kind = module.kind
        if kind == "solar":
            return "Up to %.0f kW in full sun." % (data.SOLAR_KW * cap * self.planet["solar_peak"])
        if kind == "battery":
            return "Holds %.0f kW-hours." % (data.BATTERY_PER_LEVEL * cap)
        if kind == "oxygen":
            return "Makes %.1f oxygen per hour, uses %.0f kW." % (data.OXYGEN_RATE * cap, data.OXYGEN_DEMAND * lvl)
        if kind == "miner":
            return "Digs %.1f water per hour, uses %.0f kW." % (data.MINER_RATE * cap, data.WATER_DEMAND * lvl)
        if kind == "farm":
            return "Grows %.1f food per hour, uses %.0f kW." % (data.FARM_FOOD * cap, data.FOOD_DEMAND * lvl)
        if kind == "shield":
            return "Total dose multiplier: x%.2f." % (data.SHIELD_STEP ** min(self.capacity("shield"), 5))
        if kind == "reactor":
            return "Makes %.0f kW all the time." % (data.REACTOR_KW * cap)
        return "Sheltering dose multiplier: x%.1f." % data.SHELTER_BUNKER

    def report(self):
        lines = []
        if self.outcome == "won":
            lines.append("You kept the outpost alive for %d days." % data.MISSION_DAYS)
        else:
            reasons = ", ".join(sorted(set(self.cause_of_loss))) or "unknown causes"
            lines.append("The crew was lost to %s." % reasons)
        if self.dose > data.DOSE_LIMIT:
            lines.append("Radiation: %.0f mSv is over the limit. More regolith shields or timely sheltering would have helped." % self.dose)
        else:
            lines.append("Radiation: %.0f mSv stayed under the %.0f mSv limit." % (self.dose, data.DOSE_LIMIT))
        if self.stats["blackout_hours"] > 20:
            lines.append("Power: %d hours had shortages. Real outposts size batteries for the darkest night." % self.stats["blackout_hours"])
        else:
            lines.append("Power: only %d hours with shortages. Good balance of generation and storage." % self.stats["blackout_hours"])
        if self.stats["cold_hours"] > 0:
            lines.append("Cold: heating failed for %d hours. Heating should stay high on your priority list." % self.stats["cold_hours"])
        lines.append("Flares survived: %d. Hours spent sheltering: %d." % (self.stats["flares_survived"], self.stats["shelter_hours"]))
        return lines
