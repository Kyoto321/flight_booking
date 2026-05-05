import logging
import json
import random
from datetime import datetime
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.conf import settings
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from .base import BaseProvider

logger = logging.getLogger(__name__)

class AirPeacePlaywrightProvider(BaseProvider):
    name = "airpeace"
    base_url = "https://book-airpeace.crane.aero"
    
    # Session TTL in seconds (e.g., 30 minutes)
    SESSION_TTL = 1800 

    def __init__(self):
        # Use settings if the server is configured, otherwise None
        proxy_settings = getattr(settings, "SEARCH_PROXY", {})
        if proxy_settings.get("server"):
            self.proxy = proxy_settings
        else:
            self.proxy = None

    def _get_cache_key(self):
        return f"scraper_session:{self.name}"

    def _save_session(self, context):
        """Saves the browser context state to Redis."""
        state = context.storage_state()
        cache.set(self._get_cache_key(), json.dumps(state), self.SESSION_TTL)
        logger.info(f"[{self.name}] Session saved to cache.")

    def _load_session(self):
        """Loads the browser context state from Redis."""
        state_json = cache.get(self._get_cache_key())
        if state_json:
            logger.info(f"[{self.name}] Session loaded from cache.")
            return json.loads(state_json)
        return None

    def _run_browser(self, payload):
        with sync_playwright() as p:
            # Construct the authenticated WebSocket URL for Bright Data
            server = settings.SEARCH_PROXY.get("server", "").replace("wss://", "")
            username = settings.SEARCH_PROXY.get("username", "")
            password = settings.SEARCH_PROXY.get("password", "")
            
            endpoint_url = f"wss://{username}:{password}@{server}"
            
            logger.info(f"[{self.name}] Connecting to Bright Data Scraping Browser...")
            browser = p.chromium.connect_over_cdp(endpoint_url)

            # Clean context (Scraping Browser manages its own security cookies)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            try:
                # 1. Warm up: Visit home page first (The "Human Path")
                logger.info(f"[{self.name}] Warming up: Visiting home page...")
                page.goto("https://www.flyairpeace.com/", wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(5000)

                # 2. Navigate to booking engine
                logger.info(f"[{self.name}] Navigating to {self.base_url}/ibe/search...")
                page.goto(f"{self.base_url}/ibe/search", wait_until="domcontentloaded", timeout=90000)
                
                # 3. Handle Cloudflare and Loading states (Enhanced Loop)
                logger.info(f"[{self.name}] Waiting for Scraping Browser to solve and load...")
                for _ in range(25): # Up to 75 seconds
                    title = page.title()
                    logger.info(f"[{self.name}] Current Title: {title}")
                    
                    # If we have a stable "Air Peace" title without "Just a moment"
                    if "Air Peace" in title and "moment" not in title.lower() and "momento" not in title.lower():
                        # Wait a tiny bit more for SPA mounting
                        page.wait_for_timeout(3000)
                        break
                    page.wait_for_timeout(3000)
                
                logger.info(f"[{self.name}] ✅ Page stabilized! Proceeding...")

                # Small settling pause for the JS app to boot up
                page.wait_for_timeout(7000)

                # 3. Wake up the App (Handle Cookie Banners or Splash Screens)
                try:
                    logger.info(f"[{self.name}] Checking for cookie banners or splash screens...")
                    # Look for anything that says "Accept", "Allow", or "Got it"
                    cookie_btn = page.locator("button:has-text('Accept'), button:has-text('Allow'), button:has-text('Got it'), .cookie-button").first
                    if cookie_btn.is_visible(timeout=3000):
                        logger.info(f"[{self.name}] Clicking cookie banner...")
                        cookie_btn.click()
                        page.wait_for_timeout(2000)
                except Exception:
                    pass

                # 4. Wait for form to be ready (Increased timeout for heavy SPA)
                logger.info(f"[{self.name}] Waiting for search form to mount...")
                try:
                    # Use PURE CSS selectors to avoid parsing errors
                    origin_selector = "input:visible, [role='combobox']:visible, .port-item, .selection-item, .js-origin-input"
                    page.wait_for_selector(origin_selector, timeout=45000)
                    logger.info(f"[{self.name}] ✅ Form/App loaded!")
                except Exception as e:
                    logger.warning(f"[{self.name}] Form mount timeout. Current URL: {page.url}")
                    # Log more content for debugging
                    logger.warning(f"[{self.name}] Page Body Snippet: {page.locator('body').inner_text()[:500]}")
                    raise e
                
                # Small pause to let any JS initialization finish
                page.wait_for_timeout(2000)
                
                # 3. Fill Form
                logger.info(f"[{self.name}] Attempting to fill search form...")
                
                # 3. Fill Form (Search & Confirm Path)
                logger.info(f"[{self.name}] Interacting with form...")
                
                try:
                    # 1. Trip Type
                    page.locator("label[for='one-way']").first.click(force=True)
                    page.evaluate("document.getElementById('tripType').value = 'ONE_WAY'")
                    page.wait_for_timeout(1000)

                    # 2. Origin
                    logger.info(f"[{self.name}] Selecting Origin: {payload['origin']}")
                    page.locator("button[data-id='firstDepPort']").first.click()
                    page.wait_for_selector(".dropdown-menu.show:visible", timeout=5000)
                    page.locator(".dropdown-menu.show:visible input[type='search'], .dropdown-menu.show:visible input[type='text']").first.fill(payload["origin"])
                    page.wait_for_timeout(500)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(1000)
                    page.keyboard.press("Escape")

                    # 3. Destination
                    logger.info(f"[{self.name}] Selecting Destination: {payload['destination']}")
                    page.locator("button[data-id='firstArrPort']").first.click()
                    page.wait_for_selector(".dropdown-menu.show:visible", timeout=5000)
                    page.locator(".dropdown-menu.show:visible input[type='search'], .dropdown-menu.show:visible input[type='text']").first.fill(payload["destination"])
                    page.wait_for_timeout(500)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(1000)
                    page.keyboard.press("Escape")

                    # 4. Date (Parse from payload - support both travel_date and departure_date)
                    import datetime
                    date_val = payload.get("travel_date") or payload.get("departure_date")
                    
                    try:
                        p_date = datetime.datetime.strptime(date_val, "%Y-%m-%d")
                    except Exception:
                        p_date = datetime.datetime.now() + datetime.timedelta(days=10)
                    
                    formatted_date = p_date.strftime("%d %b %Y")
                    logger.info(f"[{self.name}] Setting Date: {formatted_date}")
                    
                    # Focus and Click to wake up the calendar
                    page.locator("#oneWayDepartureDate").first.click(force=True)
                    page.wait_for_timeout(500)
                    page.evaluate(f"document.getElementById('oneWayDepartureDate').value = '{formatted_date}'")
                    page.evaluate("document.getElementById('oneWayDepartureDate').dispatchEvent(new Event('change', { bubbles: true }))")
                    page.evaluate("document.getElementById('oneWayDepartureDate').dispatchEvent(new Event('blur', { bubbles: true }))")
                    page.keyboard.press("Escape")
                    
                except Exception as e:
                    logger.warning(f"[{self.name}] Form interaction issue: {e}")
                
                page.wait_for_timeout(2000)

                # 4. Submit
                logger.info(f"[{self.name}] Submitting search...")
                
                # Click the specific JS-bound submit button
                submit_btn = page.locator(".js-submit-button, .availabilityRequest").first
                submit_btn.click(force=True)
                
                # Small pause and then press Enter as a backup
                page.wait_for_timeout(2000)
                page.keyboard.press("Enter")

                # If URL still hasn't changed, try JS submission
                if "/ibe/search" in page.url:
                    logger.info(f"[{self.name}] Button click ignored, trying JS form submission...")
                    page.evaluate("document.getElementById('availabilityForm').submit()")
                
                # 5. Wait for results
                logger.info(f"[{self.name}] Waiting for results page...")
                try:
                    page.wait_for_function("() => !window.location.href.includes('/ibe/search')", timeout=30000)
                    page.wait_for_load_state("domcontentloaded", timeout=30000)
                except Exception:
                    logger.warning(f"[{self.name}] URL did not change.")
                
                # Try to find any result indicator, but don't crash if not found
                try:
                    page.wait_for_selector("text=Select, text=Price, .flight-list, .js-flight-item", timeout=15000)
                    logger.info(f"[{self.name}] ✅ Results detected!")
                except Exception:
                    logger.warning(f"[{self.name}] Could not find specific results markers.")
                
                html_content = page.content()
                logger.info(f"[{self.name}] Results capture complete. HTML length: {len(html_content)}")
                
                # Debug snippet
                body_text = page.locator("body").inner_text()[:500].replace("\n", " ")
                logger.info(f"[{self.name}] Results Body Snippet: {body_text}")
                
                return html_content

            except Exception as e:
                logger.error(f"[{self.name}] Browser automation failed: {e}")
                return page.content() # Return whatever we have
            finally:
                browser.close()

    def _parse_html(self, html, payload):
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
    def _parse_html(self, html, payload):
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        # 1. Main Journeys (Broadened selector to ensure we catch every row)
        journeys = soup.select(".js-journey, .booking-item, [class*='journey-row']")
        if not journeys:
            # Fallback for some Crane versions
            journeys = soup.select(".flight-list-item")
        
        for journey in journeys:
            try:
                # 2. Times
                time_elements = journey.select(".time")
                if len(time_elements) < 2: continue
                dep_time = time_elements[0].get_text(strip=True)
                arr_time = time_elements[1].get_text(strip=True)
                
                # 3. Flight Number
                flight_no_el = journey.select_one(".flight-no")
                flight_no = flight_no_el.get_text(strip=True) if flight_no_el else "Unknown"
                
                # 4. Price & Currency (Targeting the specific offer inside the row)
                # Crane sites often hide the real price inside a .price-best-offer or a select button
                price_el = journey.select_one(".price-best-offer, .currency-best-offer, .js-price-container .price")
                if not price_el:
                    # Fallback to looking for anything with a currency symbol in it
                    price_el = journey.select_one(".price, .currency")
                
                if not price_el: continue
                
                raw_price = price_el.get_text(strip=True)
                currency = "NGN"
                if "$" in raw_price: currency = "USD"
                
                # Clean up: "From NGN 123,456.00" -> "123456.00"
                clean_price = raw_price.replace(",", "").replace("₦", "").replace("NGN", "").replace("$", "").replace("USD", "").strip()
                if " " in clean_price:
                    clean_price = clean_price.split()[-1]
                
                try:
                    price = float(clean_price)
                except ValueError:
                    continue

                results.append({
                    "provider": self.name,
                    "airline": "Air Peace",
                    "airline_code": "P4",
                    "flight_number": flight_no,
                    "origin": payload["origin"],
                    "destination": payload["destination"],
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "price": price,
                    "currency": currency,
                    "available": True,
                })
            except Exception as e:
                logger.debug(f"[{self.name}] Parsing row error: {e}")
                continue
                
        return results

    def search(self, payload):
        try:
            logger.info(f"[{self.name}] Searching: {payload['origin']} -> {payload['destination']}")
            html = self._run_browser(payload)
            results = self._parse_html(html, payload)
            
            logger.info(f"[{self.name}] ✅ Success: Found {len(results)} flights.")
            return results
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Search failed: {e}")
            return []
            return []