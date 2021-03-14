# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2021-03-11

### Added

- Added Garage door control server that toggles the garage door open and closed
- Added Logging Server that logs all usages of the garage to json file
- Added monitoring server to keep track of the current state of the garage door
- Added low level door sensor program to keep track of the door sensor switch
- Switch to Gitflow style development model with this release

## [0.1.1] - 2021-03-11

### Fixed

- Added CORS header: Access-Control-Allow-Origin to allow requests from originating
from the [smart-garage frontend app](https://github.com/husain3/smart-garage)

## [0.2.0] - 2021-03-11

### Added

- SG-13: Ignore json logging file and stop tracking
- SG-14: Change redis message to json format

## [0.2.1] - 2021-03-11

### Fixed

- SG-22: Create json if it doesn't exist and add json placeholders to HTTP responses if no logs exist.

## [0.3.0] - 2021-03-12

### Added

- SG-14: Create autostart script using tmuxinator to allow all servers to be booting in a tmux pane on boot.

## [0.4.0] - 2021-03-14

### Added

- SG-32: Add authentication for garage door toggle