#! /usr/bin/python3.8

# Blackboard Collaborate Ultra Launcher
# https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher
# SPDX-License-Identifier: MPL-2.0+
# SPDX-FileCopyrightText: 2021 gucci-on-fleek

import atexit
from argparse import ArgumentParser, FileType
from configparser import ConfigParser, Interpolation
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Any, Dict, Optional, Union

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

PrefsType = Dict[str, Union[bool, int]]


class WebBrowser:
    """Controls a Firefox web browser."""

    def __init__(
        self,
        extra_prefs: PrefsType = {},
        firefox_profile_path: Optional[Path] = None,
        driver_path: str = None,
    ):
        self.options = webdriver.firefox.options.Options()
        if firefox_profile_path:
            self.options.profile = firefox_profile_path

        self.prefs = {
            "media.navigator.streams.fake": True,  # Use a fake webcam and microphone to avoid permission issues
            # Always open links and popups inline (in the same tab/window)
            "browser.link.open_newwindow": 1,
            "browser.link.open_newwindow.restriction": 0,
        }

        for key, value in {**self.prefs, **extra_prefs}.items():
            self.options.set_preference(key, value)

        self.driver = webdriver.Firefox(
            options=self.options, executable_path=driver_path
        )
        # Search for each element for at least 30 seconds before giving up
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        atexit.register(self.__exit__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.driver.__exit__()
        atexit.unregister(self.__exit__)

    def navigate_to_url(self, url: str) -> None:
        """Navigate the browser to a url."""
        self.driver.get(url)

    def element_by_id(self, id: str):
        """Get an element on a webpage by its `id`."""
        return self.driver.find_element_by_id(id)

    def element_by_text(self, text: str, tag="*"):
        """Select an element on a webpage by its text contents."""
        return self.driver.find_element_by_xpath(f'//{tag}[text()="{text}"]')

    def click(self, element):
        """
        Simulate a click on an element.

        We are using this instead of `element.click()` because this works even if the element is obscured or blocked.
        """
        self.driver.execute_script(
            "arguments[0].click();", element
        )  # Use JavaScript to click the element instead of a simulated mouse

    def set_localstorage(self, key, value):
        """Set a value in the browser's `localstorage`."""
        self.driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);", key, value
        )

    def wait_until_window_close(self):
        """Blocks until the browser window closes."""
        try:
            while True:
                sleep(5)
                self.driver.get_window_position()
        except WebDriverException:
            return


class BlackboardBrowser(WebBrowser):
    """Accesses the Blackboard (Classic) Website."""

    def __init__(
        self,
        base_url: str,
        extra_prefs: PrefsType = {},
        firefox_profile_path: Optional[Path] = None,
        driver_path: str = None,
    ) -> None:
        self.base_url = base_url
        super().__init__(extra_prefs, firefox_profile_path, driver_path)

    def sign_in(self, username: str, password: str) -> None:
        """Sign in to the Blackboard Website."""
        self.navigate_to_url(self.base_url)

        self.element_by_id("user_id").send_keys(username)
        self.element_by_id("password").send_keys(password)
        self.click(self.element_by_id("entry-login"))

        # Wait until the homepage loads after login (the logout button can only appear after we have successfully logged in)
        self.element_by_id("topframe.logout.label")

    def launch_collaborate(self, course_id: str, launch_button: str) -> None:
        """Launch Blackboard Collaborate Ultra."""
        self.navigate_to_url(
            f"{self.base_url}/webapps/collab-ultra/tool/collabultra?course_id={course_id}"
        )

        self.driver.switch_to.frame(self.element_by_id("collabUltraLtiFrame"))
        self.click(self.element_by_text(launch_button))
        sleep(1)

        self.click(self.element_by_text("Join Course Room"))
        self.driver.switch_to.default_content()  # Switch out of the `iframe`

    def configure_collaborate(self) -> None:
        """
        Configure Blackboard Collaborate Ultra.

        This skips the tutorial and microphone check screens.
        """
        self.element_by_id("site-loading")
        # Skip the "Check your Microphone" screen
        self.set_localstorage("techcheck.initial-techcheck", "complete")
        self.set_localstorage("techcheck.status", "complete")
        # Skip the tutorial
        self.set_localstorage("ftue.announcement.introduction", True)

    @classmethod
    def run_all(
        cls,
        *,
        base_url,
        username,
        password,
        hide_ui=False,
        raspberry_pi=False,
        course_id,
        launch_button,
        driver_path,
    ):
        """Run all of the steps necessary to log in to Blackboard Collaborate Ultra."""
        extra_prefs: PrefsType = {}

        if raspberry_pi:
            extra_prefs.update(
                {
                    # Enable hardware acceleration
                    "layers.acceleration.force-enabled": True,
                    "media.ffmpeg.vaapi.enabled": True,
                    "webgl.force-enabled": True,
                    # The Raspberry Pi can only hardware decode h.264, so disable webm
                    "media.mediasource.webm.enabled": False,
                    "media.webm.enabled": False,
                }
            )

        if hide_ui:
            extra_prefs.update(
                {
                    "toolkit.legacyUserProfileCustomizations.stylesheets": True,  # Enable userChrome.css
                }
            )

            tempdir = TemporaryDirectory()
            atexit.register(tempdir.cleanup)
            firefox_profile_path = Path(tempdir.name)

            (firefox_profile_path / "chrome").mkdir()
            with open(
                firefox_profile_path / "chrome/userChrome.css", "wt"
            ) as user_chrome:
                user_chrome.write(
                    """
                    #nav-bar, #tabbrowser-tabs { /* Hide the URL bar and the tab bar */
                        height: 0px !important;
                        min-height: 0px !important;
                        overflow: hidden !important;
                    }
                    #navigator-toolbox { /* Match the titlebar with the BB Collab background */
                        background: #262626 !important;
                    }
                    """
                )

        with cls(
            base_url,
            extra_prefs,
            firefox_profile_path if hide_ui else None,
            driver_path,
        ) as browser:
            browser.sign_in(username, password)
            browser.launch_collaborate(course_id, launch_button)
            browser.configure_collaborate()
            browser.wait_until_window_close()


class BooleanCoercingInterpolation(Interpolation):
    """Convert any 'stringified' boolean values into 'true' booleans."""

    BOOLEANS = {"true": True, "false": False}

    def before_get(self, parser, section, option, value, defaults):
        try:
            return self.BOOLEANS[value.lower()]
        except KeyError:
            return value


if __name__ == "__main__":
    argparser = ArgumentParser(
        description=f"A simple script to automatically launch a Blackboard Collaborate Ultra session.",
        epilog="See https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher for full documentation.",
    )

    argparser.add_argument(
        "class_name",
        help="The name of the class to launch, as specified in the config file.",
    )
    argparser.add_argument(
        "-c",
        "--config",
        type=FileType("rt"),
        help="The configuration file to use. Defaults to “./blackboard_collaborate.ini”.",
        default=Path("./blackboard_collaborate.ini"),
    )

    arguments = argparser.parse_args()

    conf = ConfigParser(
        default_section="General",
        interpolation=BooleanCoercingInterpolation(),
        defaults={
            "raspberry_pi": "False",
            "hide_ui": "False",
            "driver_path": "geckodriver",
        },
    )
    conf.read_file(arguments.config)

    try:
        BlackboardBrowser.run_all(**conf[arguments.class_name])
    except TypeError:
        print(
            f"You appear to be missing some REQUIRED configuration keys. Please edit {arguments.config.name} and try again. \n"
        )
        raise

    exit()
