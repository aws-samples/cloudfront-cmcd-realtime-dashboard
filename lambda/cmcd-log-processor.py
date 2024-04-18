import json
import boto3
from botocore.config import Config
import os
import urllib.parse

session = boto3.Session()

# Recommended Timestream write client SDK configuration:
#  - Set SDK retry count to 10.
#  - Use SDK DEFAULT_BACKOFF_STRATEGY
#  - Set RequestTimeout to 20 seconds .
#  - Set max connections to 5000 or higher.
timestream_write = session.client('timestream-write', config=Config(read_timeout=20, max_pool_connections=5000,
                                                                    retries={'max_attempts': 10}))
client = boto3.client('timestream-write')

# Timestream DB and Table names
DATABASE_NAME = os.environ['timestream_database']
TABLE_NAME = os.environ['timestream_table']

log_fields_list = [
    # fields should match the configuration of real time logs
    {
        "Name": "timestamp",
        "Type": "Time",
        "Role": "Timestamp"
    },
    {
        "Name": "c-ip",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "time-to-first-byte",
        "Type": "DOUBLE",
        "Role": "Measure"
    },
    {
        "Name": "sc-status",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "sc-bytes",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cs-method",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-protocol",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-host",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-uri-stem",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-bytes",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "x-edge-location",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "x-edge-request-id",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "x-host-header",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "time-taken",
        "Type": "DOUBLE",
        "Role": "Measure"
    },
    {
        "Name": "cs-protocol-version",
        "Type": "VARCHAR",
        "Role": "Dimension"

    },
    {
        "Name": "c-ip-version",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {

        "Name": "cs-user-agent",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-referer",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    #{
    #    "Name": "cs-cookie",
    #    "Type": "VARCHAR",
    #    "Role": "Dimension"
    #},
    {
        "Name": "cs-uri-query",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "x-edge-response-result-type",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "x-forwarded-for",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "ssl-protocol",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "ssl-cipher",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "x-edge-result-type",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    #{
    #    "Name": "fle-encrypted-fields",
    #    "Type": "VARCHAR",
    #    "Role": "Dimension"
    #},
    #{
    #    "Name": "fle-status",
    #    "Type": "VARCHAR",
    #    "Role": "Dimension"
    #},
    {
        "Name": "sc-content-type",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "sc-content-len",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "sc-range-start",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "sc-range-end",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "c-port",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "x-edge-detailed-result-type",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "c-country",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-accept-encoding",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-accept",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cache-behavior-path-pattern",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-headers",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-header-names",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cs-headers-count",
        "Type": "BIGINT",
        "Role": "Dimension"
    },
    {
        "Name": "origin-fbl",
        "Type": "DOUBLE",
        "Role": "Measure"
    },
    {
        "Name": "origin-lbl",
        "Type": "DOUBLE",
        "Role": "Measure"
    },
    {
        "Name": "asn",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-encoded-bitrate",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-buffer-length",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-buffer-starvation",
        "Type": "BOOLEAN",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-content-id",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-object-duration",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-deadline",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-measured-throughput",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-next-object-request",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-next-range-request",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-object-type",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-playback-rate",
        "Type": "BIGINT",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-requested-maximum-throughput",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-streaming-format",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-session-id",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-stream-type",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-startup",
        "Type": "BOOLEAN",
        "Role": "Dimension"
    },
    {
        "Name": "cmcd-top-bitrate",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        "Name": "cmcd-version",
        "Type": "VARCHAR",
        "Role": "Dimension"
    }
]

# Headers to be used as dimensions
supported_headers = ['CloudFront-Is-IOS-Viewer', 'CloudFront-Is-Tablet-Viewer', 'CloudFront-Is-Mobile-Viewer',
                     'CloudFront-Viewer-City', 'CloudFront-Is-SmartTV-Viewer', 'CloudFront-Is-Android-Viewer',
                     'CloudFront-Is-Desktop-Viewer']

# Utility function for parsing the header fields
def parse_headers(headers):
    headers_dimensions = []
    headers_list = list(filter(None, urllib.parse.unquote(headers).split('\n')))  # filter out empty strings
    for nr, item in enumerate(headers_list):
        try:
            header, value = item.split(":", 1)
        except ValueError:
            # If there's no ":" in the item, it typically means mismatch with real-time logs fields configuration
            continue
        if header in supported_headers:
            headers_dimensions.append({
                'Name': header.replace('-', '_'),
                'Value': str(value.strip())
            })
    return headers_dimensions


def write_batch_timestream(records, record_counter):
    try:
        result = timestream_write.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME, Records=records,
                                                CommonAttributes={})
        print('Processed [%d] records. WriteRecords Status: [%s]' % (
            record_counter, result['ResponseMetadata']['HTTPStatusCode']))
    except timestream_write.exceptions.RejectedRecordsException as err:
        print("RejectedRecords: ", err)
        for rr in err.response["RejectedRecords"]:
            print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        print("Other records were written successfully. ")
    except Exception as err:
        print("Exception: " + str(err))


import base64


def lambda_handler(event, context):
    records = []
    record_counter = 0

    for record in event['Records']:

        # Extracting the record data in bytes and base64 decoding it
        payload_in_bytes = base64.b64decode(record['kinesis']['data'])

        # Converting the bytes payload to string
        payload = "".join(map(chr, payload_in_bytes))

        # counter to iterate over the record fields
        counter = 0

        dimensions_list = []
        measures_list = []

        # generate list from the tab-delimited log entry
        payload_list = payload.strip().split('\t')

        for log_field in log_fields_list:
            try:
                if log_field['Name'] == 'cs-headers':
                    headers_dimensions = parse_headers(payload_list[counter].strip())
                    if headers_dimensions:
                        dimensions_list += headers_dimensions
                    counter += 1  # comment if 'cs-headers' needs to be ingested in the Database
                    continue

                if log_field['Role'] == 'Dimension':
                    dimensions_list.append(
                        {'Name': log_field['Name'].replace('-', '_'), 'Value': str(payload_list[counter]).strip()}
                    )
                elif log_field['Role'] == 'Measure':
                    if payload_list[counter].strip() == '-':
                        counter += 1
                        continue
                    else:
                        measures_list.append(
                            {'Name': log_field['Name'].replace('-', '_'), 'Type': log_field['Type'],
                             'Value': str(payload_list[counter]).strip()}
                        )
                elif log_field['Role'] == 'Timestamp':
                    # Convert to milliseconds
                    timestamp = str(int(float(payload_list[counter].strip()) * 1000))
                counter += 1
            except Exception as e:
                print(f"Exception occurred when parsing log record: {e}")
                continue

        record = {
            'Dimensions': dimensions_list,
            'MeasureValueType': 'MULTI',
            'MeasureName': 'MULTI',
            'MeasureValues': measures_list,
            'Time': timestamp,
            'TimeUnit': 'MILLISECONDS'
        }

        print("RECORD:", record)

        records.append(record)
        record_counter = record_counter + 1

        # Timestream quota: The maximum number of records in a WriteRecords API request (100)
        if (len(records) == 100):
            write_batch_timestream(records, record_counter)
            records = []

    if (len(records) != 0):
        write_batch_timestream(records, record_counter)