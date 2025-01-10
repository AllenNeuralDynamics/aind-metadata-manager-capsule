""" top level run script """

import argparse
import json
from pathlib import Path
import shutil

from aind_data_schema.core.processing import DataProcess, PipelineProcess, Processing


def copy_ancillary_files(args: argparse.Namespace) -> None:
    """
    Copy ancillary files from /data to /results
    """
    ancillary_files = ["procedures.json", "subject.json", "session.json"]
    for file in ancillary_files:
        try:
            shutil.copy(f"{args.input_dir}/{file}", f"{args.output_dir}/{file}")
        except FileNotFoundError:
            print(f"Could not find {file} in {args.input_dir}")


def str2bool(value):
    """Convert string representations of boolean values to actual booleans"""
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Pipeline Processing Metadata Aggregator"
    )

    parser.add_argument("--verbose", action="store_true", help="Print verbose output")

    parser.add_argument("--input_dir", type=str, default="/data", help="Input directory")

    parser.add_argument(
        "--output_dir", type=str, default="/results", help="Output directory"
    )

    parser.add_argument(
        "--processor_full_name",
        type=str,
        help="Name of person responsible for processing pipeline",
    )

    parser.add_argument(
        "--pipeline_version",
        type=str,
        help="Version of the pipeline",
    )

    parser.add_argument(
        "--pipeline_url",
        type=str,
        help="URL to the pipeline code",
    )

    parser.add_argument(
        "--note",
        type=str,
        help="Notes",
    )

    parser.add_argument('--copy-ancillary-files', type=str2bool,
                      default=False,
                      help='Boolean flag accepting true/false values')
    return parser.parse_args()


def run() -> None:
    """
    This function finds all files in the '/data' directory with name like
    '*data_process.json'. It deserializes each into an aind-data-schema
    DataProcess object, then creates a single processing.json file.
    """

    args = parse_args()
    # processor_full_name is required. if it is not provided by args,
    # look for processor_full_name.txt in the input directory.
    if args.processor_full_name is None:
        try:
            with open(f"{args.input_dir}/processor_full_name.txt") as f:
                args.processor_full_name = f.read().strip()
        except FileNotFoundError:
            raise ValueError(
                f"processor_full_name not found via args or in \
                {args.input_dir}/processor_full_name.txt"
            )

    data_processes = []

    data_process_files = list(Path(args.input_dir).rglob("*data_process.json"))

    if args.verbose:
        print(f"Found {len(list(data_process_files))} data_process.json files")

    for file in data_process_files:
        if args.verbose:
            print(file)

        with open(file) as f:
            data_processes.append(DataProcess.model_validate(json.load(f)))

    processing = Processing(
        processing_pipeline=PipelineProcess(
            data_processes=data_processes,
            processor_full_name=args.processor_full_name,
            pipeline_version=args.pipeline_version,
            pipeline_url=args.pipeline_url,
            note=args.note,
        )
    )

    processing.write_standard_file(args.output_dir)

    if args.copy_ancillary_files:
        copy_ancillary_files(args)

if __name__ == "__main__":
    run()
