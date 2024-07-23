# Foxglove Data Retention Script

This script manages data retention for Foxglove recordings by deleting old `.mcap` files based on specified retention and lookback periods. It fetches recording metadata from the Foxglove API to determine which files are safe to delete and logs the process.

**Note:** Only Linux is tested and supported for the agent that this script works with.

## Features

- Configurable logging levels
- Load environment variables from a file
- Fetch recordings metadata from Foxglove API
- Identify and delete old `.mcap` files based on retention criteria
- Detailed logging and summary of the retention process

## Usage

```bash
python data_retention.py [OPTIONS]
```

### Options

- `--env <path>`: Path to the environment file (default: `/etc/foxglove/agent/envfile`)
- `--retention <duration>`: Retention period (e.g., `1h` for 1 hour, `30d` for 30 days) (default: `1h`)
- `--lookback <duration>`: Lookback period (e.g., `48h` for 48 hours) (default: `48h`)
- `--api_url <url>`: API URL for fetching recordings (default: `https://api.foxglove.dev/v1/recordings`)
- `--storage_root <path>`: Root directory for storage (overrides value from env file)
- `--api_token <token>`: API token for authorization (overrides value from environment variable)
- `--show_pending_files`: Show fully qualified filenames of pending imports that are on the filesystem
- `--log_level <level>`: Set the logging level (default: `warning`)

### Setting the API Key Environment Variable

Set the `FOXGLOVE_API_TOKEN` environment variable to provide the API key:

```bash
export FOXGLOVE_API_TOKEN=your_api_token
```

### Example

```bash
python data_retention.py --env /path/to/envfile --retention 7d --lookback 30d --api_url https://api.foxglove.dev/v1/recordings --storage_root /data/storage --log_level info
```

This example runs the script with the following parameters:

- Environment file: `/path/to/envfile`
- Retention period: 7 days
- Lookback period: 30 days
- API URL: `https://api.foxglove.dev/v1/recordings`
- Storage root: `/data/storage`
- Logging level: `info`

Ensure that the `FOXGLOVE_API_TOKEN` environment variable is set or provide the API token using the `--api_token` option.
