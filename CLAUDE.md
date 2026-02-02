# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI-based proxy service for a financial platform API (credit check/background verification system). Provides RESTful endpoints to interact with an internal financial platform at `192.168.3.53:48080`.

## Commands

```bash
# Install dependencies
pip install fastapi uvicorn pydantic aiohttp requests loguru pycryptodome pyrootutils

# Start the server
python rongxing_server.py [port]

# Or use the start script (kills old process, runs in background)
./start.sh [port]

# Connect to VPN for internal network access (if needed)
./start_vpn.sh

# Query task result directly (access_token + task_id)
python tools/check_task_result.py <access_token> <task_id>
```

Server runs on port 32461 by default (`http://0.0.0.0:32461`).

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/init` | POST | Initialize session (password: `123456`) → returns `session_id` |
| `/login/{session_id}` | POST | Execute login, prints `[Session: xxx] Access Token: xxx` |
| `/logout/{session_id}` | POST | Execute logout |
| `/create_credit_task/{session_id}` | POST | Batch create credit check tasks |
| `/query_credit_task/{session_id}` | GET | Query task results (supports retries) |

## Architecture

- **`FinancialPlatformAPI`** class in [main.py](main.py): Core client handling all external API communication
  - RSA signature generation with SHA-256 for authentication
  - AES-256 ECB decryption for response data (key derived from `user_id`)
  - Mix of sync (`requests`) for login/logout and async (`aiohttp`) for task operations
  - `session_id` property for log correlation
- **[api.py](api.py)**: FastAPI application with in-memory session storage (`_sessions: Dict[str, FinancialPlatformAPI]`)
- **[rongxing_server.py](rongxing_server.py)**: Server entry point using uvicorn
- **[config.py](config.py)**: Configuration for base_url, app_id, private_key, and credentials
- **[tools/check_task_result.py](tools/check_task_result.py)**: Direct query utility that bypasses the proxy service

### Authentication Flow

1. Initialize session via `/init` → receives UUID `session_id`
2. Call `/login/{session_id}` → uses RSA-signed request with timestamp
3. Subsequent requests use `Bearer {access_token}` header

### Two Token Types

- **`session_id`**: Proxy service session ID (UUID), for API routing and log correlation
- **`access_token`**: Financial platform API token (JWT), for downstream API authentication

### Data Encryption

Response data is AES-256 ECB encrypted. Key = first 16 chars of SHA-256 hash of `user_id`. Decryption is automatic in `query_credit_task_result()`.

### Session Logging

Login logs include both `session_id` and `access_token` for debugging:
```
[Session: d7489fcf-88bc-40df-8994-dbac19d0fd4a] Access Token: eyJhbGci...
```
