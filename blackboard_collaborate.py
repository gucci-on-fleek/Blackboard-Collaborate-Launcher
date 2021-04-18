#!/usr/bin/python3

# Blackboard Collaborate Ultra Launcher
# https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher
# SPDX-License-Identifier: MPL-2.0+
# SPDX-FileCopyrightText: 2021 gucci-on-fleek

import atexit
import encodings.idna  # Required for embedded zip file
from argparse import ArgumentParser, FileType
from base64 import b64encode as base64_encode
from configparser import ConfigParser, Interpolation
from mimetypes import guess_type as guess_mime_type
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Dict, Optional, Union

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.webelement import FirefoxWebElement

PrefsType = Dict[str, Union[bool, int]]
# JS has primitive types that match all of these, so it's trivial to translate them from Python to JS
JavascriptTypes = Union[int, bool, str, float, dict, list]


class WebBrowser:
    """Controls a Firefox web browser."""

    def __init__(
        self,
        extra_prefs: PrefsType = {},
        firefox_profile_path: Optional[Path] = None,
        driver_path: str = "geckodriver",
    ) -> None:
        """Initializes and launches Firefox.

        Args:
            extra_prefs (PrefsType, optional): Any additional settings to be set in
              "about:config". Defaults to {}.
            firefox_profile_path (Path, optional): A path to a Firefox profile
              directory. Defaults to None.
            driver_path (str, optional): The path to the `geckodriver` binary.
              Defaults to "geckodriver".
        """
        self.options = webdriver.firefox.options.Options()
        if firefox_profile_path:
            self.options.profile = firefox_profile_path

        self.prefs = {
            "media.navigator.streams.fake": True,  # Use a fake webcam and microphone to avoid permission issues
            # Always open links and popups inline (in the same tab/window)
            "browser.link.open_newwindow": 1,
            "browser.link.open_newwindow.restriction": 0,
            "media.autoplay.default": 0,  # Allow audio to play
        }

        for key, value in {**self.prefs, **extra_prefs}.items():
            self.options.set_preference(key, value)

        self.driver = webdriver.Firefox(
            options=self.options, executable_path=driver_path
        )
        # Search for each element for at most 45 seconds before giving up
        self.driver.implicitly_wait(45)
        self.driver.maximize_window()
        atexit.register(self.__exit__)

        self.localstorage = self._LocalStorage(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.driver.__exit__()
        atexit.unregister(self.__exit__)

    def navigate_to_url(self, url: str) -> None:
        """Navigate the browser to a url."""
        self.driver.get(url)

    def element_by_id(self, id: str) -> FirefoxWebElement:
        """Get an element on a webpage by its `id`."""
        return self.driver.find_element_by_id(id)

    def element_by_text(
        self, text: str, element_type: str = "*", full_text: bool = True
    ) -> FirefoxWebElement:
        """Select an element on a webpage by its text contents.

        Args:
            text (str): The text contents of the desired element.
            element_type (str, optional): The type of element to search for.
              Example: div, span. Defaults to "*" (any element).
            full_text (bool, optional): Specifies if `text` is full or
              partial text contents of the element. Defaults to True
              (full and exact match).
        """
        if full_text:
            xpath = f'//{element_type}[text()="{text}"]'
        else:
            xpath = f'//{element_type}[contains(text(), "{text}")]'
        return self.driver.find_element_by_xpath(xpath)

    def click(self, element: FirefoxWebElement) -> None:
        """Simulate a click on an element.

        We are using this instead of `element.click()` because this works even if the element is obscured or blocked.
        """
        self.driver.execute_script(  # Use JavaScript to click the element instead of a simulated mouse
            "arguments[0].click();", element
        )

    class _LocalStorage:
        """A class to allow `localstorage` to be accessed as a Mapping"""

        def __init__(self, outer: "WebBrowser") -> None:
            self.outer = outer

        def __setitem__(self, key: JavascriptTypes, value: JavascriptTypes) -> None:
            """Set a value in the browser's `localstorage`."""
            self.outer.driver.execute_script(
                "window.localStorage.setItem(arguments[0], arguments[1]);", key, value
            )

        def __getitem__(self, key: JavascriptTypes) -> None:
            NotImplemented

    @staticmethod
    def bytes_to_data_uri(data: bytes, mimetype: Optional[str]) -> str:
        """Convert a bytes object into a data URI that can be opened
        in a web browser.
        """
        if not mimetype:
            mimetype = "application/octet-stream"  # A somewhat reasonable fallback if we can't guess
        encoded = base64_encode(data).strip(b"=").decode("ascii")
        return f"data:{mimetype};base64,{encoded}"

    def wait_until_window_close(self) -> None:
        """Blocks until the browser window closes."""
        try:
            while True:
                sleep(5)
                self.driver.get_window_position()
        except (WebDriverException, KeyboardInterrupt):
            return


class BlackboardCollaborate(WebBrowser):
    """Accesses Blackboard Collaborate Ultra."""

    def __init__(
        self,
        base_url: str,
        *args,
        **kwargs,
    ) -> None:
        """Run all of the steps necessary to log in to Blackboard Collaborate Ultra.

        Args:
            base_url (str): The base Blackboard URL, including the protocol.
            *args, **kwargs: Extra arguments are passed to super().
        """
        self.base_url = base_url
        super().__init__(*args, **kwargs)

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
        sleep(1)  # Wait after clicking to let the page's JavaScript run

        self.click(self.element_by_text("Join", full_text=False))
        self.driver.switch_to.default_content()  # Switch out of the `iframe`

    def configure_collaborate(self, profile_picture: Optional[str] = None) -> None:
        """Configure Blackboard Collaborate Ultra.

        This is called to skip the tutorial and microphone check screens.

        Args:
            profile_picture (str, optional): The filesystem path to a profile picture.
              Defaults to None.
        """
        self.element_by_id("site-loading")
        # Skip the "Check your Microphone" screen
        self.localstorage["techcheck.initial-techcheck"] = "complete"
        self.localstorage["techcheck.status"] = "complete"
        # Skip the tutorial
        self.localstorage["ftue.announcement.introduction"] = True
        self.localstorage["chat.defaultchannel"] = "everyone"
        # Hide the annoying "X person joined/left" notifications
        self.localstorage["profile.notification.roster.visual"] = False

        if profile_picture:
            mimetype = guess_mime_type(profile_picture)
            with open(profile_picture, "rb") as file:
                profile_picture_uri = self.bytes_to_data_uri(file.read(), mimetype[0])
            self.localstorage["profile.avatar"] = profile_picture_uri

        self.click(self.element_by_id("side-panel-open"))  # Open the chat by default

    @classmethod
    def run_all(
        cls,
        *,
        base_url: str,
        username: str,
        password: str,
        hide_ui: bool = False,
        raspberry_pi: bool = False,
        course_id: str,
        launch_button: str,
        driver_path: str = "geckodriver",
        profile_picture: Optional[str] = None,
    ) -> None:
        """Run all of the steps necessary to log in to Blackboard Collaborate Ultra.

        Args:
            base_url (str): The base Blackboard URL, including the protocol.
            username (str):
            password (str):
            course_id (str): The Course’s ID. Found in the query string when
              you open the URL in Blackboard.
            launch_button (str): The text found in the button used to open the class.
            driver_path (str, optional): The path to the `geckodriver` binary.
              Defaults to "geckodriver".
            hide_ui (bool, optional): Whether or not to hide the browser's UI.
              Defaults to False.
            raspberry_pi (bool, optional): Whether or not we are are running on a Pi.
              Defaults to False.
            profile_picture (str, optional): The filesystem path to a profile picture.
              Defaults to None.
        """
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

        firefox_profile_path: Optional[Path] = None
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
                        border-bottom: 0px !important;
                    }
                    """
                )

        with cls(
            base_url,
            extra_prefs,
            firefox_profile_path,
            driver_path,
        ) as browser:
            browser.sign_in(username, password)
            browser.launch_collaborate(course_id, launch_button)
            browser.configure_collaborate(profile_picture)
            browser.wait_until_window_close()


class BooleanCoercingInterpolation(Interpolation):
    """Convert any 'stringified' boolean values into 'true' booleans."""

    BOOLEANS = {"true": True, "false": False}

    def before_get(self, parser, section, option, value, defaults) -> Union[bool, str]:  # type: ignore
        """Override the default ConfigParser behavior so that a proper Boolean
        is returned when a value containing "True"/"False" is requested.

        This is used instead of ConfigParser.getBoolean because using the Mapping
        protocol is much more "Pythonic" than using a getter.
        """
        try:
            return self.BOOLEANS[value.casefold()]
        except KeyError:
            return value


if __name__ == "__main__":
    argparser = ArgumentParser(
        description="A simple script to automatically launch a Blackboard Collaborate Ultra session.",
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
    )
    conf.read_file(arguments.config)

    try:
        BlackboardCollaborate.run_all(**conf[arguments.class_name])
    except TypeError:
        print(
            f"You appear to be missing some REQUIRED configuration keys. Please edit {arguments.config.name} and try again. \n"
        )
        raise

    exit()
