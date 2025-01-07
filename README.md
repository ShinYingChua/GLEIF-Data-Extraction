# LEI Data Fetcher
A Python-based application to fetch Legal Entity Identifier (LEI) records from the GLEIF API using cursor-based pagination. This project supports retry mechanisms, multi-threaded processing, and checkpointing to ensure efficient and reliable data retrieval.

## Features

- **Cursor-based Pagination**: Retrieves LEI data in batches.
- **Retry Logic**: Handles API rate-limiting and transient errors with exponential backoff.
- **Parallel Processing**: Uses `ThreadPoolExecutor` for faster data processing.
- **Checkpointing**: Saves progress to resume from the last processed record in case of interruptions.
- **Data Output**: Saves LEI data and parent relationships to CSV files.

## Limitations
- GLEIF rate limiting is currently set at 60 requests, per minute, per user, for all users (error 409).

## Prerequisites

### Requirements
- Python 3.7 or later
- Pip dependencies listed in [requirements.txt](#requirements).

### Install Dependencies
```bash
pip install -r requirements.txt
