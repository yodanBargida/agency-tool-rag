# Project File Guide

A brief explanation of each key file and directory in the `Tools_Rag` repository.

## Root Directory
- `.env`: Contains sensitive environment variables like API keys (ignored by git).
- `.gitignore`: Specifies files and directories to be excluded from version control.
- `.python-version`: Indicates the Python version used for this project.
- `FILES.md`: This file; a guide to the project's file structure.
- `pyproject.toml`: Defines project metadata, dependencies, and build configuration.
- `README.md`: General overview and setup instructions for the project.
- `uv.lock`: Lock file for deterministic dependency management.

## Source (`src/`)
- `main.py`: The main entry point for running the application.
- `agents/`:
    - `orchestrator.py`: Logic for the orchestration agent that handles tool selection and task execution.
    - `state.py`: Definitions for the agent's state management (using LangGraph).
- `connections/`:
    - `db.py`: Establises and manages connections to the database.
- `database/`:
    - `vector_store.py`: Implementation of the RAG system for tool discovery using vector embeddings.
- `models/`:
    - `tool.py`: Pydantic models defining the schema for tool definitions.
- `observability/`:
    - `langfuse_client.py`: Integration with Langfuse for tracing and performance monitoring.
- `tools/`:
    - `base.py`: Base classes and interfaces for creating new tools.
    - `manager.py`: Handles tool registration, discovery, and retrieval.
- `tools_rag/`: Core package directory containing initialization and typing markers.

## Tests (`test/`)
- `connection_test.py`: Scripts to verify database connectivity.
- `test_env.py`: Verifies that environment variables are correctly loaded.
- `test.py`: General tests for system logic and tool RAG functionality.
