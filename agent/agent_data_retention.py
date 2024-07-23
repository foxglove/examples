import os
import requests
import logging
import json
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

def configure_logging(log_level: str) -> None:
    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    logging.basicConfig(level=log_levels.get(log_level, logging.WARNING), format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(env_file_path: str) -> Dict[str, str]:
    logging.info(f"Loading configuration from {env_file_path}")
    with open(env_file_path, 'r') as file:
        config = {
            key: value
            for line in file
            if '=' in line and not line.startswith('#')
            for key, value in [line.strip().split('=', 1)]
        }
    
    if 'STORAGE_ROOT' not in config:
        raise ValueError("Required configuration not found in environment file.")
    logging.info("Configuration loaded successfully")
    return config

def fetch_recordings(api_url: str, api_token: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
    headers = {"Authorization": f"Bearer {api_token}"}
    params = {"start": start_time, "end": end_time, "sortBy": "createdAt", "order": "desc", "limit": 2000}
    recordings, page_count = [], 0

    while True:
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            new_recordings = response.json()
            recordings.extend(new_recordings)
            logging.info(f"Fetched {len(new_recordings)} recordings on page {page_count}")

            if len(new_recordings) < 2000:
                break
            params['start'] = new_recordings[-1]['createdAt']
            page_count += 1
        except requests.RequestException as e:
            logging.error(f"Failed to fetch recordings: {e}")
            break

    logging.info(f"Successfully fetched a total of {len(recordings)} recordings")
    return recordings

def get_mcap_files(storage_root: str, lookback_period: timedelta) -> List[str]:
    lookback_threshold = datetime.now(timezone.utc) - lookback_period

    return [
        os.path.join(root, file)
        for root, _, files in os.walk(storage_root)
        for file in files if file.endswith('.mcap') and datetime.utcfromtimestamp(os.path.getmtime(os.path.join(root, file))).replace(tzinfo=timezone.utc) >= lookback_threshold
    ]

def delete_file(file_path: str) -> None:
    try:
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to delete file {file_path}: {e}")

def data_retention(storage_root: str, api_url: str, api_token: str, retention_period: timedelta, lookback_period: timedelta, show_pending_files: bool) -> None:
    logging.info(f"Starting data retention process in {storage_root}")

    end_time = datetime.now(timezone.utc)
    start_time = end_time - lookback_period
    start_time_str, end_time_str = start_time.isoformat(), end_time.isoformat()

    recordings = fetch_recordings(api_url, api_token, start_time_str, end_time_str)
    completed_recordings = {os.path.basename(rec['path']) for rec in recordings if rec['importStatus'] == 'complete'}
    pending_recordings = {os.path.basename(rec['path']) for rec in recordings if rec['importStatus'] == 'pending'}

    mcap_files = get_mcap_files(storage_root, lookback_period)

    stats = {
        'total_files_checked': len(mcap_files),
        'total_files_deleted': 0,
        'total_files_not_deleted': 0,
        'not_deleted': {'not_on_foxglove': 0, 'too_recent_for_deletion': 0, 'pending_import': 0},
        'pending_recordings_not_on_local': 0,
        'pending_files_on_local': []
    }

    for mcap_file in mcap_files:
        file_basename = os.path.basename(mcap_file)
        file_creation_time = datetime.utcfromtimestamp(os.path.getmtime(mcap_file)).replace(tzinfo=timezone.utc)

        if file_basename in completed_recordings and file_creation_time < end_time - retention_period:
            delete_file(mcap_file)
            stats['total_files_deleted'] += 1
        else:
            stats['total_files_not_deleted'] += 1
            if file_basename in pending_recordings:
                stats['not_deleted']['pending_import'] += 1
                stats['pending_files_on_local'].append(mcap_file)
            elif file_basename not in completed_recordings:
                stats['not_deleted']['not_on_foxglove'] += 1
            else:
                stats['not_deleted']['too_recent_for_deletion'] += 1

    stats['pending_recordings_not_on_local'] = len(pending_recordings - {os.path.basename(file) for file in mcap_files})

    logging.info("Data retention process completed")
    logging.info(f"Total files checked: {stats['total_files_checked']}")
    logging.info(f"Total files deleted: {stats['total_files_deleted']}")
    logging.info(f"Total files not deleted: {stats['total_files_not_deleted']}")
    logging.info(f"Reasons for not deleted files: {json.dumps(stats['not_deleted'], indent=4)}")
    logging.info(f"Pending recordings not on local file system: {stats['pending_recordings_not_on_local']}")

    if show_pending_files and stats['pending_files_on_local']:
        logging.info("Pending files on local file system:")
        for file in stats['pending_files_on_local']:
            logging.info(f"- {file}")

    # Print summary regardless of log level
    print("Summary:")
    print(f"Total files checked: {stats['total_files_checked']}")
    print(f"Total files deleted: {stats['total_files_deleted']}")
    print(f"Total files not deleted: {stats['total_files_not_deleted']}")
    print(f"Reasons for not deleted files: {json.dumps(stats['not_deleted'], indent=4)}")
    print(f"Pending recordings not on local file system: {stats['pending_recordings_not_on_local']}")
    if show_pending_files and stats['pending_files_on_local']:
        print("Pending files on local file system:")
        for file in stats['pending_files_on_local']:
            print(f"- {file}")

def parse_duration(duration_str: str) -> timedelta:
    units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'M': 'days'}
    amount, unit = int(duration_str[:-1]), duration_str[-1]

    if unit == 'M':
        amount *= 30  # Approximation of a month

    if unit in units:
        return timedelta(**{units[unit]: amount})
    raise ValueError("Invalid duration format. Use s, m, h, d, or M for seconds, minutes, hours, days, or months respectively.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Data retention script for Foxglove")
    parser.add_argument('--env', type=str, default='/etc/foxglove/agent/envfile', help="Path to the environment file (default: /etc/foxglove/agent/envfile)")
    parser.add_argument('--retention', type=str, default='1h', help="Retention period (e.g., '1h' for 1 hour, '30d' for 30 days)")
    parser.add_argument('--lookback', type=str, default='48h', help="Lookback period (e.g., '48h' for 48 hours)")
    parser.add_argument('--api_url', type=str, default='https://api.foxglove.dev/v1/recordings', help="API URL for fetching recordings (default: 'https://api.foxglove.dev/v1/recordings')")
    parser.add_argument('--storage_root', type=str, help="Root directory for storage (overrides value from env file)")
    parser.add_argument('--api_token', type=str, help="API token for authorization (overrides value from environment variable)")
    parser.add_argument('--show_pending_files', action='store_true', help="Show fully qualified filenames of pending imports that are on the filesystem")
    parser.add_argument('--log_level', type=str, default='warning', help="Set the logging level (default: 'warning')")

    args = parser.parse_args()

    configure_logging(args.log_level)

    logging.info("Loading environment variables")
    config = load_config(args.env)
    storage_root = args.storage_root or config['STORAGE_ROOT']
    api_token = args.api_token or os.getenv('FOXGLOVE_API_TOKEN')

    if not api_token:
        raise ValueError("API token must be provided either as an argument or in the FOXGLOVE_API_TOKEN environment variable.")

    retention_period = parse_duration(args.retention)
    lookback_period = parse_duration(args.lookback)

    logging.info(f"Starting data retention script with a retention period of {args.retention} and a lookback period of {args.lookback}")
    logging.info(f"Arguments: {args}")

    data_retention(storage_root, args.api_url, api_token, retention_period, lookback_period, args.show_pending_files)
    logging.info("Data retention script finished")

if __name__ == "__main__":
    main()

