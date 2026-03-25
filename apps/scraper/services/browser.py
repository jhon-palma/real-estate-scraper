import pdb

from playwright.sync_api import sync_playwright


class Browser:

    def get_html(
        self,
        url,
        wait_selector=None,
        scroll=False,
        retries=3,
        click_selector=None,
    ):

        for i in range(retries):

            try:

                with sync_playwright() as p:

                    browser = p.chromium.launch(
                        headless=False
                    )

                    page = browser.new_page()

                    try:

                        page.goto(
                            url,
                            wait_until="networkidle",
                            timeout=120000
                        )

                        if wait_selector:

                            page.wait_for_selector(
                                wait_selector,
                                timeout=60000
                            )
                        

                    except Exception as e:

                        print("ERROR LOADING", url, e)

                        browser.close()
                        return None

                    if click_selector:
                        
                        try:
                            page.click(click_selector)
                            page.wait_for_timeout(1000)
                        except:
                            pass

                    if scroll:

                        for _ in range(3):
                            page.mouse.wheel(0, 3000)
                            page.wait_for_timeout(2000)

                    html = page.content()

                    browser.close()

                    return html

            except Exception:

                print("RETRY", i + 1, url)

        return None
# class Browser:

#     def get_html(self, url, retries=3):

#         for i in range(retries):

#             try:

#                 with sync_playwright() as p:

#                     browser = p.chromium.launch(
#                         headless=False
#                     )

#                     page = browser.new_page()

#                     try:
#                         page.goto(
#                             url,
#                             wait_until="networkidle",
#                             timeout=120000
#                         )

#                         page.wait_for_selector(
#                             "qr-card-property",
#                             timeout=60000
#                         )
#                     except Exception as e:

#                         print("ERROR LOADING", url, e)

#                         browser.close()
#                         return None

#                     # scroll para cargar más
#                     for _ in range(3):
#                         page.mouse.wheel(0, 3000)
#                         page.wait_for_timeout(2000)

#                     html = page.content()

#                     browser.close()

#                     return html
#             except Exception as e:

#                 print("RETRY", i + 1, url)

#         return None