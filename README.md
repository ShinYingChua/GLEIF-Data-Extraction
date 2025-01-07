# LEI Data Fetcher
A Python-based application to fetch Legal Entity Identifier (LEI) records from the GLEIF API using cursor-based pagination. This project supports retry mechanisms, multi-threaded processing, and checkpointing to ensure efficient and reliable data retrieval.

## Features

- **Cursor-based Pagination**: Retrieves LEI data in batches.
- **Retry Logic**: Handles API rate-limiting and transient errors with exponential backoff.
- **Parallel Processing**: Uses `ThreadPoolExecutor` for faster data processing.
- **Checkpointing**: Saves progress to resume from the last processed record in case of interruptions.
- **Data Output**: Saves LEI data and parent relationships to CSV files.

## Cursor-based pagnination VS Deep Pagination 
- The GLEIF API does not support deep page-based pagination beyond 10,000 results (page[number] * page[size] > 10,000) (Error 400)
- use page[cursor]=* to start cursor-based pagination and then follow the `$.links.next` URL returned in the response to traverse the entire result set.

## Limitations
- GLEIF rate limiting is currently set at 60 requests, per minute, per user, for all users (error 409).

## Output
- csv files with LEI, Legal Name, Parent LEI, Parent Legal Name

## Running the code
- Execute `python get_glief_data.py`
