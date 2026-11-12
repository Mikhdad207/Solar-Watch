# SOLAR WATCH: Junior Astronaut Mission Trainer

A 2D space-themed strategy game made for the NASA Space Apps Challenge
"Build a Junior Astronaut Mission Trainer".

You run a lunar or Martian outpost with 4 astronauts and must keep them alive for 20 days.
Every choice has a cost: power for oxygen means less power for food, shelter from a
solar flare means the ice miners stop, and shielding costs points you wanted for batteries.

## How to run

1. Install Python 3.9 or newer.
2. Install the only dependency:

       pip install pygame

3. Start the game from this folder:

       python main.py

## How to play

- Pick The Moon or Mars, then choose a mode:
  - Easy mode: more starting points and bigger supply drops, fewer and weaker flares, 10 hours of flare warning, less air, water and food used, milder dust storms and cold, fewer meteorites, and crew that get hurt more slowly. Good for first-time players and younger students.
  - Normal mode (Moon) or Hard mode (Mars): the full challenge.
- Click an empty slot to build. Click a built module to upgrade, repair or recycle it.
- Supply drops from Earth give Build Points every 3 days.
- Watch the bars: oxygen, water, food, battery, radiation and crew health.
- Use the Power Priority Program: when power runs short, the top of the list is served first.
  You can reorder systems with the arrow buttons or switch one off on purpose.
- Sun Watch warns you about solar flares. Press S (or the Shelter button) to move the crew
  into shelter. A Storm Shelter module makes this much safer.
- Micrometeorites damage modules. Repair them for a few points.

Keys: SPACE pause, 1 / 2 / 3 speed, S shelter, H help, ESC back.

## Winning

Keep at least one astronaut alive until day 20. Three stars need the whole crew alive,
radiation under 100 mSv and good health. The end screen explains what helped and what hurt.

## Challenge topics covered

- Games: a complete real-time strategy game with win and lose conditions.
- Planets and Moons: the Moon has long, freezing nights and full-strength radiation.
  Mars has weak sunlight, cold nights and long dust storms.
- Sun: the Sun is both your power supply and your biggest threat. Day and night change
  solar output, and flares of C, M and X class raise the radiation dose.
- Space Exploration: life support, power storage, radiation shielding, food and water
  production, fission power, and supply missions from Earth.
- Software: the Power Priority Program lets players decide how a power shortage is handled,
  like a simple load-shedding program. The whole game is written in Python with pygame.

## Learning goals

- Solar power stops at night, so storage or another source is needed.
- Batteries store energy, they do not make it.
- Radiation adds up over time. Shielding works all the time, sheltering works during storms.
- Every system depends on another: air needs water, water needs power, food needs both.

## Project layout

    main.py            start the game
    outpost/data.py    numbers, module list, planet settings
    outpost/sim.py     the simulation (power, life support, radiation, events)
    outpost/render.py  all drawing and menus
    outpost/app.py     game loop, input and screens

The game does not use any image or sound files. Everything is drawn with code.
Time and distances are shortened for gameplay, so numbers are simplified, not exact.
