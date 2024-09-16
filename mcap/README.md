# MCAP Examples

## List schemas in MCAP
This example demonstrates how to list all unique schemas from an MCAP file, along with their associated message counts and metadata. The script extracts the schemas directly from the summary section of the MCAP file to ensure that all schemas are listed, including those without any associated messages.

### Features:
**List all unique schemas:** The script retrieves and lists schemas from the MCAP file.

**Message count:** It counts and displays the number of messages associated with each schema.

**Metadata display:** The metadata associated with each schema (if available) is also shown.

### Prerequisites:
- Python 3.x
- mcap library installed. You can install it using:

```bash
pip install mcap
```

### How to Use:
Clone the repository and navigate to the mcap directory:

```bash
git clone https://github.com/foxglove/examples.git
cd examples/mcap
```

Run the script with your MCAP file as an argument:

```bash
python mcap_list_schemas_detail.py <path_to_mcap_file>
```

### Example Output:

```bash
Schema ID   Name                                                        Encoding    Message Count  Metadata                                                    
----------------------------------------------------------------------------------------------------------------------------------------------------------------
1           rcl_interfaces/msg/Log                                      ros2msg     39             {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
2           sensor_msgs/msg/Joy                                         ros2msg     0              {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
3           rosbag2_interfaces/msg/WriteSplitEvent                      ros2msg     0              {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
4           rcl_interfaces/msg/ParameterEvent                           ros2msg     0              {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
5           diagnostic_msgs/msg/DiagnosticArray                         ros2msg     74             {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
6           diagnostic_msgs/msg/DiagnosticStatus                        ros2msg     25             {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
7           sensor_msgs/msg/LaserScan                                   ros2msg     192            {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
8           std_msgs/msg/String                                         ros2msg     6              {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
9           tf2_msgs/msg/TFMessage                                      ros2msg     462            {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
10          geometry_msgs/msg/Twist                                     ros2msg     0              {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
11          sensor_msgs/msg/JointState                                  ros2msg     233            {"offered_qos_profiles": "- history: 3\n  depth: 0\n  rel ...
```

### Code Breakdown:
**Schema Extraction:** The script uses the summary section of the MCAP file to retrieve all schemas, ensuring none are missed.

**Message Counting:** It iterates over the messages in the MCAP file and counts how many messages are associated with each schema.

**Metadata Handling:** Any available metadata for the schemas is displayed as key-value pairs.

### Customization:
Feel free to modify the script to suit your specific use case, such as adjusting the output format or adding additional schema details.
