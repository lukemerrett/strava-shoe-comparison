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

## AI Generation

This program was developed using [Claude Code](https://www.claude.com/product/claude-code).

Prompts used for reference:

```
Hey Claude, I'd like to build a python program that accesses the Strava API on my behalf and get's a list of Running activities I've done over the last 12 
months.

Then the python program should group the activities by which shoes I was wearing.

Then I want to know the Average GAP (Grade Adjusted Pace) for each shoe

Please document how you will achieve this in a markdown SPEC.md file, then build this program.

If there's any details or clarifications you need from me please just pause and ask. I expect at some point you will need my credentials or an API key, please ask 
for it, if an API key please provide instructions on how I can get it. 
```

```
# The Strava API doesn't provide GAP, Claude asked how I would like to proceed:

Use average pace and also calculate for me an estimated GAP, then give me both in the results per shoe
```

```
Change requirements.txt to a uv setup https://github.com/astral-sh/uv 
```

```
Please update the project (code and documentation) so we output these details for each shoe:

- Average Pace over all runs
- Average GAP over all runs
- Average Pace over all runs not tagged with Race
- Average GAP over all runs not tagged with Race 
```

```
Great thank you.

Please prepare this as a GitHub repo with a Python .gitignore file, ensuring the .env file is also ignored.

Please include an MIT licence

Please then push to this repo https://github.com/lukemerrett/strava-shoe-comparison 
```

```
Remove `Or using pip:` from the README.

Change `Using uv (recommended):` so `uv` is a markdown link to the uv repository I gave you earlier

Commit and push these changes 
```