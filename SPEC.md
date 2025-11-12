# Strava Shoe Comparison Tool - Specification

## Overview
A Python program that retrieves running activities from the Strava API for the past 12 months, groups them by shoes worn, and calculates average pace and estimated Grade Adjusted Pace (GAP) for each pair of shoes.

## Features
- OAuth 2.0 authentication with Strava API
- Fetch all running activities from the last 12 months
- Group activities by gear (running shoes)
- Calculate average pace per shoe
- Calculate estimated GAP per shoe
- Display results in a clear, readable format

## Technical Requirements

### Python Version
- Python 3.8+

### Dependencies
- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management
- `datetime` - Date/time calculations

### Strava API Requirements
- **Client ID** and **Client Secret** (obtained from https://www.strava.com/settings/api)
- **OAuth 2.0 Authorization** with scopes:
  - `activity:read_all` - Read all activity data including private activities
  - `read` - Read public profile data
- **Rate Limits**: 200 requests per 15 minutes, 2,000 per day

## Architecture

### Components

#### 1. Authentication Module (`auth.py`)
**Purpose**: Handle OAuth 2.0 flow and token management

**Functions**:
- `get_authorization_url(client_id, redirect_uri)` - Generate OAuth authorization URL
- `exchange_code_for_token(client_id, client_secret, code)` - Exchange authorization code for tokens
- `refresh_access_token(client_id, client_secret, refresh_token)` - Refresh expired access token
- `save_tokens(tokens)` - Save tokens to `.env` file
- `load_tokens()` - Load tokens from `.env` file

**Flow**:
1. User obtains Client ID and Client Secret from Strava
2. Program generates authorization URL
3. User visits URL in browser and authorizes the app
4. User copies authorization code from redirect URL
5. Program exchanges code for access token and refresh token
6. Tokens are saved to `.env` file for future use

#### 2. API Client Module (`strava_client.py`)
**Purpose**: Interface with Strava API endpoints

**Class**: `StravaClient`

**Methods**:
- `__init__(access_token)` - Initialize with access token
- `get_athlete()` - Get authenticated athlete information
- `get_activities(after, before, page, per_page)` - Get paginated list of activities
- `get_all_activities_since(date)` - Get all activities since a specific date (handles pagination)
- `get_gear(gear_id)` - Get gear (shoe) details by ID

**API Endpoints Used**:
- `GET /api/v3/athlete` - Get athlete info
- `GET /api/v3/athlete/activities` - List activities
- `GET /api/v3/gear/{id}` - Get gear details

#### 3. Data Processing Module (`analyzer.py`)
**Purpose**: Process activities and calculate metrics

**Functions**:
- `filter_running_activities(activities)` - Filter for running type activities
- `group_by_gear(activities)` - Group activities by gear_id
- `is_race(activity)` - Determine if activity is a race
- `filter_non_race_activities(activities)` - Filter out race activities
- `calculate_average_pace(activities)` - Calculate average pace from distance/moving_time
- `calculate_estimated_gap(activities)` - Calculate estimated GAP using elevation data
- `format_pace(pace_seconds_per_km)` - Format pace as MM:SS per km (or mile)
- `get_gear_names(client, gear_ids)` - Fetch shoe names for gear IDs
- `calculate_shoe_statistics(activities)` - Calculate all metrics for a shoe

**Pace Calculation**:
```
pace (min/km) = moving_time (seconds) / (distance (meters) / 1000)
```

**Estimated GAP Calculation**:
The estimation uses a simplified model based on elevation gain:
```
elevation_factor = 1 + (total_elevation_gain / distance) * adjustment_coefficient
adjusted_time = moving_time / elevation_factor
estimated_gap = adjusted_time / (distance / 1000)
```

Where:
- `adjustment_coefficient` ≈ 0.033 (based on research that ~3.3% time penalty per 1% grade)
- This is a simplified approximation of Strava's proprietary GAP algorithm

**Note**: This estimated GAP is less sophisticated than Strava's actual GAP calculation, which:
- Uses segment-by-segment grade analysis
- Accounts for pace-dependent adjustments
- Handles downhill running differently
- Uses heart rate data when available

#### 4. Main Program (`main.py`)
**Purpose**: Orchestrate the entire workflow

**Workflow**:
1. Load or perform authentication
2. Initialize Strava client
3. Calculate date for 12 months ago
4. Fetch all running activities from the last 12 months
5. Filter for running activities only
6. Group activities by gear (shoes)
7. Fetch gear names from API
8. Calculate metrics for each shoe:
   - Total activities (all and non-race)
   - Total distance
   - Average pace (all runs)
   - Estimated GAP (all runs)
   - Average pace (non-race runs)
   - Estimated GAP (non-race runs)
9. Display results in formatted table

## Data Structures

### Activity Object (from API)
```json
{
  "id": 123456789,
  "name": "Morning Run",
  "type": "Run",
  "sport_type": "Run",
  "distance": 5000.0,
  "moving_time": 1800,
  "elapsed_time": 1900,
  "total_elevation_gain": 50.0,
  "start_date": "2024-11-12T08:00:00Z",
  "gear_id": "g987654",
  "average_speed": 2.78
}
```

### Gear Object (from API)
```json
{
  "id": "g987654",
  "primary": true,
  "name": "Nike Pegasus 40",
  "distance": 250000,
  "brand_name": "Nike",
  "model_name": "Pegasus 40"
}
```

### Shoe Statistics (computed)
```python
{
  "gear_id": "g987654",
  "gear_name": "Nike Pegasus 40",
  "activity_count": 45,
  "non_race_count": 40,
  "total_distance_km": 225.5,
  "average_pace_min_per_km": 5.25,  # minutes (all runs)
  "estimated_gap_min_per_km": 5.10,  # minutes (all runs)
  "average_pace_non_race_min_per_km": 5.35,  # minutes (non-race only)
  "estimated_gap_non_race_min_per_km": 5.20,  # minutes (non-race only)
  "formatted_pace": "5:15",
  "formatted_gap": "5:06",
  "formatted_pace_non_race": "5:21",
  "formatted_gap_non_race": "5:12"
}
```

## Configuration

### Environment Variables (`.env`)
```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_ACCESS_TOKEN=your_access_token
STRAVA_REFRESH_TOKEN=your_refresh_token
STRAVA_TOKEN_EXPIRES_AT=1699999999
```

### Constants
- `REDIRECT_URI` = "http://localhost"
- `AUTH_URL` = "https://www.strava.com/oauth/authorize"
- `TOKEN_URL` = "https://www.strava.com/oauth/token"
- `API_BASE_URL` = "https://www.strava.com/api/v3"

## Output Format

```
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

Note: Estimated GAP is an approximation based on elevation gain.
It will differ from Strava's proprietary GAP calculation.

Race detection includes activities with workout_type=1 (race)
or names containing: race, parkrun, marathon, half marathon, 10k race, 5k race
============================================================
```

## Setup Instructions

### 1. Create Strava API Application
1. Go to https://www.strava.com/settings/api
2. Create a new application (if you don't have one)
3. Set "Authorization Callback Domain" to `localhost`
4. Note your **Client ID** and **Client Secret**

### 2. Install Dependencies
```bash
pip install requests python-dotenv
```

### 3. Configure Application
1. Create a `.env` file in the project root
2. Add your Client ID and Client Secret:
```
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
```

### 4. Run Authentication
```bash
python main.py
```
On first run, the program will:
1. Display an authorization URL
2. Prompt you to visit the URL in your browser
3. Ask you to authorize the application
4. Prompt you to paste the authorization code from the redirect URL
5. Exchange the code for tokens and save them

### 5. Subsequent Runs
After initial authentication, simply run:
```bash
python main.py
```
The program will use stored tokens and refresh them automatically if expired.

## Error Handling

### Authentication Errors
- Invalid or expired tokens → Automatic refresh attempt
- Refresh token expired → Re-run authentication flow
- Missing credentials → Display setup instructions

### API Errors
- Rate limit exceeded → Display error and wait time
- Network errors → Retry with exponential backoff
- Invalid responses → Log error and continue

### Data Errors
- Activities without gear_id → Group as "No Shoe Recorded"
- Missing elevation data → Use 0 for GAP calculation
- Invalid distance/time → Skip activity and log warning
- No race activities → Non-race metrics will equal all-runs metrics

## Limitations

1. **Estimated GAP Accuracy**: The calculated GAP is an approximation and will differ from Strava's proprietary algorithm
2. **API Rate Limits**: Large activity histories may require multiple runs due to rate limits
3. **Private Activities**: Requires `activity:read_all` scope to include private activities
4. **Gear Assignment**: Only shows shoes that were explicitly assigned to activities in Strava
5. **Activity Types**: Filters for "Run" type activities only (excludes trail runs shown as separate type if needed)

## Future Enhancements

- Export results to CSV/JSON
- Visualizations (charts/graphs)
- Compare specific time periods
- Include additional metrics (heart rate, cadence)
- Support for other activity types (cycling, swimming)
- CLI arguments for customization (date ranges, units, etc.)
- Access to actual GAP data if available in API splits
