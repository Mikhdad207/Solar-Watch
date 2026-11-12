import sys

import pygame

from . import data
from .render import Renderer
from .sim import Outpost


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((data.WIDTH, data.HEIGHT))
        pygame.display.set_caption("Solar Watch - Junior Astronaut Mission Trainer")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.state = "menu"
        self.sim = None
        self.paused = True
        self.speed = 1
        self.popup = None
        self.show_help = False
        self.accumulator = 0.0
        self.running = True
        self.end_timer = 0.0

    def start(self, planet_key, easy=False):
        self.sim = Outpost(planet_key, easy=easy)
        self.state = "play"
        self.paused = True
        self.speed = 1
        self.popup = None
        self.show_help = True
        self.accumulator = 0.0
        self.end_timer = 0.0

    def go_menu(self):
        self.state = "menu"
        self.sim = None

    def quit(self):
        self.running = False

    def toggle_pause(self):
        self.paused = not self.paused

    def set_speed(self, speed):
        self.speed = speed
        self.paused = False

    def toggle_help(self):
        self.show_help = not self.show_help

    def open_popup(self, index):
        self.popup = index

    def close_popup(self):
        self.popup = None

    def build(self, kind):
        if self.sim.build(self.popup, kind):
            self.popup = None

    def upgrade(self):
        self.sim.upgrade(self.popup)

    def repair(self):
        self.sim.repair(self.popup)

    def demolish(self):
        if self.sim.demolish(self.popup):
            self.popup = None

    def handle_click(self, pos):
        for rect, action in reversed(self.renderer.hits):
            if rect.collidepoint(pos):
                action()
                return

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            if self.state == "menu":
                self.running = False
            elif self.show_help:
                self.show_help = False
            elif self.popup is not None:
                self.popup = None
            elif self.state == "play":
                self.go_menu()
            else:
                self.go_menu()
            return
        if self.state != "play" or self.show_help:
            return
        if key == pygame.K_SPACE:
            self.toggle_pause()
        elif key == pygame.K_1:
            self.set_speed(1)
        elif key == pygame.K_2:
            self.set_speed(2)
        elif key == pygame.K_3:
            self.set_speed(4)
        elif key == pygame.K_s:
            self.sim.toggle_shelter()
        elif key == pygame.K_h:
            self.toggle_help()

    def update(self, dt):
        if self.state != "play":
            return
        if self.sim.finished:
            self.end_timer += dt
            if self.end_timer > 1.5:
                self.state = "end"
            return
        if self.paused or self.show_help or self.popup is not None:
            return
        self.accumulator += dt * self.speed
        while self.accumulator >= data.STEP_SECONDS and not self.sim.finished:
            self.accumulator -= data.STEP_SECONDS
            self.sim.step()
            if self.sim.take_alert() and self.speed > 1:
                self.speed = 1
                self.accumulator = 0.0
                break

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            self.update(dt)
            self.renderer.draw(self)
            pygame.display.flip()
        pygame.quit()
        sys.exit()
