import argparse
from pathlib import Path
import csv
import os



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs_dir", help=(
        "PATH to the DIRECTORY that contains CSV files that need to be combined. "
        "by default is set to results directory"
        ))
    parser.add_argument("--output_file_path", help=(
        "OPTIONAL RELATIVE PATH to outputfile. "
        "by default set to combined_results.csv in inputs_dir"
        ))
    args=parser.parse_args()

    inputs_dir=args.inputs_dir
    output_file_path=args.output_file_path
    if inputs_dir is None:
        inputs_dir=Path(os.getcwd()).joinpath("results")
    else:
        inputs_dir=Path(inputs_dir)

    output_file_path=args.output_file_path
    if output_file_path is None:
        output_file_path=inputs_dir.joinpath("combined_results.csv")
    else:
        output_file_path=Path(output_file_path)

    header = ['title', 'link', 'deadline']

    # Initialize an empty list to store all the rows
    combined_results = []

    # Loop through all the CSV files in the results directory
    for csv_file in [filename for filename in inputs_dir.glob("*.csv") if "combined" not in filename.name]:
        print(f"Processing {csv_file}...")
        # Open each CSV file and read its content
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                combined_results.append(row)

    # Write the combined results into a new CSV file
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()  # Write the header once
        writer.writerows(combined_results)  # Write all the combined rows


if __name__=="__main__":
    main()