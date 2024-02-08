from dagster import (
    ModeDefinition,
    PresetDefinition,
    pipeline,
    solid,
    sensor,
    InputDefinition,
    OutputDefinition,
    EventMetadata,
    AssetMaterialization,
    DependencyDefinition,
    solid_output,
)
from dagster_aws.s3 import s3_pickle_io_manager
from dagster.core.definitions.decorators import lambda_solid
import cx_Oracle

# Define a solid to run an Oracle procedure
@solid(config={"oracle_connection_string": str, "procedure_name": str})
def run_oracle_procedure(context):
    oracle_connection_string = context.solid_config["oracle_connection_string"]
    procedure_name = context.solid_config["procedure_name"]

    connection = cx_Oracle.connect(oracle_connection_string)
    cursor = connection.cursor()

    try:
        # Execute the Oracle procedure
        cursor.callproc(procedure_name)
        connection.commit()

        context.log.info(f"Oracle procedure '{procedure_name}' executed successfully.")
        yield AssetMaterialization(asset_key=f"oracle_procedure:{procedure_name}")
    except Exception as e:
        context.log.error(f"Error executing Oracle procedure: {str(e)}")
        context.emit_event(
            "ErrorEvent",
            event_metadata=EventMetadata.text(f"Error executing Oracle procedure: {str(e)}"),
        )
    finally:
        cursor.close()
        connection.close()

# Define a sensor to trigger the pipeline when a SQL query returns a result
@sensor(pipeline_name="multi_step_pipeline")
def sql_query_sensor(context):
    # Your logic to check if the SQL query returns a result
    if sql_query_returns_result():
        return [AssetMaterialization(asset_key="sql_query_result")]

# Define a pipeline with multiple steps
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
            config={
                "solids": {
                    "run_oracle_procedure_1": {
                        "config": {
                            "oracle_connection_string": "YOUR_CONNECTION_STRING_1",
                            "procedure_name": "YOUR_PROCEDURE_NAME_1",
                        }
                    },
                    "run_oracle_procedure_2": {
                        "config": {
                            "oracle_connection_string": "YOUR_CONNECTION_STRING_2",
                            "procedure_name": "YOUR_PROCEDURE_NAME_2",
                        }
                    },
                    # Add configuration for additional steps as needed
                }
            },
        )
    ],
)
def multi_step_pipeline():
    result_1 = run_oracle_procedure.alias("run_oracle_procedure_1")()
    result_2 = run_oracle_procedure.alias("run_oracle_procedure_2")(result_1)

# Lambda solid to send an email notification
@lambda_solid(
    input_defs=[InputDefinition("event", str)],
    output_def=OutputDefinition(str),
)
def send_email_notification(context, event):
    # Your logic to send an email notification
    # You can use external libraries or services for email notifications
    # Example: send_email_notification_function(event)
    context.log.info(f"Email notification sent: {event}")
    return f"Email notification sent: {event}"

# Define dependencies between steps and email notification
multi_step_pipeline_with_email = multi_step_pipeline.depends_on(
    send_email_notification("SuccessEvent").with_input(
        run_oracle_procedure.alias("run_oracle_procedure_1").output
    )
)
multi_step_pipeline_with_email = multi_step_pipeline_with_email.depends_on(
    send_email_notification("SuccessEvent").with_input(
        run_oracle_procedure.alias("run_oracle_procedure_2").output
    )
)

# Define an error event handling lambda solid
@lambda_solid(
    input_defs=[InputDefinition("event", str)],
    output_def=OutputDefinition(str),
)
def handle_error_event(context, event):
    # Your logic to handle error events
    # Example: handle_error_event_function(event)
    context.log.error(f"Error event received: {event}")
    return f"Error event handled: {event}"

# Define dependencies between error event handling and pipeline steps
multi_step_pipeline_with_error_handling = (
    multi_step_pipeline_with_email.depends_on(
        handle_error_event.with_input(run_oracle_procedure.alias("run_oracle_procedure_1").output)
    )
)
multi_step_pipeline_with_error_handling = (
    multi_step_pipeline_with_error_handling.depends_on(
        handle_error_event.with_input(run_oracle_procedure.alias("run_oracle_procedure_2").output)
    )
)

# Note: Replace placeholders like 'YOUR_CONNECTION_STRING_1', 'YOUR_PROCEDURE_NAME_1', etc., with actual values.
# Also, implement the actual logic for sending email notifications and handling error events.

# Additional notes:
# - The `sql_query_returns_result` function should be implemented to check if the SQL query returns a result.
# - The `send_email_notification_function` and `handle_error_event_function` functions should be implemented
#   to send email notifications and handle error events, respectively.
