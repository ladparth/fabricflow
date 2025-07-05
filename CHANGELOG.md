# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-07-05

### Added

- **ServicePrincipalTokenProvider** for Microsoft Fabric REST API authentication using Azure Service Principal credentials

### Changed

- **CopyManager** and sink classes (`ParquetFileSink`, `LakehouseTableSink`) with improved parameter handling and error checking

### Removed

- `tests/copy/test_utils.py` (redundant test file)

## [0.1.0] - 2025-06-29

### Added

- Initial release of the `fabricflow` package.
- Core modules for data pipeline management, including:
  - Copy utilities (executors, job management, sinks, sources)
  - Core utilities (capacities, connections, items, workspaces)
  - Pipeline execution and templates
- Templates for SQL Server to Lakehouse and Parquet file copy operations.
- Basic logging utilities.
