import importlib
import sys
from pathlib import Path

import py7zr
import requests
from playwright.sync_api import sync_playwright

from cookielist.database import CookieListDatabase
from cookielist.environment import env


class CookieListSynchronizer:
    PA_HOST = env.string("PA_HOST")
    PA_USERNAME = env.string("PA_USERNAME")
    PA_PASSWORD = env.string("PA_PASSWORD")
    PA_TOKEN = env.string("PA_TOKEN")
    PA_APP_DOMAIN = env.string("PA_APP_DOMAIN")

    @staticmethod
    def get_cookie_database():
        cookiedb = CookieListDatabase()
        if not cookiedb.is_db_created_now:
            cookiedb.anilist.session.cache.clear()
            cookiedb.synchronize(max_retries=100, force_recreate=True)
        return cookiedb

    @staticmethod
    def generate_assets() -> None:
        if "cookielist.webapp" in sys.modules:
            import cookielist.webapp as cookie_webapp

            importlib.reload(cookie_webapp)
        else:
            import cookielist.webapp as cookie_webapp

    def pa_reload_app(self) -> bool:
        response = requests.post(
            f"https://{self.PA_HOST}/api/v0/user/{self.PA_USERNAME}/webapps/{self.PA_APP_DOMAIN}/reload",
            headers={"Authorization": f"Token {self.PA_TOKEN}"},
        )
        return response.status_code == 200

    def pa_run_app_until_next_3_months(self) -> None:
        playwright_instance = sync_playwright().start()
        if env.bool("COOKIELIST_DEBUG"):
            try:
                browser_instance = playwright_instance.firefox.launch(
                    headless=False, slow_mo=2500
                )
            except Exception:
                browser_instance = playwright_instance.firefox.launch()
        else:
            browser_instance = playwright_instance.firefox.launch()
        browser_context = browser_instance.new_context()
        page = browser_context.new_page()

        page.goto(f"https://{self.PA_HOST}/")

        page.get_by_role("link", name="Log in").click()

        page.get_by_placeholder("Username or email address").click()
        page.get_by_placeholder("Username or email address").fill(self.PA_USERNAME)
        page.get_by_placeholder("Password").click()
        page.get_by_placeholder("Password").fill(self.PA_PASSWORD)
        page.get_by_role("button", name="Log in").click()

        page.get_by_role("link", name="Web", exact=True).click()
        page.locator("#id_web_app_tab_list").get_by_role(
            "link", name=self.PA_APP_DOMAIN
        ).click()
        page.get_by_role("button", name="Run until 3 months from today").click()

        browser_context.close()
        browser_instance.close()
        playwright_instance.stop()

    def synchronize(
        self,
        *,
        sync_database: bool = env.bool("SYNC_DATABASE", False),
        sync_static: bool = env.bool("SYNC_STATIC", False),
        sync_code: bool = env.bool("SYNC_CODE", False),
        sync_env: bool = env.bool("SYNC_ENVIRONMENT", False),
        reload_app: bool = env.bool("SYNC_RELOAD_APP", False),
        extend_app: bool = env.bool("SYNC_EXTEND_APP", False),
    ) -> None:
        archive_name = ".synchronize.archive.7z"
        cl_folder = env.path("COOKIELIST_STATE_FOLDER")

        with py7zr.SevenZipFile(
            cl_folder.joinpath(archive_name),
            "w",
            filters=[{"id": py7zr.FILTER_LZMA2, "preset": 9}],
        ) as archive:
            if sync_database:
                database = self.get_cookie_database().database_file
                archive.write(database, f"{cl_folder}/{database.name}")

            if sync_static:
                self.generate_assets()
                archive.writeall(cl_folder.joinpath("assets"), f"{cl_folder}/assets")
                archive.write(
                    cl_folder.joinpath("assets.json"), f"{cl_folder}/assets.json"
                )

            if sync_code:
                import cookielist

                archive.writeall(
                    Path(cookielist.__file__).parent,
                    Path(cookielist.__file__).parent.name,
                )

            if sync_env:
                archive.write(cl_folder.parent.joinpath(".env.vault"), ".env.vault")

        if sync_code or sync_database or sync_env or sync_static:
            requests.post(
                f"https://{self.PA_HOST}/api/v0/user/{self.PA_USERNAME}/files/path/home/{self.PA_USERNAME}/{env.string('PA_SOURCE_FOLDER')}/{archive_name}",
                files={"content": cl_folder.joinpath(archive_name).open("rb")},
                headers={"Authorization": f"Token {self.PA_TOKEN}"},
            )

            response = requests.post(
                f"{env.string('COOKIELIST_SITE_URL')}/_/synchronize?state={env.string('COOKIELIST_STATE_FOLDER')}",
                json=dict(
                    CL_USERNAME=env["CL_USERNAME"],
                    CL_PASSWORD=env["CL_PASSWORD"],
                    CL_ADMIN_TOKEN=env["CL_ADMIN_TOKEN"],
                ),
            )
            print(response.status_code, response.content)

        if extend_app:
            self.pa_run_app_until_next_3_months()

        if reload_app:
            self.pa_reload_app()
