# flight_model.py

import requests
import json

class FlightModel:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://test.api.amadeus.com"
        self.token = None

    def authenticate(self):
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            raise Exception(f"Failed to authenticate with Amadeus API: {response.text}")

    def search_flights(self, origin, destination, departure, return_date, passengers):
        """Busca voos no Amadeus API."""
        if not self.token:
            self.authenticate()

        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure,
            "returnDate": return_date,
            "adults": passengers,
            "max": 5  # Mantendo um limite para evitar sobrecarga
        }
        print("Params sent to API:", params)  # Debug
        url = f"{self.base_url}/v2/shopping/flight-offers"
        response = requests.get(url, headers=headers, params=params)
        print("API Response:", response.status_code, response.text)  # Debug

        if response.status_code == 200:
            data = response.json()
            return data.get("data", []), data.get("dictionaries", {})
        else:
            raise Exception(f"Failed to retrieve flights: {response.text}")

    def get_destinations(self):
        """Busca todas as cidades e aeroportos disponíveis no Amadeus API."""
        if not self.token:
            self.authenticate()

        url = f"{self.base_url}/v1/reference-data/locations"
        params = {
            "subType": "AIRPORT,CITY",
            "keyword": "A",
            "page[limit]": 100
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            locations = response.json().get("data", [])

            unique_destinations = set()
            for loc in locations:
                if "iataCode" in loc and "name" in loc:
                    unique_destinations.add(f"{loc['iataCode']} - {loc['name']}")

            additional_destinations = ["LIS - Lisbon", "OPO - Porto", "FNC - Funchal"]
            unique_destinations.update(additional_destinations)

            return sorted(unique_destinations)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error occurred: {e}")

        except KeyError as e:
            raise Exception(f"Unexpected response format: Missing key {e}")








