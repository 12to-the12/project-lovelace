# 2025 SBCC Game Jam Submission

"lovelace"

the current codebase is just me learning networking

I've implemented a TCP based gamestate protocol and 3 different ways of drawing remote players

- just drawing their most recent recorded location (white)
- guessing where they'd be given the timestamp of their last location & their velocity (yellow)
- replaying where they were 50ms ago, interpolating between snapshots, the best way to do things(orange), this disk flashes bright blue if it's having to extrapolate from old data to arrive to 50ms ago.

red represents where the local player is

![demo](image.png)

They also get smaller based on how old their source data is.

## running
My Makefile is designed for my local environment only
This is what you need to do to run the project on a *NIX device:

run ```python -m venv .venv``` to create  a virtual environment

run ```./.venv/bin/python -m pip install -r requirements.txt``` to install the required packages

run ```./.venv/bin/python ./src/main.py``` to run the project