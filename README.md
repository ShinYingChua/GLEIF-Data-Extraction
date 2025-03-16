# LEI Data Fetcher 
A Python-based application to fetch Legal Entity Identifier (LEI) records from the GLEIF API using cursor-based pagination. This project supports retry mechanisms, multi-threaded processing, and checkpointing to ensure efficient and reliable data retrieval.
The script is useful for financial institutions, regulatory bodies, or data analysts who need to extract and analyze corporate hierarchy information using GLEIF’s LEI data.

Currently, GLEIF offers manual LEI lookup, allowing users to search for one entity at a time. This process is:
- Time-consuming – Searching for thousands of entities manually is inefficient.
- Not scalable – No built-in bulk download.
- Prone to errors – Manual lookups increase the risk of missing data or inconsistencies.
<img width="1318" alt="image" src="https://github.com/user-attachments/assets/739793c8-bbc8-4b46-9e9e-86562b74060b" />

https://search.gleif.org/#/search/simpleSearch=549300MDYVVHJ8D1DW28&fulltextFilterId=LEIREC_OWNS&currentPage=1&perPage=15&expertMode=false#search-form

This LEI Data Fetcher eliminates these limitations by:
- Automating the retrieval of all available LEI records.
- Extracting parent-child relationships, making it easier to analyze corporate structures.
- Saving results into structured CSV files for further analysis or integration into business systems.
- 
## Features
- **Cursor-based Pagination**: Retrieves LEI data in batches.
- **Handles API rate-limiting**:
  - GLEIF rate limiting is currently set at 60 requests, per minute, per user, for all users.
  - The rate limiting may cause HTTP 429 error: Too Many Requests client error response status code
- **Retry Logic**: Handles transient errors with exponential backoff.
  - Initial wait time is 1 second. Doubles the wait time (wait_time *= 2) for subsequent retries to reduce rapid API requests.
- **Parallel Processing**: Uses `ThreadPoolExecutor` for faster data processing.
- **Checkpointing**: Saves progress to resume from the last processed record in case of interruptions.
  - Purpose: Ensure that in case of failures or interruptions, data retrieval resumes from where it left off.
  - CHECKPOINT_FILE (checkpoint.txt): Stores the last processed API URL and the CSV file number.
- **Data Output**: Saves LEI data and parent relationships to CSV files.

## Cursor-based pagnination VS Deep Pagination 
- The GLEIF API does not support deep page-based pagination beyond 10,000 results (page[number] * page[size] > 10,000) (Error 400)
- use page[cursor]=* to start cursor-based pagination and then follow the `$.links.next` URL returned in the response to traverse the entire result set.

## Running the code
- Execute `python get_glief_data.py`

## Output

The script generates structured **CSV files** containing the following columns:

| Column Name            | Description                                           |
|------------------------|-------------------------------------------------------|
| **LEI**                | Legal Entity Identifier                              |
| **Legal Name**         | Official registered name of the entity               |
| **Parent LEI**         | LEI of the parent entity (if available)              |
| **Parent Name**        | Legal name of the parent entity                      |
| **Legal Address**      | Registered legal address of the entity               |
| **Legal City**         | City of the legal address                            |
| **Legal Postal Code**  | Postal code of the legal address                     |
| **HQ Address**         | Headquarters address of the entity                   |
| **HQ City**            | City of the headquarters                             |
| **HQ Postal Code**     | Postal code of the headquarters                      |
| **Registered As**      | Registration identifier of the entity (if available) |
| **Category**           | Category or classification of the entity             |
| **Legal Jurisdiction** | Jurisdiction under which the entity is registered    |
| **Entity Status**      | Active or inactive status of the entity              |
| **Registration Date**  | Date when the entity was registered                  |

