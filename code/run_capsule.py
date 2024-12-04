""" top level run script """
import argparse
import datetime
import json
from pathlib import Path

from aind_data_schema.core.processing import (DataProcess, PipelineProcess,
                                              Processing, ProcessName)


def run():
    """
    This function finds all files in the '/data' directory with name like
    '*data_process.json'. It deserializes each into an aind-data-schema
    DataProcess object, then creates a single processing.json file.
    """

    parser = argparse.ArgumentParser(
        description="Pipeline Processing Metadata Aggregator"
        )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )

    parser.add_argument(
        "--input_dir",
        type=str,
        default="/data",
        help="Input directory"
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="/results",
        help="Output directory"
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

    args = parser.parse_args()

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
            data_processes.append(
                DataProcess.model_validate(json.load(f))
                )

    processing = Processing(
        processing_pipeline=PipelineProcess(
            data_processes=data_processes,
            processor_full_name=args.processor_full_name,
            pipeline_version=args.pipeline_version,
            pipeline_url=args.pipeline_url,
            note=args.note
        )
    )

    processing.write_standard_file(args.output_dir)


if __name__ == "__main__":
    run()
