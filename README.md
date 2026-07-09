# aind-metadata-manager-capsule

## Usage
This capsule searches and input directory (default '/data') for serialized DataProcess objects named '*data_process.json'.
It aggregates them into a single processing.json file.


It requires the processor_full_name as described by [aind-data-schema](https://github.com/AllenNeuralDynamics/aind-data-schema/blob/04b53414fbc4f78fa66191cf3323db5b1cf96957/src/aind_data_schema/core/processing.py#L85). This can be input via the argument --processor_full_name or via <input_dir>/processor_full_name.txt containing a single line.

Optional Parameters:
- [pipeline_version](https://github.com/AllenNeuralDynamics/aind-data-schema/blob/04b53414fbc4f78fa66191cf3323db5b1cf96957/src/aind_data_schema/core/processing.py#L88)
- [pipeline_url](https://github.com/AllenNeuralDynamics/aind-data-schema/blob/04b53414fbc4f78fa66191cf3323db5b1cf96957/src/aind_data_schema/core/processing.py#L91)
- [note](https://github.com/AllenNeuralDynamics/aind-data-schema/blob/04b53414fbc4f78fa66191cf3323db5b1cf96957/src/aind_data_schema/core/processing.py#L)
