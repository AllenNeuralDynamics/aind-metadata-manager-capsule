import aind_metadata_manager.metadata_manager as manager
import json
import logging
import os

from log_schema import setup_logging
from pathlib import Path

def run():
    """
    Run the capsule to process metadata.
    """
    data_description_file = tuple(Path("/data").rglob("data_description.json"))
    if not data_description_file:
        raise FileNotFoundError(
            f"No data description in input folder"
        )
    with open(data_description_file[0], "r") as f:
        data_description = json.load(f)

    ### logging setup
    process_name = os.getenv("PROCESS_NAME", "aind-metadata-manager-capsule")
    pipeline_name = os.getenv("PIPELINE_NAME", "")
    setup_logging(
        (Path(__file__).parent /  "logging.yml").as_posix(),
        model={
            "acquisition_name": data_description["name"],
            "process_name": process_name,
            "pipeline_name": pipeline_name    
        },
    ) 
    logging.info(
        "Starting metadata aggregation", extra={"event_type": "stage_start"}
    )

    manager.run()

    logging.info(
        "Pipeline stage completed", extra={"event_type": "stage_complete"} 
    )

if __name__ == "__main__":
    try:
        run()
    except Exception:
        logging.exception("Pipeline stage failed", extra={"event_type": "stage_error"})
        raise