from pathlib import Path

import pandas as pd
import sportsdataverse as sdv

from src.data.clean_games import clean_games

RAW = Path('data/raw')
PROCESSED = Path('data/processed')

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

START_SEASON = 2019 
LAST_SEASON = 2027

SEASONS = range(START_SEASON, LAST_SEASON)

for season in SEASONS:
    print(f'Processing data for the {season-1}-{season} season...')

    schedule_path = RAW / f'schedule_{season}.parquet'
    box_path = RAW / f'team_box_{season}.parquet' 
    games_path = PROCESSED / f'games_{season}.parquet'

    # If the path doesn't exist yet, download the data for this season
    if not schedule_path.exists():
        schedule = sdv.nba.load_nba_schedule(seasons=[season]).to_pandas()
        schedule.to_parquet(schedule_path, index=False)
    else:
        schedule = pd.read_parquet(schedule_path)

    if not box_path.exists():
        box = sdv.nba.load_nba_team_boxscore(seasons=[season]).to_pandas()
        box.to_parquet(box_path, index=False)

    
    # Clean the game dataset and save it
    games = clean_games(schedule)
    games.to_parquet(games_path, index=False)

    print(f'Saved {len(games)} games for the {season-1}-{season} season.')