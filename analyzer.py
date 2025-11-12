"""
Activity Data Analysis Module
Processes activities and calculates pace and GAP metrics.
"""

from typing import List, Dict
from collections import defaultdict


def filter_running_activities(activities: List[Dict]) -> List[Dict]:
    """
    Filter activities to only include running activities.

    Args:
        activities: List of activity dictionaries

    Returns:
        List of running activities only
    """
    running_types = {"Run", "TrailRun", "VirtualRun"}
    return [
        activity for activity in activities
        if activity.get("type") in running_types or activity.get("sport_type") in running_types
    ]


def group_by_gear(activities: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group activities by gear_id.

    Args:
        activities: List of activity dictionaries

    Returns:
        Dictionary mapping gear_id to list of activities
        Activities without gear_id are grouped under "no_gear"
    """
    grouped = defaultdict(list)

    for activity in activities:
        gear_id = activity.get("gear_id")
        if gear_id:
            grouped[gear_id].append(activity)
        else:
            grouped["no_gear"].append(activity)

    return dict(grouped)


def calculate_average_pace(activities: List[Dict]) -> float:
    """
    Calculate average pace across activities in minutes per kilometer.

    Args:
        activities: List of activity dictionaries

    Returns:
        Average pace in minutes per kilometer
    """
    total_distance_m = 0
    total_time_s = 0

    for activity in activities:
        distance = activity.get("distance", 0)
        moving_time = activity.get("moving_time", 0)

        # Skip activities with invalid data
        if distance <= 0 or moving_time <= 0:
            continue

        total_distance_m += distance
        total_time_s += moving_time

    if total_distance_m == 0:
        return 0

    # Convert to minutes per kilometer
    pace_seconds_per_km = (total_time_s / (total_distance_m / 1000))
    pace_minutes_per_km = pace_seconds_per_km / 60

    return pace_minutes_per_km


def calculate_estimated_gap(activities: List[Dict]) -> float:
    """
    Calculate estimated Grade Adjusted Pace (GAP) in minutes per kilometer.

    This is a simplified estimation based on elevation gain. The formula uses
    an adjustment coefficient derived from research showing approximately 3.3%
    time penalty per 1% grade.

    Note: This is less accurate than Strava's proprietary GAP algorithm which
    uses segment-by-segment analysis, pace-dependent adjustments, and heart rate data.

    Args:
        activities: List of activity dictionaries

    Returns:
        Estimated GAP in minutes per kilometer
    """
    total_distance_m = 0
    total_adjusted_time_s = 0

    # Adjustment coefficient: approximately 3.3% time penalty per 1% grade
    # This means for every 10m of elevation gain per 1000m of distance,
    # the time penalty is about 3.3%
    ADJUSTMENT_COEFFICIENT = 0.033

    for activity in activities:
        distance = activity.get("distance", 0)
        moving_time = activity.get("moving_time", 0)
        elevation_gain = activity.get("total_elevation_gain", 0)

        # Skip activities with invalid data
        if distance <= 0 or moving_time <= 0:
            continue

        # Calculate elevation factor
        # elevation_gain is in meters, distance is in meters
        grade_percent = (elevation_gain / distance) * 100 if distance > 0 else 0

        # Calculate time penalty factor
        # A positive grade means running uphill, which takes longer
        elevation_factor = 1 + (grade_percent * ADJUSTMENT_COEFFICIENT)

        # Adjust time to flat-equivalent
        adjusted_time = moving_time / elevation_factor

        total_distance_m += distance
        total_adjusted_time_s += adjusted_time

    if total_distance_m == 0:
        return 0

    # Convert to minutes per kilometer
    gap_seconds_per_km = (total_adjusted_time_s / (total_distance_m / 1000))
    gap_minutes_per_km = gap_seconds_per_km / 60

    return gap_minutes_per_km


def format_pace(pace_minutes: float) -> str:
    """
    Format pace as MM:SS per km.

    Args:
        pace_minutes: Pace in minutes per kilometer

    Returns:
        Formatted pace string (e.g., "5:23")
    """
    if pace_minutes == 0:
        return "0:00"

    minutes = int(pace_minutes)
    seconds = int((pace_minutes - minutes) * 60)

    return f"{minutes}:{seconds:02d}"


def get_gear_names(client, gear_ids: List[str]) -> Dict[str, str]:
    """
    Fetch gear names from Strava API.

    Args:
        client: StravaClient instance
        gear_ids: List of gear IDs to fetch names for

    Returns:
        Dictionary mapping gear_id to gear name
    """
    gear_names = {}

    for gear_id in gear_ids:
        if gear_id == "no_gear":
            gear_names[gear_id] = "No Shoe Recorded"
            continue

        try:
            gear = client.get_gear(gear_id)
            name = gear.get("name", f"Unknown Shoe ({gear_id})")
            gear_names[gear_id] = name
        except Exception as e:
            print(f"Warning: Could not fetch gear {gear_id}: {e}")
            gear_names[gear_id] = f"Unknown Shoe ({gear_id})"

    return gear_names


def is_race(activity: Dict) -> bool:
    """
    Check if an activity is tagged as a race.

    Args:
        activity: Activity dictionary

    Returns:
        True if activity is a race, False otherwise
    """
    # Check if workout_type is 1 (race) or if name contains race indicators
    workout_type = activity.get("workout_type")
    if workout_type == 1:
        return True

    # Also check activity name for race indicators
    name = activity.get("name", "").lower()
    race_keywords = ["race", "parkrun", "marathon", "half marathon", "10k race", "5k race"]
    return any(keyword in name for keyword in race_keywords)


def filter_non_race_activities(activities: List[Dict]) -> List[Dict]:
    """
    Filter out race activities.

    Args:
        activities: List of activity dictionaries

    Returns:
        List of non-race activities
    """
    return [activity for activity in activities if not is_race(activity)]


def calculate_shoe_statistics(activities: List[Dict]) -> Dict:
    """
    Calculate comprehensive statistics for a group of activities.

    Args:
        activities: List of activity dictionaries for a specific shoe

    Returns:
        Dictionary containing statistics including all runs and non-race runs
    """
    total_distance_m = sum(a.get("distance", 0) for a in activities)
    total_distance_km = total_distance_m / 1000

    # Filter non-race activities
    non_race_activities = filter_non_race_activities(activities)

    return {
        "activity_count": len(activities),
        "total_distance_km": total_distance_km,
        "average_pace_min_per_km": calculate_average_pace(activities),
        "estimated_gap_min_per_km": calculate_estimated_gap(activities),
        "non_race_count": len(non_race_activities),
        "average_pace_non_race_min_per_km": calculate_average_pace(non_race_activities),
        "estimated_gap_non_race_min_per_km": calculate_estimated_gap(non_race_activities)
    }
