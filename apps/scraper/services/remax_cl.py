import json
import pdb
import re
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests
import unicodedata

from apps.scraper.services.browser import Browser


import requests


class RemaxScraper:

    url = "https://www.remax.cl/search/listing-search/docs/search"

    def get_list(self, page=0, transaction=261):

        page_size = 24
        skip = page * page_size

        payload = {
            "count": True,
            "skip": skip,
            "top": page_size,
            "searchMode": "any",
            "queryType": "full",
            "searchFields": "*",
            "search": "*",
            "facets": [
                "content/RegionalZone,count:500,sort:count"
            ],
            "filter": f"""
content/TenantId eq 6
and content/MacroRegionId eq 1028
and content/OnHoldListing eq false
and content/IsRegionalOffice eq false
and content/IsViewable eq true
and content/TransactionTypeUID eq {transaction}
and content/ListingClass eq 1
""",
            "minimumCoverage": 0,
            "orderby": "content/ListingPriceEuro desc"
        }

        headers = {
            "Content-Type": "application/json",
            "Origin": "https://www.remax.cl",
            "Referer": "https://www.remax.cl/listings",
            "Accept": "application/json",
        }

        r = requests.post(
            self.url,
            json=payload,
            headers=headers,
        )

        data = r.json()

        r.raise_for_status()

        if r.status_code != 200:
            print(r.status_code, r.text)
            return []

        js = r.json()

        items = js.get("value", [])

        data = []

        for item in items:

            content = item.get("content", {})
            location = content.get("Location")
            if not location:
                return None, None
            
            coords = location.get("coordinates")

            if not coords or len(coords) != 2:
                return None, None

            lng = coords[0]
            lat = coords[1]

            url = None

            for s in content.get("ShortLinks", []):
                if s["LanguageCode"] == "es-CL":
                    url = "https://www.remax.cl/" + s["ShortLink"]

            data.append({
                "url": url,
                "external_code": content.get("MLSID"),
                "lng":lng,
                "lat":lat,
            })

        return data
    
    def get_detail(self, url):
        
        browser = Browser()

        html = browser.get_html(
            url,
            wait_selector='[data-testid="listing-attributes-root"]',
            scroll=True,
            click_selector='[data-testid="description-toggle"]',
        )

        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        
        # -----------------
        # MLS / ID
        # -----------------
        mls_el = soup.select_one(
            '[data-testid="listing-mls-id"]'
        )

        mls = None

        if mls_el:
            mls = mls_el.text.replace("ID:", "").strip()
        # -----------------
        # TITLE
        # -----------------
        title_el = soup.select_one('[data-testid="listing-h1-title"]')
        title = title_el.text.strip() if title_el else None
        # -----------------
        # SUBTITLE
        # -----------------
        subtitle_el = soup.select_one(
            '[data-testid="listing-subtitle"]'
        )
        subtitle = (
            subtitle_el.text.strip()
            if subtitle_el
            else None
        )
        # -----------------
        # PRICE
        # -----------------
        price, currency = self.parse_price(soup)

        price_value = self.clean_price(price)

        currency = self.normalize_currency(currency)

        rates = self.get_rates()

        price_usd, currency = self.convert_to_usd(
            price_value,
            currency,
            rates
        )

        price_type = None

        el = soup.select_one(
            '[data-testid="card-price-type"]'
        )

        if el:
            price_type = el.get_text(
                " ",
                strip=True
            )
        # -----------------
        # ADDRESS
        # -----------------
        addr_el = soup.select_one(
            '[data-testid="listing-address"] p'
        )

        address = (
            addr_el.text.strip()
            if addr_el
            else None
        )

        # -----------------
        # DESCRIPTION
        # -----------------
        desc_el = soup.select_one(
            '[data-testid="listing-description-text"]'
        )

        description = None

        if desc_el:
            description = desc_el.get_text(
                "\n",
                strip=True,
            )

        additional_costs_el = soup.select_one('[data-testid="additional-costs-maintenance-fee-value"]')
        additional_costs = (
            additional_costs_el.text.strip()
            if additional_costs_el
            else None
        )
        # -----------------
        # ROOMS DETAILS
        # -----------------
        rooms_details = self.parse_rooms_details(soup)
        # -----------------
        # IMAGES
        # -----------------
        images = []

        for img in soup.select("img"):

            src = img.get("src")

            if not src:
                continue

            if "gryphtech" in src:
                images.append(src)
        # -----------------
        # AGENT (probable)
        # -----------------
        agent = None
        agent, office = self.parse_agent(soup)
        # -----------------
        # ATTRIBUTES
        # -----------------
        attributes = self.parse_attributes(soup)
        # -----------------
        # COMMUNITY DESCRIPTION
        # -----------------
        extras = {}
        extras.update(self.parse_listing_features(soup))
        extras.update(self.parse_community_description(soup))
        # -----------------
        # LAND USE
        # -----------------
        land_use_el = soup.select_one('[data-testid="land-info-designated-land-use-value"]')
        land_use = land_use_el.text.strip() if land_use_el else None
        # -----------------
        # VIDEO
        # -----------------
        video = self.parse_video(soup)

        return {
            "url": url,
            "title": title,
            "subtitle": subtitle,
            "price": price_usd,
            "price_type": price_type,
            "location": address,
            "code": mls,
            "description": description,
            "images": images,
            "currency": currency,
            "land_use": land_use,
            "agent": agent,
            "extras": extras,
            "office_name": office,
            "attributes": attributes,
            "rooms_details": rooms_details,
            "additional_costs": additional_costs,
            "video_url": video,
        }

    def parse_community_description(self, soup):

        result = {}

        container = soup.select_one('[data-testid="community-description-section"]')

        if not container:
            return result

        title_el = container.select_one(
            '[data-testid="community-description-title"]'
        )

        text_el = container.select_one(
            '[data-testid="community-description-text"]'
        )

        if title_el and text_el:

            title = title_el.get_text(strip=True)

            text = text_el.get_text(
                "\n\n",
                strip=True,
            )

            result[title] = [text] 

        return result

    def parse_listing_features(self, soup):

        result = {}

        section = soup.select_one(
            '[data-testid="listing-features-section"]'
        )

        if not section:
            return result

        title_el = section.select_one(
            '[data-testid="listing-features-heading"]'
        )

        if not title_el:
            return result

        title = title_el.get_text(strip=True).replace(":", "")

        features = []

        items = section.select(
            '[data-testid="listing-feature-name"]'
        )

        for item in items:

            text = item.get_text(strip=True)

            if text:
                features.append(text)

        if features:
            result[title] = features

        return result

    def parse_agent(self, soup):

        agent = None
        office = None

        card = soup.select_one("#contact-agent")

        if not card:
            return None, None

        agent_el = card.select_one('[data-testid="agent-name-link"]')
        office_el = card.select_one('[data-testid="agent-office-link"]')

        if agent_el:
            agent = agent_el.get_text(strip=True)

        if office_el:
            office = office_el.get_text(strip=True)

        return agent, office
    
    def clean_label(self, text):

        if not text:
            return None

        text = text.strip().lower()

        text = text.rstrip(":")

        text = " ".join(text.split())

        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))

        return text

    def parse_attributes(self, soup):

        attrs = {}

        root = soup.select_one('[data-testid="listing-attributes-root"]')

        if not root:
            return attrs

        items = root.select('[data-testid*="listing-attribute-"]')

        for item in items:

            label_el = item.select_one('[data-testid*="text"]')
            value_el = item.select_one('[data-testid*="value"]')

            if not label_el or not value_el:
                continue

            label = label_el.get_text(strip=True)
            value = value_el.get_text(strip=True)

            label = self.clean_label(label)

            attrs[label.lower()] = value

        return attrs
    
    def map_attributes(self, obj, attrs):

        if not attrs:
            return

        if "sup. habitable(m2)" in attrs:
            obj.total_area = self.to_float(attrs["sup. habitable(m2)"])
    
        if "m2 totales" in attrs:
            obj.land_area = self.to_float(attrs["m2 totales"])
        
        if "m2 construidos" in attrs:
            obj.covered_area = self.to_float(attrs["m2 construidos"])

        if "terreno" in attrs:
            obj.land = attrs["terreno"]

        if "estacionamientos" in attrs:
            obj.parking = attrs["estacionamientos"]
        
        if "ano/mes de construccion" in attrs:
            obj.year = attrs["ano/mes de construccion"]
        
        if "total de ambientes" in attrs:
            obj.rooms = attrs["total de ambientes"]

    def to_float(self, value):
        if not value:
            return None

        value = value.replace(".", "").replace(",", ".")
        
        try:
            return float(value)
        except:
            return None
    
    def parse_video(self, soup):

        iframe = soup.select_one(
            '[data-testid="listing-desktop-image-slider-video-frame"]'
        )

        if not iframe:
            return None

        src = iframe.get("src")

        if not src:
            return None

        src = src.split("?")[0]

        return src

    def parse_price(self, soup):

        price = None
        currency = None

        first_price_el = soup.select_one(
            '[data-testid="card-first-price"]'
        )

        if first_price_el:

            text = first_price_el.get_text(" ", strip=True)

            parts = text.split()

            if len(parts) >= 2:
                price = parts[0]
                currency = parts[1]

            return price, currency

        price_el = soup.select_one(
            '[data-testid="listing-price"]'
        )

        if price_el:

            text = price_el.get_text(" ", strip=True)

            parts = text.split()

            if len(parts) >= 2:
                price = parts[0]
                currency = parts[1]

        return price, currency

    def normalize_currency(self, currency):

        if not currency:
            return None

        currency = currency.upper()

        if currency == "UF":
            return "CLF"

        if currency == "$":
            return "CLP"

        return currency
    
    def clean_price(self, value):

        if not value:
            return None

        value = value.replace(".", "")
        value = value.replace(",", ".")

        try:
            return float(value)
        except:
            return None
    
    def get_rates(self):

        url = "https://www.remax.cl/sitesettings/settings.json"

        r = requests.get(url)

        data = r.json()

        rates = {}

        for c in data["RegionSupportedCurrencies"]:

            code = c["CurrencyCode"]

            rate = float(c["USExchangeRate"])

            rates[code] = rate

        return rates

    def convert_to_usd(self, price, currency, rates):

        if not price:
            return None

        if currency not in rates:
            return None

        rate_current = rates[currency]

        rate_usd = rates["USD"]

        price_usd = price * rate_current / rate_usd

        return price_usd, "USD"
    
    def parse_rooms_details(self, soup):

        result = []

        container = soup.select_one(
            '[data-testid="listing-rooms-list"]'
        )

        if not container:
            return None

        items = container.select(
            '[data-testid^="listing-room-item"]'
        )

        for item in items:

            type_el = item.select_one(
                '[data-testid^="listing-room-type"]'
            )

            value_el = item.select_one(
                '[data-testid^="listing-room-description"]'
            )

            img_el = item.select_one(
                '[data-testid^="listing-room-image"]'
            )

            if not type_el or not value_el:
                continue

            room_type = type_el.get_text(strip=True)

            try:
                room_value = int(
                    value_el.get_text(strip=True)
                )
            except:
                room_value = None

            image = None

            if img_el:
                image = img_el.get("src")

            result.append(
                {
                    "type": room_type,
                    "count": room_value,
                    "image": image,
                }
            )

        return result or None