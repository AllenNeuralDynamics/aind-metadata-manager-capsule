"""Metadata management script for processing pipeline aggregation"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Optional

from aind_data_schema.core.data_description import DerivedDataDescription
from aind_data_schema.core.processing import DataProcess, PipelineProcess, Processing
from aind_data_schema_models.modalities import Modality
from aind_metadata_upgrader.data_description_upgrade import DataDescriptionUpgrade
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class MetadataSettings(BaseSettings, cli_parse_args=True):
    """Command line arguments for the metadata management pipeline"""

    verbose: bool = Field(default=False, description="Print verbose output")
    
    # Input/Output directories
    input_dir: str = Field(
        default="/data",
        description="Input directory containing data_process.json files",
    )
    output_dir: str = Field(
        default="/results", description="Output directory for processing.json and metadata"
    )
    
    # Required fields
    processor_full_name: str = Field(
        description="Name of person responsible for processing pipeline"
    )
    
    # Pipeline information with defaults
    pipeline_version: str = Field(
        default_factory=lambda: os.environ.get("VERSION", ""),
        description="Version of the pipeline (defaults to VERSION env var)"
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
        description="Skip copying ancillary files (procedures.json, subject.json, session.json, rig.json)"
    )
    
    @field_validator('processor_full_name', mode='before')
    @classmethod
    def validate_processor_name(cls, v, info):
        """Validate processor_full_name is provided or can be read from file"""
        if not v:
            # Try to get input_dir from the validation info context
            input_dir = info.data.get('input_dir', '/data') if info.data else '/data'
            try:
                processor_file = Path(input_dir) / "processor_full_name.txt"
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
        self.ancillary_files = ["procedures.json", "subject.json", "session.json", "rig.json"]
    
    def copy_ancillary_files(self) -> None:
        """
        Copy ancillary files from input_dir to output_dir

        Raises
        ------
        FileNotFoundError
            If any required ancillary file is not found
        """
        if self.settings.skip_ancillary_files:
            if self.settings.verbose:
                print("Skipping ancillary files copy (--skip_ancillary_files=True)")
            return
        
        copied_files = []
        missing_files = []
        
        for file in self.ancillary_files:
            source_path = Path(self.settings.input_dir) / file
            dest_path = Path(self.settings.output_dir) / file
            
            try:
                if source_path.exists():
                    shutil.copy(source_path, dest_path)
                    copied_files.append(file)
                    if self.settings.verbose:
                        print(f"Copied {file}")
                else:
                    missing_files.append(file)
                    if self.settings.verbose:
                        print(f"Warning: {file} not found in {self.settings.input_dir}")
            except Exception as e:
                raise FileNotFoundError(
                    f"Error copying {file} from {source_path} to {dest_path}: {e}"
                )
        
        if self.settings.verbose:
            print(f"Successfully copied {len(copied_files)} ancillary files")
            if missing_files:
                print(f"Missing files: {missing_files}")
    
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
        data_description_fp = Path(self.settings.input_dir) / "data_description.json"
        
        if not data_description_fp.exists():
            if self.settings.verbose:
                print(f"Warning: data_description.json not found at {data_description_fp}")
            return
        
        with open(data_description_fp) as f:
            data_description = json.load(f)
        
        data_description_upgrader = DataDescriptionUpgrade(
            old_data_description_dict=data_description
        )
        data_upgrader = data_description_upgrader.upgrade()
        
        # Apply optional overrides
        if self.settings.data_summary:
            data_upgrader.data_summary = self.settings.data_summary
            if self.settings.verbose:
                print(f"Set data_summary: {self.settings.data_summary}")
        
        if self.settings.modality:
            validated_modalities = self._validate_modality(self.settings.modality)
            data_upgrader.modality = validated_modalities
            if self.settings.verbose:
                print(f"Set modality: {[m.abbreviation for m in validated_modalities]}")

        # Create derived data description
        derived_data_description = DerivedDataDescription.from_data_description(
            data_description=data_upgrader, process_name="processed"
        )
        derived_data_description.write_standard_file(output_directory=self.settings.output_dir)
        
        if self.settings.verbose:
            print("Created derived data description")
    
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
        data_process_files = list(Path(self.settings.input_dir).rglob("*data_process.json"))

        if self.settings.verbose:
            print(f"Found {len(data_process_files)} data_process.json files")

        for file_path in data_process_files:
            if self.settings.verbose:
                print(f"Processing: {file_path}")

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
            print(f"Created processing metadata with {len(data_processes)} data processes")
            print(f"Pipeline version: {self.settings.pipeline_version}")
            print(f"Processor: {self.settings.processor_full_name}")
        
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
        manager = MetadataManager(settings)
        
        if settings.verbose:
            print("=== Metadata Management Pipeline ===")
            print(f"Input directory: {settings.input_dir}")
            print(f"Output directory: {settings.output_dir}")
            print(f"Processor: {settings.processor_full_name}")
            print(f"Pipeline version: {settings.pipeline_version}")
        
        # Create main processing metadata
        processing = manager.create_processing_metadata()
        processing.write_standard_file(settings.output_dir)
        
        if settings.verbose:
            print("✓ Written processing.json")
        
        # Copy ancillary files (by default, unless skipped)
        manager.copy_ancillary_files()
        
        # Always attempt to create derived data description
        manager.create_derived_data_description()
        
        if settings.verbose:
            print("=== Pipeline completed successfully ===")
            
    except Exception as e:
        print(f"Error: {e}")
        raise


# Legacy function stubs for backward compatibility (deprecated)
def copy_ancillary_files(settings) -> None:
    """Deprecated: Use MetadataManager.copy_ancillary_files() instead"""
    manager = MetadataManager(settings)
    manager.copy_ancillary_files()


def create_derived_data_description(settings) -> None:
    """Deprecated: Use MetadataManager.create_derived_data_description() instead"""
    manager = MetadataManager(settings)
    manager.create_derived_data_description()


if __name__ == "__main__":
    run()
