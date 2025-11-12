"""
Strava API Client
Provides interface to Strava API v3 endpoints.
"""

import time
import requests
from typing import List, Dict, Optional
from datetime import datetime


API_BASE_URL = "https://www.strava.com/api/v3"


class StravaClient:
    """Client for interacting with Strava API v3."""

    def __init__(self, access_token: str):
        """
        Initialize Strava API client.

        Args:
            access_token: Valid Strava OAuth access token
        """
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })

    def get_athlete(self) -> Dict:
        """
        Get authenticated athlete information.

        Returns:
            Athlete data dictionary

        Raises:
            requests.RequestException: If the API request fails
        """
        response = self.session.get(f"{API_BASE_URL}/athlete")
        response.raise_for_status()
        return response.json()

    def get_activities(
        self,
        after: Optional[int] = None,
        before: Optional[int] = None,
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict]:
        """
        Get paginated list of athlete activities.

        Args:
            after: Epoch timestamp to fetch activities after
            before: Epoch timestamp to fetch activities before
            page: Page number (default 1)
            per_page: Number of activities per page (default 30, max 200)

        Returns:
            List of activity dictionaries

        Raises:
            requests.RequestException: If the API request fails
        """
        params = {
            "page": page,
            "per_page": per_page
        }

        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        response = self.session.get(f"{API_BASE_URL}/athlete/activities", params=params)
        response.raise_for_status()

        return response.json()

    def get_all_activities_since(self, since_date: datetime) -> List[Dict]:
        """
        Get all activities since a specific date, handling pagination automatically.

        Args:
            since_date: Fetch activities after this date

        Returns:
            List of all activity dictionaries since the date

        Raises:
            requests.RequestException: If the API request fails
        """
        after_timestamp = int(since_date.timestamp())
        all_activities = []
        page = 1
        per_page = 200  # Maximum allowed by API

        while True:
            print(f"Fetching activities page {page}...")
            activities = self.get_activities(
                after=after_timestamp,
                page=page,
                per_page=per_page
            )

            if not activities:
                break

            all_activities.extend(activities)

            # If we got fewer activities than requested, we've reached the end
            if len(activities) < per_page:
                break

            page += 1

            # Be respectful of rate limits - add small delay between requests
            time.sleep(0.5)

        return all_activities

    def get_gear(self, gear_id: str) -> Dict:
        """
        Get gear (equipment) details by ID.

        Args:
            gear_id: Strava gear ID

        Returns:
            Gear data dictionary

        Raises:
            requests.RequestException: If the API request fails
        """
        response = self.session.get(f"{API_BASE_URL}/gear/{gear_id}")
        response.raise_for_status()
        return response.json()

    def get_activity_by_id(self, activity_id: int) -> Dict:
        """
        Get detailed activity information by activity ID.

        Args:
            activity_id: Strava activity ID

        Returns:
            Detailed activity data dictionary

        Raises:
            requests.RequestException: If the API request fails
        """
        response = self.session.get(f"{API_BASE_URL}/activities/{activity_id}")
        response.raise_for_status()
        return response.json()
