# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* Title feature and property (`title`) for the different areas
* `hide-name`, `hide-address` and `hide-size` style properties to hide specific visual elements
* `flags` can be specified at map file as well
* `size` property at root level to modify the document size

## [0.2.0] - 2023-12-14

### Added
* Style overriding by section: each section can have its own style
* Added `links/sections`, which links a section or group of between main and secondary area
* `flags` property for each section
* `opacity` style property that controls the background opacity of a linked section
* `background` style property that controls the document's background
* `grows-up` and `grows-down` flags for sections that draw an arrow indicating the growth direction of the section
* `growth-arrow-weight`, `-stroke-color` and `-fill-color` style properties for the sections growth arrows
* Method at `Style` class to easily override properties from another object: `override_properties_from`
* Method at `Style` class to get a default initialized object: `get_default`
* Property names in yaml also accept `-` instead of underscore
* `style` property to `links`, `area`, and `area/sections`
* flags are specified per section at `area/sections/`
* custom labels at specific memory addresses

### Changed
* Naming of the memory domain: Area instead of Map
* Refactored initialization of `AreaView` to pass parameters via `kwargs`
* Refactored out parameter `dwg` at `map_drawer.py`
* `size-x` and `size-y` moved to `[size]`, `x` and `y` to `[pos]`, `addresses` to `[range]`
* overridden style for areas is constructed before class declaration, and not before drawing

## [0.1.0] - 2023-11-24

* Initial release
