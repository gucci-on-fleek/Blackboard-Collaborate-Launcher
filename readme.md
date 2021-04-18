*Blackboard Collaborate Ultra* Launcher
======================================

<!-- Blackboard Collaborate Ultra Launcher
     https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2021 gucci-on-fleek
-->

A simple script to automatically launch a *Blackboard Collaborate Ultra* session. Zero clicks and zero interaction required.

<details><summary>View Demo Video</summary>
<video src="https://user-images.githubusercontent.com/49086429/115156872-b1224c00-a043-11eb-9f13-cd8f127dfe02.mp4" title="Video demonstration of the script present in this repository."></video> <!-- Licence for Example_1.mp4: MPL-2.0+ OR CC-BY-SA-4.0+ --></details>

Motivation
----------

Launching *Blackboard Collaborate Ultra* takes nearly 10 clicks: 3 to login, 1 to open the class, 3 to launch *Collaborate*, and then 2 to close the annoying “Check Your Microphone/Webcam” screens. This tool reduces that to **0 clicks** and requires **zero interaction**, so it can be automatically launched at class time via `cron` or the “Task Scheduler.”

Installation
------------

You will require [`python3`](https://www.python.org/downloads/) (≥ 3.8), [Firefox](https://www.mozilla.org/en-US/firefox/download/thanks/), and [`geckodriver`](https://github.com/mozilla/geckodriver/releases/latest). This script has been tested on Windows and Linux, but it should work on macOS as well.

1. Install Firefox and `python3`.
2. Place `geckodriver` somewhere in your `PATH`, or add its location to the config file.
3. Run: `pip3 install -r requirements.txt`
4. That’s it!

### Note
I have used this script for an entire semester with zero issues; however, it is heavily reliant on the exact structure of the _Blackboard_ website, which may change at any time. Nevertheless, I can confirm that this script is fully functional as of April 2021. If anything changes to make this script stop working, feel free to raise an issue or submit a PR.

Usage
-----
### Script
```text
usage: blackboard_collaborate.py [-h] [-c CONFIG] class_name

A simple script to automatically launch a Blackboard Collaborate Ultra session.

positional arguments:
  class_name            The name of the class to launch, as specified in the config file.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        The configuration file to use. Defaults to “./blackboard_collaborate.ini”.

See https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher for full documentation.
```

### Config File
```ini
[General]                                 # Place global settings in the [General]
                                          # Section. They will be applied to all classes.

base_url        = https://bb.example.edu  # The base Blackboard URL. (Required) 
                                          # You must include “https://” or “http://”

username        = john.smith              # Your Blackboard Username. (Required)

password        = SuperSecretPassword     # Your Blackboard Password. (Required)

hide_ui         = False                   # Hide the UI of the browser so that only 
                                          # Blackboard Collaborate is visible. (Optional)

raspberry_pi    = False                   # Enable hardware acceleration of videos on
                                          # the Raspberry Pi. (Optional)

profile_picture = C:\image.png            # A path to the profile picture to use in
                                          # Blackboard Collaborate. (Optional)

driver_path     = C:\geckodriver.exe      # The path to geckodriver. (Optional)

[ClassOne]                                # The class name. You can have unlimited  
                                          # classes; just give each its own [section]. 

course_id       = _12345_6                # The Course’s ID. Found in the query string
                                          # in the Blackboard URL. (Required)
                                        
launch_button   = Math 101 - Course Room  # The text found in the button used to
                                          # open the class. (Required)

[Biology]                                 # Launch this with
                                          # “blackboard_collaborate.py Biology”.

cOuRsE_iD       = _98765_4                # All keys are case-insensitive.
launch_button   = Biology 300 - Lecture
hide_ui         = True                    # You can override any setting from [General].
```

Licence
-------

Unless otherwise stated, all files are licensed under the [Mozilla Public Licence](licence.txt), version&nbsp;2.0 or later.
