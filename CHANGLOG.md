# Changelog

All notable changes to this project will be documented in this file.

---

## [2025-06-03]
### Added
- Bollinger Bands strategy support to the backtesting module.
- RSI strategy support to the backtesting module.
- Enhanced plotting for all strategies, including cumulative profit visualization.
- Example usage in `backtesting.py` for quick testing.

### Changed
- Improved code structure and readability in `backtesting.py`.
- Standardized function arguments and documentation.
- Updated README and documentation to reflect new strategies and usage examples.

### Fixed
- Fixed cumulative profit calculation for all strategies.
- Addressed edge cases for open positions at the end of the backtest period.
- Minor bug fixes in trade signal logic.

---

## [2025-06-01]
### Added
- MACD strategy support to the backtesting module.

### Changed
- Improved SMA strategy: ensured price series is always aligned after dropping NA values.
- Updated README and documentation to reflect new features and bug fixes.

### Fixed
- Potential index misalignment bug in SMA strategy.

---

## [Earlier Releases]
- Initial release with SMA strategy backtesting and visualization.