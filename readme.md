*Blackboard Collaborate Ultra* Launcher
====================================

<!-- Blackboard Collaborate Ultra Launcher
     https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2021 gucci-on-fleek
-->

A simple script to automatically launch a *Blackboard Collaborate Ultra* session.

Motivation
----------

Launching *Blackboard Collaborate Ultra* takes nearly 10 clicks: 3 to login, 1 to open the class, 3 to launch *Collaborate*, and then 2 to close the annoying “Check Your Microphone/Webcam” screens. This tool reduces that to 0 clicks, and can be automatically launched at class time via `cron` or the “Task Scheduler.”

Installation
------------

You will require [`python3`](https://www.python.org/downloads/) (≥ 3.8), [Firefox](https://www.mozilla.org/en-US/firefox/download/thanks/), and [`geckodriver`](https://github.com/mozilla/geckodriver/releases/latest). This script has been tested on Windows and Linux, but it should work on macOS as well.

1. Install Firefox and `python3`.
2. Place `geckodriver` somewhere in your `PATH`.
3. Run: `pip3 install -r requirements.txt`
4. That's it!

Usage
-----

```
usage: blackboard_collaborate.py [-h] [--raspberry-pi] [--hide-ui]
                                 base_url course_id launch_button username
                                 password

╔═══════════════════════════════════════╗
║ Blackboard Collaborate Ultra Launcher ║
╚═══════════════════════════════════════╝
A simple script to automatically launch a Blackboard Collaborate Ultra session.

positional arguments:
  base_url        The base Blackboard URL. (Example:
                  'blackboard.example.edu')
  course_id       The Course's ID. Found in the query string when you open
                  the URL in Blackboard. (Example: '_12345_6')
  launch_button   The text found in the button used to open the class.
                  (Example: 'Math 101 - Course Room')
  username        Your Blackboard username.
  password        Your Blackboard password.

optional arguments:
  -h, --help      show this help message and exit
  --raspberry-pi  Enable Raspberry Pi about:config settings for hardware
                  acceleration of videos.
  --hide-ui       Hide the UI of the browser so that only Blackboard
                  Collaborate is visible.

See https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher for more.
```
