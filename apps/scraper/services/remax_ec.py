import re
from urllib.parse import unquote
from bs4 import BeautifulSoup

from apps.scraper.services.browser import Browser


class RemaxScraper:

    # url = "https://www.remax.com.ec/alquilar-propiedades"
    base_url = "https://www.remax.com.ec/listings/buy"

    def get_list(self, page=0):

        url = f"{self.base_url}?page={page}&pageSize=24&in:typeId=3,5,6,7,11,13,16,17,18,19,20,21,22,23,24,25,26,15"

        browser = Browser()

        html = browser.get_html(url, wait_selector="qr-card-property", scroll=True)

        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")

        items = soup.select("qr-card-property")

        data = []

        for item in items:

            link = item.select_one("a")

            if not link:
                continue

            url = "https://www.remax.com.ec" + link.get("href")

            data.append({
                "url": url
            })

        return data


    def parse_features(self, soup):

        data = {}

        items = soup.select("#second-item .column-item")

        for item in items:

            icon = item.select_one("div.icon")

            if not icon:
                continue

            key = icon.get("id")

            text_el = item.select_one(".feature-detail")

            # caso especial antiguedad
            if not text_el:
                text_el = item.select_one(".feature-detail-text")

            if not key or not text_el:
                continue

            text = text_el.get_text(" ", strip=True).lower()

            # quitar etiquetas tipo "superficie total:"
            if ":" in text:
                text = text.split(":", 1)[1].strip()

            if key in [
                "suitable-credit",
                "offer-financing",
                "suitable-professional",
            ]:
                value = self.parse_bool(text)

            # ---------- NUMBER ----------
            else:
                value = self.parse_number(text)

            data[key] = value

        return data

    def parse_number(self, value):

        if not value:
            return None

        value = value.strip()

        # quitar unidades
        value = value.replace("m²", "")
        value = value.replace("m2", "")

        # dejar solo números y separadores
        value = re.sub(r"[^0-9.,]", "", value)

        # caso raro: 1.329.03 → 1329.03
        if value.count(".") > 1:
            parts = value.split(".")
            value = "".join(parts[:-1]) + "." + parts[-1]

        # cambiar coma por punto
        value = value.replace(",", ".")

        try:
            return float(value)
        except:
            return None

    def get_description(self, soup):

        desc_list = soup.select(
            "qr-card-details-prop h3.title-description"
        )

        if not desc_list:
            return None

        if len(desc_list) == 1:
            return desc_list[0].get_text("\n", strip=True)

        return desc_list[1].get_text("\n", strip=True)

    def parse_mls(self, soup):

        el = soup.select_one("#publication-code")

        if not el:
            return None

        text = el.get_text(strip=True)

        if ":" in text:
            text = text.split(":", 1)[1].strip()

        return text

    def parse_location(self, soup):

        el = soup.select_one("#ubication-text")

        if not el:
            return None

        return el.get_text(strip=True)


    def parse_bool(self, text):

        if not text:
            return None

        text = text.strip().lower()

        if text in ["si", "sí", "yes", "true", "1"]:
            return True

        if text in ["no", "false", "0"]:
            return False

        return None

    def parse_coordinates(self, soup):

        # ----- caso 1: static map (img) -----
        img = soup.select_one("#map-static-img")
        print("""""""""""""")
        print(img)
        if img:

            src = img.get("src", "")
            src = unquote(src)
            m = re.search(r"markers=.*?\|(-?\d+\.\d+),(-?\d+\.\d+)", src)
            print("""""""""""""")
            print(m)
            if m:
                lat = float(m.group(1))
                lng = float(m.group(2))
                return lat, lng

        # ----- caso 2: iframe embed -----
        iframe = soup.select_one("#map-embed")
        print("""""""""""""")
        print(iframe)
        if iframe:

            src = iframe.get("src", "")

            # q=0.34158265900383,-78.149984478951
            m = re.search(r"q=(-?\d+\.\d+),(-?\d+\.\d+)", src)

            if m:
                lat = float(m.group(1))
                lng = float(m.group(2))
                return lat, lng

        return None, None

    def parse_extra_features(self, soup):

        result = {}

        container = soup.select_one("#third-item")

        if not container:
            return result

        current_group = None

        items = container.select(".column-item")

        for item in items:

            title = item.select_one(".subheading-03-bold")

            if title:
                current_group = title.get_text(strip=True)
                result[current_group] = []
                continue

            value = item.select_one(".subheading-03-regular")

            if value and current_group:

                text = value.get_text(strip=True)

                result[current_group].append(text)

        return result

    def parse_office(self, soup):

        result = {}

        container = soup.select_one("qr-card-info-office")

        if not container:
            return result

        name = container.select_one('[itemprop="name"]')
        address = container.select_one('[itemprop="address"]')
        img = container.select_one("img")

        if name:
            result["name"] = name.get_text(strip=True)

        if address:
            result["address"] = address.get_text(strip=True)

        if img:
            result["image"] = img.get("src")

        return result

    def get_detail(self, url):

        browser = Browser()

        html = browser.get_html(
            url,
            wait_selector="qr-card-info-prop",
            scroll=True,
        )

        if not html:
            return None
    
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1")

        text = soup.get_text(" ", strip=True)
        price = soup.select_one("#price-container p")
        agent_el = soup.select_one(
            "card-contact-details .card-agent__name"
        )

        agent = None

        if agent_el:
            agent = agent_el.text.strip()

        features = self.parse_features(soup)

        description = self.get_description(soup)
        
        images = []

        for img in soup.select("img"):

            src = img.get("src")

            if not src:
                continue

            if "cloudfront" in src:
                images.append(src)
        
        code = self.parse_mls(soup)
        location = self.parse_location(soup)
        lat, lng = self.parse_coordinates(soup)
        extras = self.parse_extra_features(soup)
        office = self.parse_office(soup)
        print("office: ",office)
        # print("price: ",price)
        # print("images: ",images)
        # print("agent: ",agent)

        return {
            "url": url,
            "title": title.text.strip() if title else None,
            "price": price.text.strip() if price else None,
            "images": images,
            "agent": agent,
            "extras": extras,
            "description": description,
            "code": code,
            "location": location,
            "lat": lat,
            "lng": lng,
            "land_area": features.get("lot-surface"),
            "total_area": features.get("total-surface"),
            "covered_area": features.get("cover-surface"),
            "semi_covered_area": features.get("semi-cover-surface"),
            "rooms": features.get("rooms"),
            "bathrooms": features.get("bathrooms"),
            "bedrooms": features.get("bedrooms"),
            "suitable_credit": features.get("suitable-credit"),
            "offer_financing": features.get("offer-financing"),
            "suitable_professional": features.get("suitable-professional"),
            "parking": features.get("garage"),
            "antiquity": features.get("antiquity"),
            "half_bathrooms": features.get("toilettes"),
            "property_floors": features.get("flats-on-the-property"),
            "expenses": features.get("expenses"),

            "office_name" : office.get("name"),
            "office_address" : office.get("address"),
            "office_image" : office.get("image"),

    

        }

    def scrape_all(self):

        results = []

        for page in range(1, 4):

            items = self.get_list(page)

            for item in items:

                detail = self.get_detail(item["url"])

                results.append(detail)

        return results