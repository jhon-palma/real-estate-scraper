import requests


class BaseScraper:

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }

    def get(self, url):

        r = requests.get(
            url,
            headers=self.headers,
            timeout=30,
        )

        print("==========================status_code==========================")
        print(r.status_code)
        print("===============================================================")

        r.raise_for_status()

        return r.text