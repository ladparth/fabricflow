# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-07-08

### Added

- **Pipeline Activities Module**: New `fabricflow.pipeline.activities` with `Copy` and `Lookup` classes
- **Lookup Activity**: Full support for lookup operations in data pipelines with dedicated executor
- **BaseActivityExecutor**: Abstract base class for activity-specific pipeline executors
- **Enhanced Templates**: New `LookupSQLServerForEach` and `LookupSQLServer` templates for lookup operations
- **Comprehensive Documentation**: Added detailed docstrings and module documentation throughout the codebase
- **Template Isolation**: Support for `isolation_level` and `query_timeout` parameters in all SQL Server templates

### Changed

- **Major Restructure**: Moved copy functionality from `fabricflow.copy` to `fabricflow.pipeline.activities.copy`
- **CopyManager → Copy**: Renamed `CopyManager` class to `Copy` (backward compatible alias maintained)
- **Template Organization**: Moved template files to `src/fabricflow/pipeline/templates/definitions/` directory
- **Enhanced Parameter Handling**: Improved parameter validation and default value assignment in activities
- **Import Structure**: Reorganized imports for better modularity and cleaner API surface

### Fixed

- **Template Parameters**: Fixed parameter passing for `query_timeout` and `isolation_level` in pipeline templates
- **Source Parameter Propagation**: Ensured source-level parameters are properly propagated to activity items

### Deprecated

- **CopyManager**: Use `Copy` class instead (alias maintained for backward compatibility)

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
