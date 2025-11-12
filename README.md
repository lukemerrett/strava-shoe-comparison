# Strava Shoe Comparison Tool

Compare your running shoes' performance by analyzing Strava activities from the last 12 months. Get average pace and estimated Grade Adjusted Pace (GAP) for each pair of shoes.

## Quick Start

### 1. Get Strava API Credentials

1. Go to https://www.strava.com/settings/api
2. Create a new application:
   - **Application Name**: Choose any name (e.g., "Shoe Comparison")
   - **Category**: Choose appropriate category
   - **Club**: Leave blank if not applicable
   - **Website**: Can be any URL (e.g., "http://localhost")
   - **Authorization Callback Domain**: **Must be** `localhost`
3. After creating the app, note your:
   - **Client ID** (displayed on the page)
   - **Client Secret** (click "Show" to reveal it)

### 2. Install Dependencies

Using [uv](https://github.com/astral-sh/uv) (recommended):
```bash
uv sync
```

### 3. Configure Credentials

Create a `.env` file in the project directory:

```
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
```

### 4. Run the Program

Using uv:
```bash
uv run python main.py
```

Or directly with Python:
```bash
python main.py
```

On first run, you'll be prompted to:
1. Visit an authorization URL in your browser
2. Authorize the application
3. Copy the authorization code from the redirect URL
4. Paste it back into the terminal

After initial setup, the program will automatically refresh tokens and run without manual intervention.

## Output

The program displays results grouped by shoes, showing metrics for all runs and non-race runs separately:

```
============================================================
Strava Running Shoe Comparison (Last 12 Months)
============================================================

Nike Pegasus 40
  Total Activities: 45 (40 non-race)
  Total Distance: 225.5 km

  All Runs:
    Average Pace: 5:15 /km
    Estimated GAP: 5:06 /km

  Non-Race Runs:
    Average Pace: 5:21 /km
    Estimated GAP: 5:12 /km

Hoka Clifton 9
  Total Activities: 32 (30 non-race)
  Total Distance: 180.3 km

  All Runs:
    Average Pace: 5:30 /km
    Estimated GAP: 5:22 /km

  Non-Race Runs:
    Average Pace: 5:35 /km
    Estimated GAP: 5:28 /km
============================================================
```

## Understanding the Metrics

- **All Runs**: Includes every running activity (races, easy runs, workouts, etc.)
- **Non-Race Runs**: Excludes races to show your typical training pace
- **Average Pace**: Your actual running pace calculated from distance and moving time
- **Estimated GAP**: Grade Adjusted Pace - an approximation of your pace on flat terrain, accounting for elevation changes
  - Note: This is a simplified estimation and will differ from Strava's proprietary GAP calculation
  - Strava's actual GAP uses more sophisticated segment-by-segment analysis

### Race Detection

Activities are classified as races if they have:
- `workout_type=1` (race) in Strava, OR
- Names containing: "race", "parkrun", "marathon", "half marathon", "10k race", "5k race"

## Project Structure

- `main.py` - Main program orchestration
- `auth.py` - OAuth 2.0 authentication handling
- `strava_client.py` - Strava API client
- `analyzer.py` - Activity data processing and metrics calculation
- `SPEC.md` - Detailed technical specification

## Requirements

- Python 3.8+
- Active Strava account with running activities
- Activities must have shoes assigned in Strava to be grouped properly

## API Rate Limits

The Strava API has rate limits:
- 200 requests per 15 minutes
- 2,000 requests per day

The program respects these limits with pagination and delays between requests.

## Troubleshooting

### "No valid access token found"
Run the authentication flow again. Your tokens may have expired.

### "Failed to fetch activities"
Check your internet connection and Strava API status. You may have hit rate limits.

### "No running activities found"
Ensure you have running activities in Strava for the last 12 months with the activity type set to "Run".

### Activities without shoes
Activities without assigned gear will be grouped under "No Shoe Recorded".

## Security

- Never commit your `.env` file to version control
- Keep your Client Secret private
- Tokens are stored locally in `.env` file

## License

This project is for personal use with your own Strava data.
