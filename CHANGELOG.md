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