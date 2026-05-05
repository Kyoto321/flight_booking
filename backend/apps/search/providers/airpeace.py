import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

from .base import BaseProvider

logger = logging.getLogger(__name__)


class AirPeaceProvider(BaseProvider):
    name = "airpeace"
    base_url = "https://book-airpeace.crane.aero"

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": "https://book-airpeace.crane.aero/ibe/search",
        }

    # ---------------------------
    # STEP 1 — SESSION INIT
    # ---------------------------
    def _bootstrap_session(self):
        url = f"{self.base_url}/ibe/search"
        response = self.session.get(url, headers=self.headers, timeout=10)
        print("Bootstrap status:", response.status_code)
        print("Cookies:", self.session.cookies.get_dict())

    # ---------------------------
    # STEP 2 — FORMAT DATE
    # ---------------------------
    def _format_date(self, date_obj):
        return date_obj.strftime("%d %B %Y")

    # ---------------------------
    # STEP 3 — SEARCH REQUEST (POST FIXED)
    # ---------------------------
    def _fetch_availability(self, payload):
        url = f"{self.base_url}/ibe/availability/create"

        data = {
            "depPort": payload["origin"],
            "arrPort": payload["destination"],
            "date": self._format_date(payload["date"]),
            "tripType": "ONE_WAY",
            "passengerQuantities[0].passengerType": "ADT",
            "passengerQuantities[0].quantity": str(payload.get("adults", 1)),
        }

        headers = {
            **self.headers,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://book-airpeace.crane.aero",
        }

        response = self.session.post(
            url,
            data=data,
            headers=headers,
            timeout=15
        )

        print("Search status:", response.status_code)

        response.raise_for_status()
        return response.text

    # ---------------------------
    # STEP 4 — PARSE HTML
    # ---------------------------
    def _parse_html(self, html, payload):
        soup = BeautifulSoup(html, "html.parser")

        journeys = soup.select(".js-journey")
        print("Journeys found:", len(journeys))

        results = []

        for journey in journeys:
            flight_block = journey.select_one(".selection-item")
            if not flight_block:
                continue

            times = flight_block.select(".time")
            ports = flight_block.select(".port")
            flight_no = flight_block.select_one(".flight-no")
            duration = flight_block.select_one(".flight-duration")

            departure_time = times[0].text.strip() if len(times) > 0 else None
            arrival_time = times[1].text.strip() if len(times) > 1 else None

            origin = ports[0].text.strip() if len(ports) > 0 else payload["origin"]
            destination = ports[1].text.strip() if len(ports) > 1 else payload["destination"]

            flight_number = flight_no.text.strip() if flight_no else None
            duration_text = duration.text.strip() if duration else None

            # PRICE EXTRACTION
            price = None
            price_candidates = journey.select(".price-text-with-blocks span")

            if price_candidates and len(price_candidates) >= 2:
                try:
                    raw_price = (
                        price_candidates[-1]
                        .text.replace(",", "")
                        .replace("₦", "")
                        .strip()
                    )
                    price = float(raw_price)
                except Exception:
                    price = None

            results.append({
                "provider": "airpeace",
                "provider_key": f"airpeace_{flight_number}",
                "airline": "Air Peace",
                "airline_code": "P4",
                "flight_number": flight_number,
                "origin": origin,
                "destination": destination,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration_text,
                "price": price,
                "currency": "NGN",
                "available": True,
            })

        return results

    # ---------------------------
    # PUBLIC METHOD
    # ---------------------------
    def search(self, payload):
        try:
            print("\n=== START AIRPEACE SEARCH ===")

            # STEP 1
            print("Bootstrapping session...")
            self._bootstrap_session()

            # STEP 2
            print("Fetching availability...")
            html = self._fetch_availability(payload)

            print("\n--- HTML PREVIEW ---")
            print(html[:800])
            print("--- END PREVIEW ---\n")

            # STEP 3
            results = self._parse_html(html, payload)

            print("Parsed results count:", len(results))

            return results

        except Exception as e:
            print(f"[AirPeaceProvider ERROR]: {e}")
            return []