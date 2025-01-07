import os
import requests
import csv
import traceback
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# File to store checkpoint data
CHECKPOINT_FILE = "checkpoint.txt"


def fetch_with_retry(url, headers, retries=5):
    """
    Fetches data from the provided URL with retries in case of rate-limiting or transient errors.
    """
    wait_time = 1  # Start with 1 second wait
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Rate limit
                retry_after = int(response.headers.get(
                    "Retry-After", wait_time))
                print(f"Rate limited. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
                wait_time *= 2
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(wait_time)
            wait_time *= 2
    print(f"Exceeded maximum retries for URL: {url}")
    return None


def get_relationships(lei, headers):
    """
    Fetches the parent relationship information for a given LEI using the GLEIF API.
    """
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}/direct-parent-relationship"
    try:
        response = fetch_with_retry(url, headers)
        if response:
            data = response.json()
            if 'data' in data and data['data']:
                relationships = data['data']
                if 'relationships' in relationships:
                    end_node = relationships['relationships'].get(
                        'end-node', {})
                    parent_url = end_node['links']['related']
                    parent_id = parent_url.split('/')[-1]

                    parent_response = fetch_with_retry(parent_url, headers)
                    if parent_response:
                        parent_data = parent_response.json()
                        parent_name = parent_data['data']['attributes']['entity']['legalName']['name']
                        return parent_id, parent_name
            return 'N/A', 'N/A'
        else:
            return 'N/A', 'N/A'
    except Exception as e:
        print(f"Error fetching relationships for LEI {lei}: {e}")
        return 'N/A', 'N/A'


def save_checkpoint(next_url, file_counter):
    """
    Saves the next URL and file counter to a checkpoint file.
    """
    with open(CHECKPOINT_FILE, 'w') as f:
        f.write(f"{next_url}\n{file_counter}")


def load_checkpoint():
    """
    Loads the last URL and file counter from the checkpoint file.
    Returns None and 1 if the file doesn't exist.
    """
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) == 2:
                return lines[0].strip(), int(lines[1].strip())
    return None, 1


def save_to_csv(data, file_number, next_url):
    """
    Saves the collected data to a CSV file and updates the checkpoint.
    """
    file_name = f'lei-data-part-{file_number}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ['LEI', 'Legal Name', 'Parent LEI', 'Parent Legal Name'])
        writer.writerows(data)
        print(f'File saved: {file_name}')

    # Save checkpoint after saving the CSV
    save_checkpoint(next_url, file_number + 1)


def process_record(record, headers):
    """
    Processes a single record to fetch LEI, name, parent LEI, and parent name.
    """
    try:
        lei = record['attributes']['lei']
        name = record['attributes']['entity']['legalName']['name']
        parent_lei, parent_name = get_relationships(lei, headers)
        print(f"Processing LEI: {lei}")
        return [lei, name, parent_lei, parent_name]
    except KeyError as e:
        print(f"Error processing record: {e}")
        return None


def get_all_leis():
    """
    Fetches all LEI records with their parent relationships and saves them in CSV files.
    """
    headers = {'Accept': 'application/vnd.api+json'}
    batch_size = 100
    lei_data = []

    # Load progress from checkpoint
    next_url, file_counter = load_checkpoint()
    if not next_url:
        next_url = "https://api.gleif.org/api/v1/lei-records?page[cursor]=*"

    try:
        # Start cursor-based pagination
        with ThreadPoolExecutor(max_workers=10) as executor:
            while next_url:
                print(f"Fetching data from: {next_url}")
                response = fetch_with_retry(next_url, headers)

                if response:
                    data = response.json()

                    # Process records in parallel
                    futures = [
                        executor.submit(process_record, record, headers)
                        for record in data['data']
                    ]

                    for future in as_completed(futures):
                        result = future.result()
                        if result:
                            lei_data.append(result)

                    # Save data in batches
                    if len(lei_data) >= batch_size:
                        save_to_csv(lei_data, file_counter, next_url)
                        file_counter += 1
                        lei_data = []

                    # Follow the next page link
                    next_url = data.get('links', {}).get('next')

                else:
                    print("Stopping data retrieval due to repeated errors.")
                    break

        # Save remaining rows
        if lei_data:
            save_to_csv(lei_data, file_counter, next_url)

    except Exception as ex:
        print(f"An exception occurred:\n{ex}\n\n{traceback.format_exc()}")


# Download LEI data using cursor-based pagination
get_all_leis()
