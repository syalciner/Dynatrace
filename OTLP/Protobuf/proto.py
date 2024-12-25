import json
from opentelemetry.proto.common.v1.common_pb2 import KeyValue, AnyValue
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans, ScopeSpans, Span, TracesData

def assign_value_to_key_value(key_value, value):
    try:
        # Create an AnyValue object to store the value
        any_value = AnyValue()

        # Check the type of the value and assign it accordingly
        if isinstance(value, str):
            # If the value is a string, assign it directly
            any_value.string_value = value
        elif isinstance(value, bool):
            any_value.bool_value = value
        elif isinstance(value, int):
            any_value.int_value = value
        elif isinstance(value, float):
            any_value.double_value = value
        else:
            # For other types, convert to string and then assign
            any_value.string_value = str(value)

        # Now assign the AnyValue to the KeyValue
        key_value.value.CopyFrom(any_value)

    except Exception as e:
        print(f"Error assigning value to KeyValue: {e}")

def convert_json_to_protobuf(json_data, output_file):
    try:
        # Initialize the TracesData object that will hold the converted data
        traces_data = TracesData()

        # Process resource spans
        for resource_span in json_data.get('resourceSpans', []):
            resource_spans = ResourceSpans()

            # Add resource attributes to resource_spans
            resource_spans.resource.attributes.extend([
                KeyValue(key=attr['key'], value=AnyValue(string_value=attr['value'].get('stringValue', '')))
                for attr in resource_span.get('resource', {}).get('attributes', [])
            ])

            # Process scope spans
            for scope_span in resource_span.get('scopeSpans', []):
                scope_spans = ScopeSpans()  # Do not set the 'name' field
                for span in scope_span.get('spans', []):
                    trace_span = Span(
                        #trace_id=span['traceId'].encode('utf-8'),
                        #span_id=span['spanId'].encode('utf-8'),
                        #trace_id = span['traceId'],  # Should be a 32-character hex string (16 bytes)
                        #span_id = span['spanId'],
                        trace_id = bytes.fromhex(span["traceId"]),
                        span_id = bytes.fromhex(span["spanId"]),
                        name=span['name'],
                        start_time_unix_nano=int(span['startTimeUnixNano']),  # Convert string to int
                        end_time_unix_nano=int(span['endTimeUnixNano']),        # Convert string to int
                        kind=span.get('kind', 0)
                    )

                    # Add span attributes
                    for attr in span.get('attributes', []):
                        key_value = KeyValue(key=attr['key'])
                        assign_value_to_key_value(key_value, attr['value'].get('stringValue', ''))
                        trace_span.attributes.append(key_value)

                    scope_spans.spans.append(trace_span)

                resource_spans.scope_spans.append(scope_spans)

            traces_data.resource_spans.append(resource_spans)

        # Write the Protobuf data to a binary file
        with open(output_file, 'wb') as f:
            f.write(traces_data.SerializeToString())
        print(f"Protobuf data written to {output_file}")
    except Exception as e:
        print(f"Error converting JSON to Protobuf: {e}")

def main():
    input_json_file = 'Payload.json'  # Assuming the JSON file is named 'Payload.json' in the same directory
    output_pb_file = 'output.pb'

    try:
        with open(input_json_file, 'r') as json_file:
            json_trace_data = json.load(json_file)
            print(f"Loaded JSON data: {json_trace_data}")
            convert_json_to_protobuf(json_trace_data, output_pb_file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")

if __name__ == "__main__":
    main()
