import math
import random

import pygame

from . import data

W = data.WIDTH
H = data.HEIGHT
SCENE_TOP = 48
HORIZON = 330
GROUND_BOTTOM = 388
PANEL_TOP = 396

INK = (232, 238, 248)
MUTED = (150, 165, 190)
PANEL = (16, 22, 36)
PANEL_EDGE = (52, 70, 104)
GOOD = (110, 225, 140)
WARN = (255, 200, 90)
ALERT = (255, 100, 95)
LOG_COLORS = {"info": (170, 190, 215), "warn": WARN, "alert": ALERT, "good": GOOD}


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dim(color, k):
    return tuple(max(0, min(255, int(v * k))) for v in color)


def slot_x(index):
    position = index if index < data.HABITAT_POSITION else index + 1
    return 62 + position * 106


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.huge = pygame.font.Font(None, 72)
        self.big = pygame.font.Font(None, 44)
        self.mid = pygame.font.Font(None, 28)
        self.small = pygame.font.Font(None, 22)
        self.tiny = pygame.font.Font(None, 19)
        self.hits = []
        rng = random.Random(7)
        self.stars = [(rng.randrange(W), rng.randrange(SCENE_TOP, HORIZON), rng.random()) for _ in range(140)]
        self.hills = {}
        self.craters = {}
        for key in data.PLANETS:
            hill_rng = random.Random(key)
            points = [(0, HORIZON)]
            x = 0
            while x < W:
                x += hill_rng.randint(40, 90)
                points.append((x, HORIZON - hill_rng.randint(6, 34)))
            points.append((W, HORIZON))
            self.hills[key] = points
            self.craters[key] = [
                (hill_rng.randrange(W), hill_rng.randint(HORIZON + 30, GROUND_BOTTOM - 4), hill_rng.randint(8, 26))
                for _ in range(16)
            ]

    def text(self, font, s, pos, color=INK, anchor="topleft"):
        img = font.render(s, True, color)
        rect = img.get_rect(**{anchor: pos})
        self.screen.blit(img, rect)
        return rect

    def wrap(self, font, s, width):
        lines = []
        line = ""
        for word in s.split():
            trial = (line + " " + word).strip()
            if font.size(trial)[0] <= width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def button(self, rect, label, action, enabled=True, color=(38, 60, 100), font=None, active=False):
        rect = pygame.Rect(rect)
        hover = enabled and rect.collidepoint(pygame.mouse.get_pos())
        base = color if enabled else (36, 40, 48)
        if active:
            base = mix(base, (255, 255, 255), 0.22)
        if hover:
            base = mix(base, (255, 255, 255), 0.14)
        pygame.draw.rect(self.screen, base, rect, border_radius=8)
        edge = (130, 165, 220) if enabled else (66, 70, 80)
        pygame.draw.rect(self.screen, edge, rect, 2, border_radius=8)
        self.text(font or self.small, label, rect.center, INK if enabled else (110, 114, 124), "center")
        if enabled:
            self.hits.append((rect, action))

    def panel(self, rect, title):
        rect = pygame.Rect(rect)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=10)
        pygame.draw.rect(self.screen, PANEL_EDGE, rect, 2, border_radius=10)
        self.text(self.small, title, (rect.x + 14, rect.y + 8), MUTED)

    def bar(self, rect, fraction, color, marker=None):
        rect = pygame.Rect(rect)
        fraction = max(0.0, min(1.0, fraction))
        pygame.draw.rect(self.screen, (34, 42, 60), rect, border_radius=5)
        if fraction > 0:
            fill = pygame.Rect(rect.x, rect.y, max(4, int(rect.w * fraction)), rect.h)
            pygame.draw.rect(self.screen, color, fill, border_radius=5)
        if marker is not None:
            mx = rect.x + int(rect.w * marker)
            pygame.draw.line(self.screen, (255, 255, 255), (mx, rect.y - 2), (mx, rect.bottom + 2), 2)
        pygame.draw.rect(self.screen, (70, 86, 120), rect, 1, border_radius=5)

    def level_color(self, fraction):
        if fraction < 0.2:
            return ALERT
        if fraction < 0.45:
            return WARN
        return GOOD

    def draw(self, game):
        self.hits = []
        if game.state == "menu":
            self.draw_menu(game)
        elif game.state == "play":
            self.draw_play(game)
        else:
            self.draw_end(game)

    def draw_menu(self, game):
        self.screen.fill((4, 6, 14))
        for x, y, b in self.stars:
            c = int(90 + 150 * b)
            self.screen.fill((c, c, c), (x, (y * 2) % H, 2, 2))
        self.text(self.huge, "SOLAR WATCH", (W // 2, 70), (255, 214, 110), "center")
        self.text(self.mid, "Junior Astronaut Mission Trainer", (W // 2, 118), INK, "center")
        self.text(self.small, "Run an outpost. Balance power, air, water, food and radiation. Outsmart the Sun.", (W // 2, 150), MUTED, "center")
        cards = [("moon", pygame.Rect(70, 200, 480, 400)), ("mars", pygame.Rect(630, 200, 480, 400))]
        for key, rect in cards:
            planet = data.PLANETS[key]
            hover = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, (22, 30, 48) if not hover else (32, 44, 70), rect, border_radius=14)
            pygame.draw.rect(self.screen, (255, 214, 110) if hover else PANEL_EDGE, rect, 3, border_radius=14)
            disc = (200, 200, 195) if key == "moon" else (200, 100, 60)
            pygame.draw.circle(self.screen, disc, (rect.x + 70, rect.y + 80), 46)
            for dx, dy, r in ((-14, -10, 9), (12, 14, 12), (16, -18, 6)):
                pygame.draw.circle(self.screen, dim(disc, 0.75), (rect.x + 70 + dx, rect.y + 80 + dy), r)
            self.text(self.big, planet["name"], (rect.x + 140, rect.y + 44))
            self.text(self.small, planet["site"], (rect.x + 140, rect.y + 82), MUTED)
            self.text(self.small, "Difficulty: " + planet["level"], (rect.x + 140, rect.y + 106), WARN if planet["level"] == "Hard" else GOOD)
            y = rect.y + 160
            for line in self.wrap(self.small, planet["challenge"], rect.w - 40):
                self.text(self.small, line, (rect.x + 20, y), INK)
                y += 24
            y += 12
            for fact in planet["facts"]:
                for i, line in enumerate(self.wrap(self.tiny, fact, rect.w - 60)):
                    prefix = "- " if i == 0 else "  "
                    self.text(self.tiny, prefix + line, (rect.x + 20, y), MUTED)
                    y += 21
                y += 6
            self.button((rect.x + 20, rect.bottom - 70, 210, 48), "Easy mode", lambda k=key: game.start(k, True),
                        color=(40, 100, 60), font=self.mid)
            self.button((rect.x + 250, rect.bottom - 70, 210, 48), "Hard mode" if key == "mars" else "Normal mode",
                        lambda k=key: game.start(k, False), color=(110, 60, 50) if key == "mars" else (38, 60, 100), font=self.mid)
        self.text(self.small, "Easy mode: more supplies, fewer and weaker flares, longer warnings, slower use of air, water and food.", (W // 2, H - 66), MUTED, "center")
        self.text(self.small, "Press ESC to quit", (W // 2, H - 40), MUTED, "center")

    def draw_play(self, game):
        sim = game.sim
        self.screen.fill((8, 11, 20))
        self.draw_scene(game)
        self.draw_top_bar(game)
        self.draw_life_panel(game)
        self.draw_power_panel(game)
        self.draw_control_panel(game)
        if game.popup is not None:
            self.draw_popup(game)
        if game.show_help:
            self.draw_help(game)

    def draw_top_bar(self, game):
        sim = game.sim
        pygame.draw.rect(self.screen, (10, 14, 26), (0, 0, W, SCENE_TOP))
        pygame.draw.line(self.screen, PANEL_EDGE, (0, SCENE_TOP), (W, SCENE_TOP), 2)
        day = sim.hour // 24 + 1
        clock = "Day %d/%d   %02d:00" % (min(day, data.MISSION_DAYS), data.MISSION_DAYS, sim.hour % 24)
        tag = " (EASY)" if sim.easy else ""
        self.text(self.mid, sim.planet["name"].upper() + " OUTPOST" + tag, (16, 14), (255, 214, 110))
        self.text(self.mid, clock, (330, 14))
        if sim.storm_active():
            phase, color = "DUST STORM", WARN
        elif sim.is_day():
            phase, color = "DAYLIGHT", GOOD
        else:
            phase, color = "NIGHT", (140, 170, 255)
        self.text(self.mid, phase, (520, 14), color)
        self.text(self.mid, "Build Points: %d" % sim.points, (670, 14), (150, 220, 255))
        status, level = sim.sun_status()
        color = {"alert": ALERT, "warn": WARN, "good": GOOD}[level]
        self.text(self.small, "SUN WATCH: " + status, (W - 16, 17), color, "topright")

    def sky_color(self, sim):
        base = sim.planet["sky"]
        if sim.key == "moon":
            return base
        return mix((10, 8, 26), base, min(1.0, sim.sunlight() * 1.6))

    def draw_scene(self, game):
        sim = game.sim
        planet = sim.planet
        sun = sim.sunlight()
        tick = pygame.time.get_ticks()
        pygame.draw.rect(self.screen, self.sky_color(sim), (0, SCENE_TOP, W, HORIZON - SCENE_TOP))

        star_vis = 1.0 if sim.key == "moon" else max(0.0, 1.0 - sun * 3.0)
        if star_vis > 0.05:
            for x, y, b in self.stars:
                c = int((90 + 150 * b) * star_vis)
                size = 2 if b > 0.8 else 1
                self.screen.fill((c, c, c), (x, y, size, size))

        if sim.key == "moon":
            pygame.draw.circle(self.screen, (60, 120, 220), (930, 110), 22)
            pygame.draw.circle(self.screen, (70, 170, 100), (924, 106), 9)
            pygame.draw.circle(self.screen, (235, 240, 250), (938, 100), 7)
        else:
            px = (tick // 40 + sim.hour * 9) % (W + 60) - 30
            pygame.draw.circle(self.screen, (120, 110, 105), (px, 120 + int(20 * math.sin(px / 90.0))), 5)

        self.draw_sun(sim, tick)

        shade = 0.28 + 0.72 * min(1.0, sun * 1.4)
        ground = dim(planet["ground"], shade)
        pygame.draw.polygon(self.screen, dim(planet["ground"], shade * 0.8), self.hills[sim.key] + [(W, HORIZON + 2), (0, HORIZON + 2)])
        pygame.draw.rect(self.screen, ground, (0, HORIZON, W, GROUND_BOTTOM - HORIZON))
        for x, y, r in self.craters[sim.key]:
            pygame.draw.ellipse(self.screen, dim(ground, 0.8), (x - r, y - r // 3, r * 2, max(4, r * 2 // 3)))

        if sim.flare_active():
            self.draw_particles(sim, tick)

        for i in range(data.SLOT_COUNT):
            self.draw_slot(game, i, shade)
        self.draw_habitat(game, shade)
        self.draw_crew(game, tick)
        self.draw_banner(sim, tick)

    def draw_sun(self, sim, tick):
        p = sim.phase()
        span = sim.planet["sun_hours"]
        radius = 26 if sim.key == "moon" else 18
        flare_now = sim.flare_active()
        incoming = sim.flare_incoming()
        if p < span:
            t = p / span
            x = int(70 + t * (W - 140))
            y = int(HORIZON - 12 - math.sin(math.pi * t) * (HORIZON - SCENE_TOP - 70))
            for extra, alpha in ((22, 0.12), (12, 0.25), (5, 0.5)):
                pygame.draw.circle(self.screen, mix(self.sky_color(sim), (255, 230, 150), alpha), (x, y), radius + extra)
            pygame.draw.circle(self.screen, (255, 236, 150), (x, y), radius)
            if incoming and (tick // 300) % 2 == 0:
                pygame.draw.circle(self.screen, ALERT, (x, y), radius + 10, 3)
            if flare_now:
                for k in range(8):
                    ang = k * math.pi / 4 + tick / 500.0
                    ex = x + int(math.cos(ang) * (radius + 26))
                    ey = y + int(math.sin(ang) * (radius + 26))
                    pygame.draw.line(self.screen, (255, 140, 60), (x, y), (ex, ey), 4)
        else:
            if incoming and (tick // 300) % 2 == 0:
                self.text(self.small, "Sun below the horizon, flare still inbound!", (W // 2, SCENE_TOP + 66), ALERT, "center")

    def draw_particles(self, sim, tick):
        for k in range(46):
            progress = ((tick / 1100.0) + k * 0.137) % 1.0
            x = 20 + (k * 263) % (W - 40)
            y = SCENE_TOP + progress * (GROUND_BOTTOM - SCENE_TOP)
            color = (255, 210, 90) if k % 2 else (255, 130, 70)
            pygame.draw.line(self.screen, color, (x, y), (x - 8, y - 22), 2)

    def draw_banner(self, sim, tick):
        text = None
        color = ALERT
        flare = sim.flare_active()
        incoming = sim.flare_incoming()
        storm_warn = None
        for storm in sim.storms:
            lead = storm["start"] - sim.hour
            if 0 < lead <= 12:
                storm_warn = lead
        if flare:
            text = "SOLAR FLARE (%s-class) IN PROGRESS" % flare["cls"]
        elif incoming:
            text = "%s-CLASS FLARE ARRIVES IN %d h  -  press S to shelter" % (incoming[0]["cls"], incoming[1])
        elif storm_warn:
            text = "DUST STORM ARRIVES IN %d h" % storm_warn
            color = WARN
        if text and (tick // 400) % 3 != 0:
            rect = pygame.Rect(0, 0, 640, 34)
            rect.center = (W // 2, SCENE_TOP + 30)
            pygame.draw.rect(self.screen, dim(color, 0.35), rect, border_radius=8)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=8)
            self.text(self.small, text, rect.center, INK, "center")
        if sim.sheltering:
            self.text(self.small, "CREW SHELTERING - ice mining paused", (W // 2, SCENE_TOP + 74), (150, 220, 255), "center")

    def draw_slot(self, game, index, shade):
        sim = game.sim
        cx = slot_x(index)
        gy = HORIZON + 22
        module = sim.slots[index]
        hit = pygame.Rect(cx - 46, gy - 76, 92, 112)
        pygame.draw.rect(self.screen, dim((90, 96, 108), shade + 0.2), (cx - 42, gy, 84, 6), border_radius=2)
        if module is None:
            r = pygame.Rect(cx - 36, gy - 52, 72, 52)
            for x in range(r.x, r.right, 10):
                pygame.draw.line(self.screen, (90, 110, 150), (x, r.y), (min(x + 5, r.right), r.y), 1)
                pygame.draw.line(self.screen, (90, 110, 150), (x, r.bottom), (min(x + 5, r.right), r.bottom), 1)
            self.text(self.big, "+", (cx, gy - 26), (110, 140, 190), "center")
            self.text(self.tiny, "empty slot", (cx, gy + 16), (110, 130, 170), "center")
        else:
            self.draw_module(module, cx, gy, shade, pygame.time.get_ticks())
            self.text(self.tiny, module.spec["name"], (cx, gy + 16), INK, "center")
            for l in range(module.level):
                pygame.draw.circle(self.screen, (255, 214, 110), (cx - (module.level - 1) * 6 + l * 12, gy + 34), 4)
            if module.damaged:
                self.text(self.mid, "!", (cx + 30, gy - 58), ALERT, "center")
                pygame.draw.line(self.screen, (120, 120, 120), (cx + 12, gy - 40), (cx + 18, gy - 62), 3)
        if hit.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, (255, 214, 110), hit, 2, border_radius=6)
        self.hits.append((hit, lambda i=index: game.open_popup(i)))

    def draw_module(self, module, cx, gy, shade, tick):
        kind = module.kind
        base = data.MODULE_COLORS[kind]
        c = dim(base, 0.55 + 0.45 * shade)
        d = dim(base, 0.35 + 0.3 * shade)
        s = self.screen
        if kind == "solar":
            pygame.draw.rect(s, (110, 110, 118), (cx - 2, gy - 30, 4, 30))
            panel = [(cx - 36, gy - 34), (cx + 30, gy - 54), (cx + 38, gy - 40), (cx - 28, gy - 20)]
            pygame.draw.polygon(s, c, panel)
            pygame.draw.polygon(s, (200, 220, 255), panel, 2)
            for k in range(1, 4):
                t = k / 4.0
                a = (panel[0][0] + (panel[1][0] - panel[0][0]) * t, panel[0][1] + (panel[1][1] - panel[0][1]) * t)
                b = (panel[3][0] + (panel[2][0] - panel[3][0]) * t, panel[3][1] + (panel[2][1] - panel[3][1]) * t)
                pygame.draw.line(s, (200, 220, 255), a, b, 1)
        elif kind == "battery":
            for k in range(3):
                filled = k < module.level
                rect = pygame.Rect(cx - 30 + k * 21, gy - 40, 18, 40)
                pygame.draw.rect(s, c if filled else d, rect, border_radius=3)
                pygame.draw.rect(s, (220, 240, 225), rect, 1, border_radius=3)
                pygame.draw.rect(s, (200, 200, 200), (rect.x + 5, rect.y - 4, 8, 4))
        elif kind == "oxygen":
            pygame.draw.rect(s, c, (cx - 18, gy - 44, 36, 44), border_radius=14)
            pygame.draw.rect(s, (230, 245, 255), (cx - 18, gy - 44, 36, 44), 2, border_radius=14)
            self.text(self.small, "O2", (cx, gy - 22), (20, 40, 70), "center")
        elif kind == "miner":
            pygame.draw.line(s, c, (cx - 22, gy), (cx, gy - 58), 4)
            pygame.draw.line(s, c, (cx + 22, gy), (cx, gy - 58), 4)
            pygame.draw.line(s, d, (cx - 12, gy - 24), (cx + 12, gy - 24), 3)
            bob = int(math.sin(tick / 200.0) * 4)
            pygame.draw.line(s, (200, 200, 205), (cx, gy - 58), (cx, gy - 8 + bob), 3)
            pygame.draw.circle(s, (255, 230, 120), (cx, gy - 62), 5)
        elif kind == "farm":
            points = [(cx + math.cos(math.pi * k / 12) * 38, gy - math.sin(math.pi * k / 12) * 44) for k in range(13)]
            pygame.draw.polygon(s, dim((150, 230, 170), 0.5 + 0.5 * shade), points)
            pygame.draw.polygon(s, (220, 255, 225), points, 2)
            for k in range(-2, 3):
                pygame.draw.rect(s, c, (cx + k * 12 - 3, gy - 14, 6, 12))
        elif kind == "shield":
            height = 22 + module.level * 12
            points = [(cx - 42, gy), (cx - 26, gy - height * 0.7), (cx, gy - height), (cx + 26, gy - height * 0.7), (cx + 42, gy)]
            pygame.draw.polygon(s, c, points)
            pygame.draw.polygon(s, d, points, 3)
            for k in range(module.level):
                pygame.draw.line(s, d, (cx - 30 + k * 4, gy - 10 - k * 12), (cx + 30 - k * 4, gy - 10 - k * 12), 2)
        elif kind == "reactor":
            pygame.draw.rect(s, (120, 124, 134), (cx - 22, gy - 46, 44, 46), border_radius=6)
            glow = 160 + int(70 * math.sin(tick / 250.0))
            pygame.draw.circle(s, (glow, glow, 60), (cx, gy - 26), 12)
            pygame.draw.rect(s, (90, 94, 104), (cx - 6, gy - 62, 12, 16))
        else:
            pygame.draw.rect(s, c, (cx - 36, gy - 30, 72, 30), border_radius=6)
            pygame.draw.rect(s, (30, 30, 40), (cx - 10, gy - 22, 20, 22))
            for k in range(4):
                pygame.draw.line(s, (255, 214, 110), (cx - 34 + k * 20, gy - 30), (cx - 24 + k * 20, gy - 22), 3)

    def draw_habitat(self, game, shade):
        cx = slot_x(0) + 5 * 106
        gy = HORIZON + 22
        pygame.draw.rect(self.screen, dim((90, 96, 108), shade + 0.2), (cx - 66, gy, 132, 6), border_radius=2)
        points = [(cx + math.cos(math.pi * k / 16) * 62, gy - math.sin(math.pi * k / 16) * 62) for k in range(17)]
        pygame.draw.polygon(self.screen, dim((205, 210, 220), 0.5 + 0.5 * shade), points)
        pygame.draw.polygon(self.screen, (240, 246, 255), points, 3)
        lit = game.sim.eff["heat"] > 0.5
        window = (255, 220, 130) if lit else (60, 66, 80)
        for k in (-32, -10, 12, 34):
            pygame.draw.rect(self.screen, window, (cx + k - 5, gy - 30, 10, 14), border_radius=3)
        pygame.draw.line(self.screen, (220, 220, 220), (cx, gy - 62), (cx, gy - 88), 2)
        pygame.draw.polygon(self.screen, (230, 70, 70), [(cx, gy - 88), (cx + 20, gy - 82), (cx, gy - 76)])
        self.text(self.tiny, "HABITAT", (cx, gy + 16), INK, "center")

    def draw_crew(self, game, tick):
        sim = game.sim
        if sim.sheltering:
            return
        cx = slot_x(0) + 5 * 106
        gy = HORIZON + 46
        for k, astro in enumerate(sim.crew):
            if not astro.alive:
                continue
            x = cx - 45 + k * 30 + int(math.sin(tick / 400.0 + k) * 3)
            pygame.draw.rect(self.screen, (240, 240, 245), (x - 4, gy - 16, 8, 14), border_radius=3)
            pygame.draw.circle(self.screen, (250, 210, 90), (x, gy - 20), 5)

    def draw_life_panel(self, game):
        sim = game.sim
        rect = pygame.Rect(8, PANEL_TOP, 420, H - PANEL_TOP - 8)
        self.panel(rect, "LIFE SUPPORT")
        rows = [
            ("Oxygen", sim.oxygen / data.OXYGEN_CAP, "%d" % sim.oxygen),
            ("Water", sim.water / data.WATER_CAP, "%d" % sim.water),
            ("Food", sim.food / data.FOOD_CAP, "%d" % sim.food),
            ("Battery", sim.battery / max(1.0, sim.battery_cap()), "%d/%d" % (sim.battery, sim.battery_cap())),
        ]
        y = rect.y + 36
        for label, fraction, value in rows:
            self.text(self.small, label, (rect.x + 14, y))
            self.bar((rect.x + 96, y + 2, 220, 18), fraction, self.level_color(fraction))
            self.text(self.small, value, (rect.x + 326, y), MUTED)
            y += 32
        dose_fraction = sim.dose / (data.DOSE_LIMIT * 1.5)
        dose_color = GOOD if sim.dose < data.DOSE_LIMIT * 0.6 else WARN if sim.dose < data.DOSE_LIMIT else ALERT
        self.text(self.small, "Radiation", (rect.x + 14, y))
        self.bar((rect.x + 96, y + 2, 220, 18), dose_fraction, dose_color, marker=1 / 1.5)
        self.text(self.small, "%.0f mSv" % sim.dose, (rect.x + 326, y), MUTED)
        y += 30
        rate = sim.radiation_rate()
        self.text(self.tiny, "Dose rate now: %.2f mSv/h   (white mark = safe limit)" % rate, (rect.x + 14, y), MUTED)
        y += 26
        self.text(self.small, "CREW HEALTH", (rect.x + 14, y), MUTED)
        y += 24
        for k, astro in enumerate(sim.crew):
            col = k % 2
            row = k // 2
            bx = rect.x + 14 + col * 202
            by = y + row * 34
            self.text(self.tiny, astro.name if astro.alive else astro.name + " (lost)", (bx, by))
            fraction = astro.health / 100.0
            self.bar((bx + 70, by + 1, 110, 14), fraction, self.level_color(fraction) if astro.alive else (80, 80, 80))

    def draw_power_panel(self, game):
        sim = game.sim
        rect = pygame.Rect(436, PANEL_TOP, 360, H - PANEL_TOP - 8)
        self.panel(rect, "POWER PRIORITY PROGRAM")
        made = sim.production
        self.text(self.tiny, "Making %.0f kW   Using %.0f kW" % (made, sim.used), (rect.right - 14, rect.y + 10), GOOD if made >= sim.used else WARN, "topright")
        self.text(self.tiny, "Always on: computers and comms (%.0f kW)" % data.BASE_LOAD, (rect.x + 14, rect.y + 32), MUTED)
        y = rect.y + 56
        for rank, key in enumerate(sim.priority):
            row = pygame.Rect(rect.x + 10, y, rect.w - 20, 54)
            pygame.draw.rect(self.screen, (24, 32, 50), row, border_radius=8)
            pygame.draw.circle(self.screen, (60, 90, 140), (row.x + 18, row.centery), 12)
            self.text(self.small, str(rank + 1), (row.x + 18, row.centery), INK, "center")
            on = sim.enabled[key]
            self.text(self.small, data.SYSTEM_NAMES[key], (row.x + 40, row.y + 6), INK if on else (110, 116, 130))
            want = sim.demand(key)
            if not on:
                note = "switched off"
            elif want <= 0 and key in ("oxygen", "food"):
                note = "none built"
            elif want <= 0 and key == "water":
                note = "none built" if sim.levels("miner") == 0 else "paused (shelter)"
            else:
                note = "needs %.0f kW" % want
            self.text(self.tiny, note, (row.x + 40, row.y + 30), MUTED)
            eff = sim.eff[key] if on else 0.0
            self.bar((row.x + 136, row.y + 33, 76, 10), eff, self.level_color(eff))
            self.button((row.x + 222, row.y + 12, 30, 30), "^", lambda k=key: sim.move_priority(k, -1), rank > 0, font=self.small)
            self.button((row.x + 256, row.y + 12, 30, 30), "v", lambda k=key: sim.move_priority(k, 1), rank < len(sim.priority) - 1, font=self.small)
            self.button((row.x + 290, row.y + 12, 46, 30), "ON" if on else "OFF", lambda k=key: sim.toggle_system(k), True,
                        color=(40, 100, 60) if on else (110, 50, 50), font=self.tiny)
            y += 60

    def draw_control_panel(self, game):
        sim = game.sim
        rect = pygame.Rect(804, PANEL_TOP, W - 804 - 8, H - PANEL_TOP - 8)
        self.panel(rect, "MISSION CONTROL")
        x = rect.x + 12
        y = rect.y + 30
        self.button((x, y, 84, 32), "Play" if game.paused else "Pause", game.toggle_pause, active=game.paused)
        for k, speed in enumerate((1, 2, 4)):
            self.button((x + 92 + k * 48, y, 42, 32), "%dx" % speed, lambda s=speed: game.set_speed(s), active=game.speed == speed)
        self.button((rect.right - 88, y, 76, 32), "Help", game.toggle_help)
        label = "Come out of shelter (S)" if sim.sheltering else "SHELTER the crew (S)"
        self.button((x, y + 40, rect.w - 24, 40), label, sim.toggle_shelter,
                    color=(120, 60, 50) if not sim.sheltering else (40, 100, 120), font=self.mid)
        status, level = sim.sun_status()
        top = y + 92
        area = pygame.Rect(x, top, rect.w - 24, rect.bottom - top - 10)
        pygame.draw.rect(self.screen, (10, 14, 24), area, border_radius=6)
        self.screen.set_clip(area.inflate(-8, -6))
        rows = []
        for hour, message, kind in sim.log[-14:]:
            stamp = "D%d %02d:00  %s" % (hour // 24 + 1, hour % 24, message)
            for line in self.wrap(self.tiny, stamp, area.w - 16):
                rows.append((line, LOG_COLORS[kind]))
        fit = max(1, (area.h - 8) // 19)
        for k, (line, color) in enumerate(rows[-fit:]):
            self.text(self.tiny, line, (area.x + 8, area.y + 6 + k * 19), color)
        self.screen.set_clip(None)

    def draw_popup(self, game):
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 160))
        self.screen.blit(veil, (0, 0))
        self.hits.append((pygame.Rect(0, 0, W, H), game.close_popup))
        module = game.sim.slots[game.popup]
        if module is None:
            self.draw_build_menu(game)
        else:
            self.draw_module_menu(game, module)

    def draw_build_menu(self, game):
        sim = game.sim
        box = pygame.Rect(190, 40, 800, 600)
        pygame.draw.rect(self.screen, PANEL, box, border_radius=14)
        pygame.draw.rect(self.screen, PANEL_EDGE, box, 3, border_radius=14)
        self.hits.append((box, lambda: None))
        self.text(self.big, "What should we build?", (box.x + 24, box.y + 16))
        self.text(self.small, "Build Points: %d" % sim.points, (box.right - 24, box.y + 26), (150, 220, 255), "topright")
        y = box.y + 70
        for kind in data.MODULE_ORDER:
            spec = data.MODULES[kind]
            row = pygame.Rect(box.x + 18, y, box.w - 36, 56)
            affordable = sim.points >= spec["cost"]
            hover = affordable and row.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, (40, 56, 88) if hover else (24, 32, 50), row, border_radius=8)
            pygame.draw.rect(self.screen, data.MODULE_COLORS[kind], (row.x, row.y, 8, row.h), border_radius=4)
            self.text(self.mid, spec["name"], (row.x + 22, row.y + 16), INK if affordable else (110, 116, 130))
            for i, line in enumerate(self.wrap(self.tiny, spec["blurb"], 420)[:2]):
                self.text(self.tiny, line, (row.x + 230, row.y + 10 + i * 19), MUTED)
            self.text(self.mid, "%d BP" % spec["cost"], (row.right - 16, row.y + 16), (150, 220, 255) if affordable else ALERT, "topright")
            if affordable:
                self.hits.append((row, lambda k=kind: game.build(k)))
            y += 62
        self.button((box.centerx - 60, box.bottom - 46, 120, 34), "Cancel", game.close_popup)

    def draw_module_menu(self, game, module):
        sim = game.sim
        index = game.popup
        box = pygame.Rect(320, 150, 540, 380)
        pygame.draw.rect(self.screen, PANEL, box, border_radius=14)
        pygame.draw.rect(self.screen, PANEL_EDGE, box, 3, border_radius=14)
        self.hits.append((box, lambda: None))
        self.text(self.big, module.spec["name"], (box.x + 24, box.y + 18), data.MODULE_COLORS[module.kind])
        self.text(self.small, "Level %d of %d" % (module.level, module.spec["max"]), (box.right - 24, box.y + 28), INK, "topright")
        y = box.y + 70
        for line in self.wrap(self.small, module.spec["blurb"], box.w - 48):
            self.text(self.small, line, (box.x + 24, y), MUTED)
            y += 24
        y += 10
        self.text(self.small, sim.describe(module), (box.x + 24, y), GOOD)
        y += 28
        if module.damaged:
            self.text(self.small, "DAMAGED: working at half strength.", (box.x + 24, y), ALERT)
        by = box.bottom - 170
        can_up = module.can_upgrade()
        label = "Upgrade (%d BP)" % module.upgrade_cost() if can_up else "Max level"
        self.button((box.x + 24, by, box.w - 48, 40), label, game.upgrade, can_up and sim.points >= module.upgrade_cost(), font=self.mid)
        self.button((box.x + 24, by + 48, box.w - 48, 40), "Repair (%d BP)" % data.REPAIR_COST, game.repair,
                    module.damaged and sim.points >= data.REPAIR_COST, font=self.mid)
        self.button((box.x + 24, by + 96, (box.w - 60) // 2, 40), "Recycle (+%d BP)" % (module.spec["cost"] // 2), game.demolish,
                    True, color=(110, 50, 50), font=self.mid)
        self.button((box.x + 36 + (box.w - 60) // 2, by + 96, (box.w - 60) // 2, 40), "Close", game.close_popup, font=self.mid)

    def draw_help(self, game):
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 200))
        self.screen.blit(veil, (0, 0))
        box = pygame.Rect(160, 40, 860, 640)
        pygame.draw.rect(self.screen, PANEL, box, border_radius=14)
        pygame.draw.rect(self.screen, PANEL_EDGE, box, 3, border_radius=14)
        self.hits.append((pygame.Rect(0, 0, W, H), game.toggle_help))
        self.text(self.big, "MISSION BRIEFING - " + game.sim.planet["name"], (box.x + 28, box.y + 20), (255, 214, 110))
        y = box.y + 80
        for line in data.HELP_LINES:
            if line:
                color = (255, 214, 110) if line.split(":")[0].isupper() and ":" in line else INK
                self.text(self.small, line, (box.x + 28, y), color)
            y += 27
        self.button((box.centerx - 100, box.bottom - 56, 200, 40), "Start mission", game.toggle_help, font=self.mid, color=(40, 100, 60))

    def draw_end(self, game):
        sim = game.sim
        self.screen.fill((4, 6, 14))
        for x, y, b in self.stars:
            c = int(90 + 150 * b)
            self.screen.fill((c, c, c), (x, (y * 2) % H, 2, 2))
        won = sim.outcome == "won"
        self.text(self.huge, "MISSION COMPLETE" if won else "MISSION FAILED", (W // 2, 80), GOOD if won else ALERT, "center")
        if sim.easy:
            self.text(self.small, "Easy mode", (W // 2, 130), (150, 220, 255), "center")
        stars = sim.stars()
        for k in range(3):
            self.draw_star((W // 2 - 90 + k * 90, 170), 34, k < stars)
        self.text(self.mid, "Crew alive: %d/4     Average health: %.0f%%     Radiation: %.0f mSv" % (sim.alive_count(), sim.average_health(), sim.dose),
                  (W // 2, 240), INK, "center")
        y = 290
        for line in sim.report():
            for part in self.wrap(self.small, line, 860):
                self.text(self.small, part, (W // 2, y), MUTED, "center")
                y += 28
            y += 6
        self.button((W // 2 - 230, H - 120, 210, 48), "Play again", game.go_menu, font=self.mid, color=(40, 100, 60))
        self.button((W // 2 + 20, H - 120, 210, 48), "Quit", game.quit, font=self.mid, color=(110, 50, 50))

    def draw_star(self, center, radius, filled):
        points = []
        for k in range(10):
            r = radius if k % 2 == 0 else radius * 0.45
            ang = -math.pi / 2 + k * math.pi / 5
            points.append((center[0] + math.cos(ang) * r, center[1] + math.sin(ang) * r))
        if filled:
            pygame.draw.polygon(self.screen, (255, 214, 110), points)
        pygame.draw.polygon(self.screen, (255, 214, 110) if filled else (80, 88, 110), points, 3)
