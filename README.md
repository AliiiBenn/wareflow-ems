# Simple Employee Manager

A desktop application for managing warehouse employee data, including certifications (CACES), medical visits, and training records.

## Project Structure

This repository contains the source code and build tools for the Employee Management System. The application is designed to run on shared network drives with SQLite-based data storage and Flet-based UI.

## Development

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) for package management

### Setup

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest
```

### Project Documentation

See [docs/](docs/) for detailed project documentation:
- [PROJECT.md](docs/PROJECT.md) - Complete specifications
- [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - Architecture and organization

### Building

```bash
python build/build.py
```

## Deployment

Use the bootstrapper to create new project instances:

```bash
python bootstrapper/main.py create [project_name]
```

## Architecture

The application follows an **entity-oriented** design where each domain concept (Employee, Lock, Export) has its own module containing all related logic:

- `src/employee/` - Employee models, queries, calculations, and validations
- `src/lock/` - Locking mechanism for concurrent access control
- `src/export/` - Excel export functionality
- `src/ui/` - Flet-based desktop interface

Models contain their own business logic (classmethods, properties) following Pythonic OOP principles rather than layered service/repository patterns.

## License

MIT
