"""top level run script"""

import json
import shutil
from pathlib import Path

from aind_data_schema.core.data_description import DerivedDataDescription
from aind_data_schema.core.processing import (DataProcess, PipelineProcess,
                                              Processing)
from aind_data_schema_models.modalities import Modality
from aind_metadata_upgrader.data_description_upgrade import \
    DataDescriptionUpgrade
from pydantic import Field
from pydantic_settings import BaseSettings


class ProcessSettings(BaseSettings, cli_parse_args=True):
    """Command line arguments for the processing aggregator"""

    verbose: bool = Field(default=False, description="Print verbose output")
    data_summary: str = Field(
        default="",
        description="Data summary file to overwrite in the derived data description",
    )
    input_dir: str = Field(
        default="/data",
        description="Input directory containing data_process.json files",
    )
    modality: str = Field(
        default="",
        description="Modality(ies) to overwrite in the derived data description",
    )
    output_dir: str = Field(
        default="/results", description="Output directory for processing.json"
    )
    processor_full_name: str = Field(
        default="", description="Name of person responsible for processing pipeline"
    )
    pipeline_version: str = Field(default="", description="Version of the pipeline")
    pipeline_url: str = Field(default="", description="URL to the pipeline code")
    note: str = Field(default="", description="Notes")
    copy_ancillary_files: bool = Field(
        default=False,
        description="Copy ancillary files (procedures.json, subject.json, session.json) to output",
    )


def copy_ancillary_files(settings: ProcessSettings) -> None:
    """
    Copy ancillary files from input_dir to output_dir
    """
    ancillary_files = ["procedures.json", "subject.json", "session.json"]
    for file in ancillary_files:
        try:
            shutil.copy(f"{settings.input_dir}/{file}", f"{settings.output_dir}/{file}")
        except FileNotFoundError:
            print(f"Could not find {file} in {settings.input_dir}")


def create_derived_data_description(settings: ProcessSettings) -> None:
    """
    Create a derived data description

    Parameters
    ----------
    settings : ProcessSettings
        Command line arguments

    """
    data_description_fp = Path(settings.input_dir) / "data_description.json"
    with open(data_description_fp) as j:
        data_description = json.load(j)
    data_description_upgrader = DataDescriptionUpgrade(
        old_data_description_dict=data_description
    )
    data_upgrader = data_description_upgrader.upgrade()
    if settings.data_summary:
        data_upgrader.data_summary = settings.data_summary
    if settings.modality:
        validated_modalities = []
        modality_found = False
        for modality_class in Modality.ALL:
            if settings.modality in modality_class().abbreviation:
                validated_modalities.append(modality_class())
                modality_found = True
                break
        if not modality_found:
            raise ValueError(
                f"Modality '{settings.modality}' is not a valid modality. "
                f"Valid modalities are: {Modality.ONE_OF}"
            )
        
    data_upgrader.modality = validated_modalities
    derived_data_description = DerivedDataDescription.from_data_description(
        data_description=data_upgrader, process_name="processed"
    )
    derived_data_description.write_standard_file(output_directory=settings.output_dir)


def run() -> None:
    """
    This function finds all files in the '/data' directory with name like
    '*data_process.json'. It deserializes each into an aind-data-schema
    DataProcess object, then creates a single processing.json file.
    """

    settings = ProcessSettings()
    # processor_full_name is required. if it is not provided by args,
    # look for processor_full_name.txt in the input directory.
    if settings.processor_full_name is None:
        try:
            with open(f"{settings.input_dir}/processor_full_name.txt") as f:
                settings.processor_full_name = f.read().strip()
        except FileNotFoundError:
            raise ValueError(
                f"processor_full_name not found via args or in \
                {settings.input_dir}/processor_full_name.txt"
            )

    data_processes = []

    data_process_files = list(Path(settings.input_dir).rglob("*data_process.json"))

    if settings.verbose:
        print(f"Found {len(list(data_process_files))} data_process.json files")

    for file in data_process_files:
        if settings.verbose:
            print(file)

        with open(file) as f:
            data_processes.append(DataProcess.model_validate(json.load(f)))

    processing = Processing(
        processing_pipeline=PipelineProcess(
            data_processes=data_processes,
            processor_full_name=settings.processor_full_name,
            pipeline_version=settings.pipeline_version,
            pipeline_url=settings.pipeline_url,
            note=settings.note,
        )
    )

    processing.write_standard_file(settings.output_dir)

    if settings.copy_ancillary_files:
        copy_ancillary_files(settings)

    if settings.data_summary or settings.modality:
        create_derived_data_description(settings)


if __name__ == "__main__":
    run()
