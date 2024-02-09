# RootAI

[//]: # (Write description here)

## Running the Project

### Prerequisite

- pygame 2.4.0+
  - `pip install pygame`
  - (not recommended, un-maintained) `conda install -c conda-forge pygame`
- conda 23.3.1+
  - download from conda website
- python 11.3+
  - select from conda navigator when creating environment

### Setup

1. Add a new Python configuration (top right)
   - set name: `Run main.py`
   - set Script path: `.\main.py`
   - set Environment > Working directory to absolute path to `src`
     - eg. `D:\GitHub\RootAI\src`
2. Go to Settings > CodeStyle > Cogs icon > Import scheme > import `codestyle.xml` 

### Running the Game
#### Option 1 - Run inside IntelliJ
1. Run `Run main.py` to run the game
#### Option 2 - Run via command line
1. run python with config file path as arg `python -m src.main ".\src\config\config.yml"`

## Controls
- Press UP/DOWN --- change action
- Press R --- random action
- Press RETURN/SPACE --- execute selected action
- Press O --- print_game_state
- Press C --- new_game_from_current_game_state
- Hold F --- continuously run player
- Hold A --- continuously run agent
- Press N in game-end state --- new game
- Press Q in game-end state --- quit game

## Technical
### Action generation
Each action generation sequence corresponds to a 5 digit-number.
- Digit 0: faction = 1 (Marquise) | 2 (Eyrie) | 9 (Neutral)
- Digit 1-4: distinct id for that method

e.g.
- 10001 = action generation sequence 1 for Marquise


