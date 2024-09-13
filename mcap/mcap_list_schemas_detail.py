import json
import sys
from mcap.reader import make_reader


def list_schemas_with_messages_and_metadata(mcap_file: str) -> None:
    """Extract and display unique schemas with message count and metadata from an MCAP file."""
    with open(mcap_file, "rb") as stream:
        reader = make_reader(stream)
        summary = reader.get_summary()

        if not summary:
            print("No summary section available in the MCAP file.")
            return

        # Prepare to store message counts for each schema
        message_counts = {schema_id: 0 for schema_id in summary.schemas}

        # Iterate over all messages to count how many are associated with each schema
        for _, channel, _ in reader.iter_messages():
            schema_id = channel.schema_id
            if schema_id in message_counts:
                message_counts[schema_id] += 1

        # Display the schema information along with message count and metadata
        print('\n')
        print(f"{'Schema ID':<12}{'Name':<60}{'Encoding':<12}{'Message Count':<15}{'Metadata':<60}")
        print('-' * 160)
        for schema_id in sorted(summary.schemas):
            schema = summary.schemas[schema_id]
            channel = summary.channels.get(schema_id, {})
            metadata = channel.metadata if channel else {}
            metadata_str = json.dumps(metadata)
            if len(metadata_str) > 60:
                metadata_str = metadata_str[:57] + " ..."
            print(f"{schema_id:<12}{schema.name:<60}{schema.encoding:<12}{message_counts[schema_id]:<15}{metadata_str}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python list_schemas_with_messages_and_metadata.py <mcap_file>")
    else:
        list_schemas_with_messages_and_metadata(sys.argv[1])
