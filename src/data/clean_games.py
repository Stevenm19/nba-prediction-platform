import pandas as pd

def clean_games(schedule: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning NBA schedules into one row per completed game.
    """

    required_cols = [
        'game_id',
        'game_date',
        'season',
        'season_type',
        'status_type_name',
        'status_type_completed',
        'home_id',
        'away_id',
        'home_abbreviation',
        'away_abbreviation',
        'home_score',
        'away_score'
    ]

    # Check for any missing columns
    missing_cols = set(required_cols) - set(schedule.columns)

    if missing_cols:
        raise ValueError(f'Missing required columns: {missing_cols}')

    # We only want completed regular-season games
    # Note: Regular season games have season_type 2
    games = schedule.loc[
        (
            (schedule['season_type'] == 2) &
            (schedule['status_type_name'] == 'STATUS_FINAL') &
            (schedule['status_type_completed'] == True) &
            (schedule['type_abbreviation'] == 'STD') &
            (schedule['home_id'].between(1,30)) &
            (schedule['away_id'].between(1,30))
        ),
        required_cols
    ].copy()

    # Rename some columns for ease of use
    games = games.rename(columns= {
        'home_abbreviation': 'home_team',
        'away_abbreviation': 'away_team'
    })

    # Convert date column to datetime
    games['game_date'] = pd.to_datetime(games['game_date'], errors='coerce')

    # Making sure the scores are numeric
    for c in ['home_score', 'away_score']:
        games[c] = pd.to_numeric(games[c], errors='coerce')
    
    cleaned_cols = [
        'game_id', 
        'game_date',
        'season',
        'home_id',
        'away_id',
        'home_team',
        'away_team',
        'home_score',
        'away_score',
    ]

    # Validation checks
    if games[cleaned_cols].isna().any().any():
        raise ValueError('Missing values in essential game fields')

    if games['game_id'].duplicated().any():
        raise ValueError('Duplicate game IDs detected')
    
    if (games['home_id'] == games['away_id']).any():
        raise ValueError('Teams cannot play against themselves')
    
    if (games[['home_score', 'away_score']] < 0).any().any():
        raise ValueError('Invalid scores detected (negative scores)')
    
    if (games['home_score'] == games['away_score']).any():
        raise ValueError('Completed games cannot have tied games')
    
    # Calculate home_win
    games['home_win'] = (games['home_score'] > games['away_score']).astype(int)

    # Sort games chronilogicaly and by game_id
    games = games.sort_values(['game_date', 'game_id']).reset_index(drop=True)

    return games[cleaned_cols + ['home_win']]