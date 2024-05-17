import pandas as pd
import json
import subprocess
import argparse
import uuid
import os
import tempfile


def run_external_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')

        # Print the output and error directly
        if output:
            print("Output:", output)
        if error:
            print("Error:", error)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with return code {e.returncode}")
        if e.output:
            print(e.output.decode('utf-8'))


def excel_to_json_and_call_datahub(excel_file_path):
    df = pd.read_excel(excel_file_path)
    df = df.astype(object)
    df.fillna("", inplace=True)

    for _, row in df.iterrows():
        json_obj = {
            "definition": str(row["Short Description"]),
            "name": str(row["Field Name"]),
            "termSource": "INTERNAL",
            "customProperties": {
                "Long Description": str(row["Long Description"]),
                "Type": str(row["Type"]),
                "Length": str(row["Length"]),
                "Mask": str(row["Mask"]),
                "Notes": str(row["Notes"]),
                "Alternate Name": str(row["Alternate Name"]),
                "FLA Friendly": str(row["FLA Friendly"]),
                "DataType": str(row["DataType"]),
                "Level": str(row["Level"]),
                "Royalty": str(row["Royalty"]),
                "FieldCategory1": str(row["FieldCategory1"]),
                "FieldCategory2": str(row["FieldCategory2"]),
                "FieldCategory3": str(row["FieldCategory3"]),
                "Sp. Use Code 1": str(row["Sp. Use Code 1"]),
                "Sp. Use Code 2": str(row["Sp. Use Code 2"]),
                "OptOutReasonCode": str(row["OptOutReasonCode"])
            }
        }

        json_str = json.dumps(json_obj, indent=4)

        # Generate a random UUID
        random_uuid = uuid.uuid4()
        urn = f"urn:li:glossaryTerm:{random_uuid}"

        # Create a temporary file for the JSON data
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_json_file:
            temp_json_file.write(json_str)
            temp_json_file_path = temp_json_file.name

        try:
            # Prepare the command
            command = f'datahub put --urn "{urn}" -a glossaryTermInfo -d {temp_json_file_path}'

            # Run the external command
            run_external_command(command)
        finally:
            # Delete the temporary file
            os.remove(temp_json_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Excel file and call datahub put for each row.')
    parser.add_argument('excel_file_path', type=str, help='The path to the Excel file')

    args = parser.parse_args()
    excel_to_json_and_call_datahub(args.excel_file_path)
