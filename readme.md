Blackboard Collaborate Ultra Launcher
====================================

<!-- Blackboard Collaborate Ultra Launcher
     https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2021 gucci-on-fleek
-->

A simple script to automatically launch a Blackboard Collaborate Ultra session.

```
usage: blackboard_collaborate.py [-h]
                                 [--profile-picture-path PROFILE_PICTURE_PATH]
                                 [--raspberry-pi]
                                 base_url course_id launch_button username
                                 password

╔═══════════════════════════════════════╗
║ Blackboard Collaborate Ultra Launcher ║
╚═══════════════════════════════════════╝
A simple script to automatically launch a Blackboard Collaborate Ultra session.

positional arguments:
  base_url              The base Blackboard URL. (Example:
                        'blackboard.example.edu')
  course_id             The Course's ID. Found in the query string when you open
                        the URL in Blackboard. (Example: '_12345_6')
  launch_button         The text found in the button used to open the class.
                        (Example: 'Math 101 - Course Room')
  username              Your Blackboard username.
  password              Your Blackboard password.

optional arguments:
  -h, --help            show this help message and exit
  --profile-picture-path PROFILE_PICTURE_PATH
                        The path to your profile picture. Should be a 400×400
                        png/jpg.
  --raspberry-pi        Enable Raspberry Pi about:config settings for hardware
                        acceleration of videos.

See https://github.com/gucci-on-fleek/Blackboard-Collaborate-Launcher for more.
```
