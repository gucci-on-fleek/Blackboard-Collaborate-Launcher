#! /usr/bin/python3.8

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import atexit
from base64 import b64encode
from time import sleep
from typing import Dict, Union

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


class WebBrowser:
    """Controls a Firefox web browser."""

    def __init__(self, extra_prefs: Dict[str, Union[bool, int]] = {}):
        self.options = webdriver.firefox.options.Options()

        self.prefs = {
            "media.navigator.streams.fake": True,  # Use a fake webcam and microphone to avoid permission issues
            # Always open links and popups inline (in the same tab/window)
            "browser.link.open_newwindow": 1,
            "browser.link.open_newwindow.restriction": 0,
        }

        for key, value in {**self.prefs, **extra_prefs}.items():
            self.options.set_preference(key, value)

        self.driver = webdriver.Firefox(options=self.options)
        self.driver.implicitly_wait(20)  # Try finding each element for 20 seconds
        self.driver.maximize_window()
        atexit.register(self.__exit__)

    def __enter__(self):  # For a context manager (`with` statement)
        return self

    def __exit__(self, *args):
        self.driver.__exit__()
        atexit.unregister(self.__exit__)

    def get_url(self, url: str) -> None:
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

        We are using this instead of `element.click()` because this works even if the element is obscured or blocked
        """
        self.driver.execute_script("arguments[0].click();", element)

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
    """Accesses the Blackboard Website"""

    def __init__(
        self, base_url: str, extra_prefs: Dict[str, Union[bool, int]] = {}
    ) -> None:
        self.base_url = base_url
        super().__init__(extra_prefs)

    def sign_in(self, username: str, password: str) -> None:
        """Sign in to the Blackboard webapp."""
        self.get_url(self.base_url)

        self.element_by_id("user_id").send_keys(username)
        self.element_by_id("password").send_keys(password)
        self.click(self.element_by_id("entry-login"))

        # Wait until the homepage loads after login
        self.element_by_id("topframe.logout.label")

    def launch_collaborate(self, course_id: str, launch_button: str) -> None:
        """Launch Blackboard Collaborate Ultra."""
        self.get_url(
            f"{self.base_url}/webapps/collab-ultra/tool/collabultra?course_id={course_id}"
        )

        self.driver.switch_to.frame(self.element_by_id("collabUltraLtiFrame"))
        self.click(self.element_by_text(launch_button))
        sleep(
            1
        )  # I can't find any event to trigger the next click, so we'll need to sleep

        self.click(self.element_by_text("Join Course Room"))
        self.driver.switch_to.default_content()  # Switch out of the `iframe`

    def configure_collaborate(self, profile_picture_path: str = "") -> None:
        """Configure the Blackboard Collaborate Ultra."""
        self.element_by_id("site-loading")
        # Skip the "Check your Microphone" screen
        self.set_localstorage("techcheck.initial-techcheck", "complete")
        self.set_localstorage("techcheck.status", "complete")
        # Skip the tutorial
        self.set_localstorage("ftue.announcement.introduction", True)

        if profile_picture_path:
            with open(profile_picture_path, "rb") as file:
                encoded = b64encode(file.read()).decode("ascii")
                value = f'"data:image/{profile_picture_path[-3:]};base64,{encoded}"'
                self.set_localstorage("profile.avatar", value)


if __name__ == "__main__":
    title = " Blackboard Collaborate Ultra Launcher "
    parser = ArgumentParser(
        description=f"╔{'═'*len(title)}╗\n"
        f"║{title}║\n"
        f"╚{'═'*len(title)}╝\n"
        "A simple script to automatically launch a Blackboard Collaborate Ultra session.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "base_url", help="The base Blackboard URL. (Example: 'blackboard.example.edu')"
    )
    parser.add_argument(
        "course_id",
        help="The Course's ID. Found in the query string when you open the URL in Blackboard. (Example: '_12345_6')",
    )
    parser.add_argument(
        "launch_button",
        help="The text found in the button used to open the class. (Example: 'Math 101 - Course Room')",
    )
    parser.add_argument("username", help="Your Blackboard username.")
    parser.add_argument("password", help="Your Blackboard password.")
    parser.add_argument(
        "--profile-picture-path",
        help="The path to your profile picture. Should be a 400×400 png/jpg.",
    )
    parser.add_argument(
        "--raspberry-pi",
        help="Enable Raspberry Pi about:config settings for hardware acceleration of videos.",
        action="store_true",
    )
    args = parser.parse_args()

    if args.raspberry_pi:
        extra_prefs: Dict[str, Union[bool, int]] = {
            "layers.acceleration.force-enabled": True,
            "media.ffmpeg.vaapi.enabled": True,
            "media.mediasource.webm.enabled": False,
            "media.webm.enabled": False,
            "webgl.force-enabled": True,
        }
    else:
        extra_prefs = {}

    with BlackboardBrowser(args.base_url, extra_prefs) as browser:
        browser.sign_in(args.username, args.password)
        browser.launch_collaborate(args.course_id, args.launch_button)
        browser.configure_collaborate(args.profile_picture_path)
        browser.wait_until_window_close()
    exit()
