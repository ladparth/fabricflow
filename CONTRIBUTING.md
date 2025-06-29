# Contributing to FabricFlow

Thank you for your interest in contributing to FabricFlow! Your help is appreciated.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
    - Install dependencies:
        ```sh
        pip install -e .
        ```

2. **Write clear, concise code** and follow the existing style.
3. **Add tests** for new features or bug fixes.
    - Run tests:
        ```sh
        pytest
        ```
4. **Document your changes** in code and, if needed, in the documentation.
5. **Submit a pull request** with a clear description of your changes.

---

## Project Structure

- `src/fabricflow/` - Main package
  - `pipeline/` - Pipeline templates, execution, and utilities
  - `copy/` - Copy activity abstractions and executors
  - `core/` - Workspaces, items, connections, and capacities management
  - `log_utils.py` - Logging setup
- `tests/` - Unit tests

---

## Code of Conduct

Please be respectful and considerate in all interactions.

## Reporting Issues

- Use the [issue tracker](https://github.com/ladparth/fabricflow/issues) to report bugs or request features.
- Provide as much detail as possible.

## Questions?

Open an issue or start a discussion!

---

Thank you for helping make FabricFlow better!
