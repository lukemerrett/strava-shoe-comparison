#!/usr/bin/env python3
"""
Strava Shoe Comparison Tool
Analyzes running activities from the last 12 months grouped by shoes.
"""

import os
import sys
import time
from datetime import datetime, timedelta

import auth
from strava_client import StravaClient
from analyzer import (
    filter_running_activities,
    group_by_gear,
    get_gear_names,
    calculate_shoe_statistics,
    format_pace
)


def ensure_authentication() -> tuple[str, str, str]:
    """
    Ensure user is authenticated, handling initial auth and token refresh.

    Returns:
        Tuple of (access_token, client_id, client_secret)
    """
    # Load credentials
    credentials = auth.load_credentials()

    if not credentials:
        print("No Strava API credentials found.")
        print("\nTo get your credentials:")
        print("1. Go to https://www.strava.com/settings/api")
        print("2. Create an application (or use an existing one)")
        print("3. Set 'Authorization Callback Domain' to 'localhost'")
        print("4. Note your Client ID and Client Secret")
        print("\nCreate a .env file with:")
        print("STRAVA_CLIENT_ID=your_client_id")
        print("STRAVA_CLIENT_SECRET=your_client_secret")
        sys.exit(1)

    client_id = credentials['client_id']
    client_secret = credentials['client_secret']

    # Check for existing tokens
    tokens = auth.load_tokens()

    # If we have tokens, check if they need refreshing
    if tokens:
        expires_at = tokens.get('expires_at', 0)
        current_time = int(time.time())

        # If token expires in less than 5 minutes, refresh it
        if expires_at - current_time < 300:
            print("Access token expired or expiring soon. Refreshing...")
            try:
                new_tokens = auth.refresh_access_token(
                    client_id,
                    client_secret,
                    tokens['refresh_token']
                )
                auth.save_tokens(new_tokens)
                print("Token refreshed successfully.\n")
                return new_tokens['access_token'], client_id, client_secret
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                print("Will need to re-authenticate.\n")
                tokens = None

    # If no valid tokens, perform initial authentication
    if not tokens:
        print("No valid access token found. Starting authentication flow...\n")

        # Generate authorization URL
        auth_url = auth.get_authorization_url(client_id)

        print("Please visit this URL in your browser to authorize the application:")
        print(f"\n{auth_url}\n")
        print("After authorizing, you will be redirected to a URL like:")
        print("http://localhost/?state=&code=AUTHORIZATION_CODE&scope=read,activity:read_all")
        print("\nCopy the entire URL or just the AUTHORIZATION_CODE part.")

        redirect_url = input("\nPaste the redirect URL or authorization code: ").strip()

        # Extract code from URL if full URL was pasted
        if "code=" in redirect_url:
            code = redirect_url.split("code=")[1].split("&")[0]
        else:
            code = redirect_url

        # Exchange code for tokens
        try:
            tokens = auth.exchange_code_for_token(client_id, client_secret, code)
            auth.save_tokens(tokens)
            print("\nAuthentication successful! Tokens saved.\n")
            return tokens['access_token'], client_id, client_secret
        except Exception as e:
            print(f"\nAuthentication failed: {e}")
            sys.exit(1)

    return tokens['access_token'], client_id, client_secret


def display_results(results: list[dict]) -> None:
    """
    Display shoe comparison results in a formatted table.

    Args:
        results: List of shoe statistics dictionaries
    """
    print("\n" + "=" * 60)
    print("Strava Running Shoe Comparison (Last 12 Months)")
    print("=" * 60)

    if not results:
        print("\nNo running activities found in the last 12 months.")
        return

    # Sort by total distance (most used shoes first)
    results.sort(key=lambda x: x['total_distance_km'], reverse=True)

    for shoe in results:
        print(f"\n{shoe['gear_name']}")
        print(f"  Total Activities: {shoe['activity_count']} ({shoe['non_race_count']} non-race)")
        print(f"  Total Distance: {shoe['total_distance_km']:.1f} km")
        print(f"\n  All Runs:")
        print(f"    Average Pace: {shoe['formatted_pace']} /km")
        print(f"    Estimated GAP: {shoe['formatted_gap']} /km")
        print(f"\n  Non-Race Runs:")
        print(f"    Average Pace: {shoe['formatted_pace_non_race']} /km")
        print(f"    Estimated GAP: {shoe['formatted_gap_non_race']} /km")

    print("\n" + "=" * 60)
    print("\nNote: Estimated GAP is an approximation based on elevation gain.")
    print("It will differ from Strava's proprietary GAP calculation.")
    print("\nRace detection includes activities with workout_type=1 (race)")
    print("or names containing: race, parkrun, marathon, half marathon, 10k race, 5k race")
    print("=" * 60 + "\n")


def main():
    """Main program execution."""
    print("Strava Shoe Comparison Tool")
    print("=" * 60)

    # Authenticate
    access_token, client_id, client_secret = ensure_authentication()

    # Initialize client
    client = StravaClient(access_token)

    # Verify authentication
    try:
        athlete = client.get_athlete()
        print(f"Authenticated as: {athlete.get('firstname')} {athlete.get('lastname')}")
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        print("Please check your credentials and try again.")
        sys.exit(1)

    # Calculate date range (last 12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"Fetching activities from {start_date.date()} to {end_date.date()}...")

    # Fetch all activities
    try:
        all_activities = client.get_all_activities_since(start_date)
        print(f"Retrieved {len(all_activities)} total activities.")
    except Exception as e:
        print(f"Failed to fetch activities: {e}")
        sys.exit(1)

    # Filter for running activities
    running_activities = filter_running_activities(all_activities)
    print(f"Found {len(running_activities)} running activities.")

    if not running_activities:
        print("\nNo running activities found in the last 12 months.")
        sys.exit(0)

    # Group by gear
    print("\nGrouping activities by shoes...")
    grouped_activities = group_by_gear(running_activities)

    # Get gear names
    print("Fetching shoe information...")
    gear_names = get_gear_names(client, list(grouped_activities.keys()))

    # Calculate statistics for each shoe
    print("Calculating statistics...\n")
    results = []

    for gear_id, activities in grouped_activities.items():
        stats = calculate_shoe_statistics(activities)
        stats['gear_id'] = gear_id
        stats['gear_name'] = gear_names.get(gear_id, f"Unknown ({gear_id})")
        stats['formatted_pace'] = format_pace(stats['average_pace_min_per_km'])
        stats['formatted_gap'] = format_pace(stats['estimated_gap_min_per_km'])
        stats['formatted_pace_non_race'] = format_pace(stats['average_pace_non_race_min_per_km'])
        stats['formatted_gap_non_race'] = format_pace(stats['estimated_gap_non_race_min_per_km'])
        results.append(stats)

    # Display results
    display_results(results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
