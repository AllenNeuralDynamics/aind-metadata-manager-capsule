"""Metadata management script for processing pipeline aggregation"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import List

from aind_data_schema.core.data_description import DerivedDataDescription
from aind_data_schema.core.processing import (DataProcess, PipelineProcess,
                                              Processing)
from aind_data_schema_models.modalities import Modality
from aind_metadata_upgrader.data_description_upgrade import \
    DataDescriptionUpgrade
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Set up logging
logger = logging.getLogger(__name__)


class MetadataSettings(BaseSettings, cli_parse_args=True):
    """Command line arguments for the metadata management pipeline"""

    verbose: bool = Field(default=False, description="Print verbose output")

    # Input/Output directories - automatically converted to Path objects by BaseSettings
    input_dir: Path = Field(
        default=Path("/data"),
        description="Input directory containing data_process.json files",
    )
    output_dir: Path = Field(
        default=Path("/results"),
        description="Output directory for processing.json and metadata",
    )

    # Required fields
    processor_full_name: str = Field(
        description="Name of person responsible for processing pipeline"
    )

    # Pipeline information with defaults
    pipeline_version: str = Field(
        default_factory=lambda: os.environ.get("VERSION", ""),
        description="Version of the pipeline (defaults to VERSION env var)",
    )
    pipeline_url: str = Field(default="", description="URL to the pipeline code")
    note: str = Field(default="", description="Notes")

    # Data description fields
    data_summary: str = Field(
        default="",
        description="Data summary to overwrite in the derived data description",
    )
    modality: str = Field(
        default="",
        description="Modality to overwrite in the derived data description",
    )

    # File management - copy ancillary files by default, with opt-out
    skip_ancillary_files: bool = Field(
        default=False,
        description="Skip copying ancillary files (procedures.json, subject.json, session.json, rig.json)",
    )

    @field_validator("processor_full_name", mode="before")
    @classmethod
    def validate_processor_name(cls, v, info):
        """Validate processor_full_name is provided or can be read from file"""
        if not v:
            # Try to get input_dir from the validation info context
            input_dir_raw = (
                info.data.get("input_dir", "/data") if info.data else "/data"
            )
            # Ensure input_dir is a Path object
            input_dir = (
                Path(input_dir_raw)
                if not isinstance(input_dir_raw, Path)
                else input_dir_raw
            )
            try:
                processor_file = input_dir / "processor_full_name.txt"
                if processor_file.exists():
                    return processor_file.read_text().strip()
                else:
                    raise ValueError(
                        f"processor_full_name not provided via args and not found in "
                        f"{processor_file}"
                    )
            except Exception:
                raise ValueError(
                    f"processor_full_name is required. Provide it via --processor_full_name "
                    f"or create {input_dir}/processor_full_name.txt"
                )
        return v


class MetadataManager:
    """Manages processing metadata aggregation and file operations"""

    def __init__(self, settings: MetadataSettings):
        self.settings = settings
        self.ancillary_files = [
            "procedures.json",
            "subject.json",
            "session.json",
            "rig.json",
        ]

    def copy_ancillary_files(self) -> None:
        """
        Copy ancillary files from input_dir to output_dir using recursive search

        Raises
        ------
        FileNotFoundError
            If any required ancillary file is not found
        """
        if self.settings.skip_ancillary_files:
            if self.settings.verbose:
                logger.info(
                    "Skipping ancillary files copy (--skip_ancillary_files=True)"
                )
            return

        copied_files = []
        missing_files = []
        # input_dir and output_dir are already Path objects
        input_path = self.settings.input_dir
        output_path = self.settings.output_dir

        for file_name in self.ancillary_files:
            # Use recursive search (rglob) to find the file anywhere in the input directory
            matching_files = list(input_path.rglob(file_name))

            if matching_files:
                # Use the first match found
                source_path = matching_files[0]
                dest_path = output_path / file_name

                try:
                    # Ensure output directory exists
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(source_path, dest_path)
                    copied_files.append(file_name)
                    if self.settings.verbose:
                        logger.info(
                            f"Copied {file_name} from {source_path} to {dest_path}"
                        )
                except Exception as e:
                    raise FileNotFoundError(
                        f"Error copying {file_name} from {source_path} to {dest_path}: {e}"
                    )
            else:
                missing_files.append(file_name)
                if self.settings.verbose:
                    logger.warning(
                        f"{file_name} not found in {self.settings.input_dir} (searched recursively)"
                    )

        if self.settings.verbose:
            logger.info(f"Successfully copied {len(copied_files)} ancillary files")
            if missing_files:
                logger.info(f"Missing files: {missing_files}")
            if copied_files:
                logger.info("Copied files placed in output directory root")

    def create_derived_data_description(self) -> None:
        """
        Create a derived data description with optional modality override

        Raises
        ------
        FileNotFoundError
            If data_description.json is not found
        ValueError
            If specified modality is invalid
        """
        # Use recursive search (rglob) to find data_description.json anywhere in the input directory
        input_path = self.settings.input_dir
        matching_files = list(input_path.rglob("data_description.json"))

        if not matching_files:
            message = f"data_description.json not found in {input_path} (searched recursively)"
            if self.settings.verbose:
                logger.warning(message)
                logger.info("Skipping derived data description creation")
                logger.info(
                    "To create a derived data description, ensure data_description.json exists somewhere in the input directory"
                )
            else:
                logger.info(f"{message} - skipping derived data description creation")
            return

        # Use the first match found
        data_description_fp = matching_files[0]

        if self.settings.verbose:
            logger.info(f"Found data_description.json at {data_description_fp}")
            if len(matching_files) > 1:
                logger.info(
                    f"Multiple data_description.json files found, using: {data_description_fp}"
                )

        try:
            with open(data_description_fp) as f:
                data_description = json.load(f)

            if self.settings.verbose:
                logger.info("Successfully loaded data_description.json")

            data_description_upgrader = DataDescriptionUpgrade(
                old_data_description_dict=data_description
            )
            data_upgrader = data_description_upgrader.upgrade()

            if self.settings.verbose:
                logger.info("Successfully upgraded data description")

            # Apply optional overrides
            if self.settings.data_summary:
                data_upgrader.data_summary = self.settings.data_summary
                if self.settings.verbose:
                    logger.info(f"Set data_summary: {self.settings.data_summary}")

            if self.settings.modality:
                validated_modalities = self._validate_modality(self.settings.modality)
                data_upgrader.modality = validated_modalities
                if self.settings.verbose:
                    logger.info(
                        f"Set modality: {[m.abbreviation for m in validated_modalities]}"
                    )

            # Create derived data description
            derived_data_description = DerivedDataDescription.from_data_description(
                data_description=data_upgrader, process_name="processed"
            )

            # Ensure output_directory is a string for the API call
            output_dir_str = str(self.settings.output_dir)
            derived_data_description.write_standard_file(
                output_directory=output_dir_str
            )

            if self.settings.verbose:
                logger.info(
                    f"✓ Created derived data description at {output_dir_str}/data_description.json"
                )

        except Exception as e:
            logger.error(f"Error creating derived data description: {e}")
            if self.settings.verbose:
                import traceback

                logger.error(traceback.format_exc())
            raise

    def _validate_modality(self, modality_str: str) -> List[Modality]:
        """
        Validate and return modality objects

        Parameters
        ----------
        modality_str : str
            Modality abbreviation to validate

        Returns
        -------
        List[Modality]
            List of validated modality objects

        Raises
        ------
        ValueError
            If modality is not valid
        """
        validated_modalities = []
        modality_found = False

        for modality_class in Modality.ALL:
            if modality_str in modality_class().abbreviation:
                validated_modalities.append(modality_class())
                modality_found = True
                break

        if not modality_found:
            raise ValueError(
                f"Modality '{modality_str}' is not a valid modality. "
                f"Valid modalities are: {Modality.ONE_OF}"
            )

        return validated_modalities

    def collect_data_processes(self) -> List[DataProcess]:
        """
        Collect all DataProcess objects from data_process.json files

        Returns
        -------
        List[DataProcess]
            List of DataProcess objects found in input directory
        """
        data_processes = []
        # input_dir is already a Path object
        data_process_files = list(self.settings.input_dir.rglob("*data_process.json"))

        if self.settings.verbose:
            logger.info(f"Found {len(data_process_files)} data_process.json files")

        for file_path in data_process_files:
            if self.settings.verbose:
                logger.info(f"Processing: {file_path}")

            with open(file_path) as f:
                data_processes.append(DataProcess.model_validate(json.load(f)))

        return data_processes

    def create_processing_metadata(self) -> Processing:
        """
        Create Processing object with collected data processes

        Returns
        -------
        Processing
            Processing object containing all data processes and pipeline info
        """
        data_processes = self.collect_data_processes()

        processing = Processing(
            processing_pipeline=PipelineProcess(
                data_processes=data_processes,
                processor_full_name=self.settings.processor_full_name,
                pipeline_version=self.settings.pipeline_version,
                pipeline_url=self.settings.pipeline_url,
                note=self.settings.note,
            )
        )

        if self.settings.verbose:
            logger.info(
                f"Created processing metadata with {len(data_processes)} data processes"
            )
            logger.info(f"Pipeline version: {self.settings.pipeline_version}")
            logger.info(f"Processor: {self.settings.processor_full_name}")

        return processing


def run() -> None:
    """
    Main function to aggregate processing metadata and manage ancillary files.

    This function:
    1. Collects all DataProcess objects from input directory
    2. Creates a Processing object with pipeline metadata
    3. Copies ancillary files by default (unless skipped)
    4. Creates derived data description with optional modality override
    """
    try:
        settings = MetadataSettings()

        # Configure logging based on verbose setting
        log_level = logging.INFO if settings.verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        manager = MetadataManager(settings)

        if settings.verbose:
            logger.info("=== Metadata Management Pipeline ===")
            logger.info(f"Input directory: {settings.input_dir}")
            logger.info(f"Output directory: {settings.output_dir}")
            logger.info(f"Processor: {settings.processor_full_name}")
            logger.info(f"Pipeline version: {settings.pipeline_version}")

        # Create main processing metadata
        processing = manager.create_processing_metadata()
        # Ensure output_dir is a string for the API call
        processing.write_standard_file(str(settings.output_dir))

        if settings.verbose:
            logger.info("✓ Written processing.json")

        # Copy ancillary files (by default, unless skipped)
        manager.copy_ancillary_files()

        # Always attempt to create derived data description
        manager.create_derived_data_description()

        if settings.verbose:
            logger.info("=== Pipeline completed successfully ===")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    run()
