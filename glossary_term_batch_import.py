import pandas as pd
import json
import subprocess
import argparse


def run_external_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')
        print("Output:", output)
        print("Error:", error)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with return code {e.returncode}")


def excel_to_json_and_call_datahub(excel_file_path):
    df = pd.read_excel(excel_file_path)
    df = df.astype(object)
    df.fillna("", inplace=True)

    for _, row in df.iterrows():
        json_obj = {
            "definition": row["Short Description"],
            "name": row["Field Name"],
            "termSource": "INTERNAL",
            "customProperties": {
                "Long Description": row["Long Description"],
                "Type": row["Type"],
                "Length": row["Length"],
                "Mask": row["Mask"],
                "Notes": row["Notes"],
                "Alternate Name": row["Alternate Name"],
                "FLA Friendly": row["FLA Friendly"],
                "DataType": row["DataType"],
                "Level": row["Level"],
                "Royalty": row["Royalty"],
                "FieldCategory1": row["FieldCategory1"],
                "FieldCategory2": row["FieldCategory2"],
                "FieldCategory3": row["FieldCategory3"],
                "Sp. Use Code 1": row["Sp. Use Code 1"],
                "Sp. Use Code 2": row["Sp. Use Code 2"],
                "OptOutReasonCode": row["OptOutReasonCode"]
            }
        }

        json_str = json.dumps(json_obj, indent=4)

        # Prepare the command
        urn = f"urn:li:glossaryTerm:{row['Field Name']}"
        command = f'datahub put --urn "{urn}" -a glossaryTermInfo -d \'{json_str}\''

        # Run the external command
        run_external_command(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Excel file and call datahub put for each row.')
    parser.add_argument('excel_file_path', type=str, help='The path to the Excel file')

    args = parser.parse_args()
    excel_to_json_and_call_datahub(args.excel_file_path)


