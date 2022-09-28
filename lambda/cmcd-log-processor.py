import base64
import json
import boto3
from botocore.config import Config
import os
import datetime
import urllib.parse

import sys

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
    {
        "Name": "cs-cookie",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
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
    {
        "Name": "fle-encrypted-fields",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        "Name": "fle-status",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
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
    }
]

cmcd_fields_list = [
    # CMCD paramerers supported by the player
    {
        # Encoded Bitrate, kbps
        "Name": "br",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        # Content ID
        "Name": "cid",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        # Buffer Length, ms
        "Name": "bl",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        # Object duration, ms
        "Name": "d",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        # Deadline, kbps.
        "Name": "dl",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        # Measured throughput, kbps
        "Name": "mtp",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        # Object type
        "Name": "ot",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        # Playback rate
        "Name": "pr",
        "Type": "BIGINT",
        "Role": "Dimension"
    },
    {
        # Requested  maximum throughput, kbps
        "Name": "rtp",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        # Streaming format
        "Name": "sf",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        # Session ID
        "Name": "sid",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        # Stream type
        "Name": "st",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        # Startup
        "Name": "su",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        # Buffer Starvation
        "Name": "bs",
        "Type": "BOOLEAN",
        "Role": "Measure"
    },
    {
        # Top bitrate, kbps
        "Name": "tb",
        "Type": "BIGINT",
        "Role": "Measure"
    },
    {
        # Next Object Request
        "Name": "nor",
        "Type": "VARCHAR",
        "Role": "Dimension"
    },
    {
        # Next Range Request
        "Name": "nrr",
        "Type": "VARCHAR",
        "Role": "Dimension"
    }
]

# Headers to be used as dimensions
supported_headers = ['CloudFront-Is-IOS-Viewer', 'CloudFront-Is-Tablet-Viewer', 'CloudFront-Is-Mobile-Viewer',
                     'CloudFront-Viewer-City', 'CloudFront-Is-SmartTV-Viewer', 'CloudFront-Is-Android-Viewer',
                     'CloudFront-Is-Desktop-Viewer']

# Utility function for parsing the query string
def parse_query_string(query_string):
    cmcd_dimensions = []
    cmcd_measures = []

    query_string_dict = urllib.parse.parse_qs(query_string)
    if 'CMCD' in query_string_dict:
        cmcd_string_decoded = urllib.parse.unquote(urllib.parse.unquote(''.join(query_string_dict['CMCD'])))
        cmcd_parameters_list = (cmcd_string_decoded.split(","))
        # removing emtpy elements
        cmcd_parameters_list = list(filter(None, cmcd_parameters_list))
        for nr, item in enumerate(cmcd_parameters_list):
            # bs and su flags don't carry any value
            if item == 'su' or item == 'bs':
                cmcd_parameters_list[nr] = item + "=" + "true"

        cmcd_parameters_dict = dict(s.split('=') for s in cmcd_parameters_list)

        for cmcd_field in cmcd_fields_list:
            if cmcd_field['Name'] in cmcd_parameters_dict.keys():
                if cmcd_field['Role'] == 'Dimension':
                    cmcd_dimensions.append(
                        {'Name': 'cmcd' + '_' + cmcd_field['Name'],
                         'Value': str(cmcd_parameters_dict[cmcd_field['Name']]).strip()}
                    )
                elif cmcd_field['Role'] == 'Measure':
                    cmcd_measures.append(
                        {'Name': 'cmcd' + '_' + cmcd_field['Name'], 'Type': cmcd_field['Type'],
                         'Value': str(cmcd_parameters_dict[cmcd_field['Name']]).strip()}
                    )
    return cmcd_dimensions, cmcd_measures


# Utility function for parsing the header fields
def parse_headers(headers):
    headers_dimensions = []
    headers_list = list(filter(None, urllib.parse.unquote(headers).split('\n')))  # filter out empty strings
    for nr, item in enumerate(headers_list):
        header, value = item.split(":", 1)
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
        print("payload_list:", payload_list)

        for log_field in log_fields_list:
            if log_field['Name'] == 'cs-headers':
                headers_dimensions = parse_headers(payload_list[counter].strip())
                if headers_dimensions:
                    dimensions_list = dimensions_list + headers_dimensions
                counter += 1 #comment if 'cs-headers' needs to be ingested in the Database
                continue
            elif log_field['Name'] == 'cs-uri-query':
                cs_uri_query = payload_list[counter].strip()
                query_dimensions, query_measures = parse_query_string(payload_list[counter].strip())
                dimensions_list += query_dimensions
                measures_list += query_measures
                counter += 1 #comment if 'cs-uri-query' needs to be ingested in the Database
                continue
            if log_field['Role'] == 'Dimension':
                dimensions_list.append(
                    {'Name': log_field['Name'].replace('-', '_'), 'Value': str(payload_list[counter]).strip()}
                )
            elif log_field['Role'] == 'Measure':
                # If the measure value is '-' (e.g. sc-content-len is '-' for compressed files), we omit it and Timestream record it as Null
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

        record = {
            'Dimensions': dimensions_list,
            'MeasureValueType': 'MULTI',
            'MeasureName': 'MULTI',
            'MeasureValues': measures_list,
            'Time': timestamp,
            'TimeUnit': 'MILLISECONDS'
        }

        print ("RECORD:", record)
        t = json.dumps(record)
        print("SIZE OF RECORD:", len(t.encode('utf-8')))

        records.append(record)
        record_counter = record_counter + 1

        # Timestream quota: The maximum number of records in a WriteRecords API request (100)
        if (len(records) == 100):
            write_batch_timestream(records, record_counter)
            records = []

    if (len(records) != 0):
        write_batch_timestream(records, record_counter)