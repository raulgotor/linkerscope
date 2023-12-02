# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* Style overriding by section: each section can have its own style
* `background_color` style property that controls the document's background
* Method at `Style` class to easily override properties from other object: `override_properties_from`
* Method at `Style` class to get a default initialized object: `get_default`

### Changed
* Naming of the memory domain: Area instead of Map
* `map_background_color` property name to `area_background_color`
* Refactored initialization of `SectionView` to pass parameters via `kwargs`

## [0.1.0] - 2023-11-24

* Initial release
