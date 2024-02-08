import os
from dagster import (
    ModeDefinition,
    PresetDefinition,
    pipeline,
    solid,
    sensor,
    Field,
    AssetMaterialization,
)
from dagster.core.storage.asset_materialization import FileMaterialization
from dagster_aws.s3 import s3_pickle_io_manager

# Define a solid to run the Python application
@solid(
    config={"python_command": Field(str, description="Command to run the Python application")}
)
def run_python_application(context):
    python_command = context.solid_config["python_command"]

    try:
        # Run the Python application using subprocess or any appropriate method
        os.system(python_command)

        context.log.info("Python application executed successfully.")
    except Exception as e:
        context.log.error(f"Error executing Python application: {str(e)}")

# Define a sensor to detect files matching a certain pattern
@sensor(pipeline_name="python_app_pipeline")
def file_sensor(context):
    # Specify the directory and file pattern to watch for
    directory_path = "/path/to/your/files"
    file_pattern = "your_file_pattern*.txt"

    # Check if there are any files matching the pattern
    matching_files = [
        filename for filename in os.listdir(directory_path) if filename.endswith(".txt")
    ]

    # Return a list of events if there are matching files
    if matching_files:
        return [AssetMaterialization(asset_key=f"file_sensor:{filename}") for filename in matching_files]

# Define the Dagster pipeline
@pipeline(
    mode_defs=[
        ModeDefinition(
            name="default",
            resource_defs={
                "io_manager": s3_pickle_io_manager,
            },
        ),
    ],
    preset_defs=[
        PresetDefinition.from_pkg_resources(
            "default",
            solid_subset=["run_python_application"],
            config={
                "solids": {
                    "run_python_application": {
                        "config": {"python_command": "python your_application.py"}
                    }
                }
            },
        )
    ],
)
def python_app_pipeline():
    run_python_application()


# Note: Replace '/path/to/your/files' and 'your_file_pattern*.txt' with the actual directory and file pattern.
