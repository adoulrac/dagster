from dagster import ModeDefinition, PresetDefinition, pipeline, solid, Field
from dagster_aws.s3 import s3_pickle_io_manager
import cx_Oracle

# Define a solid to run the Oracle procedure
@solid(config={"oracle_connection_string": Field(str, description="Oracle connection string")})
def run_oracle_procedure(context):
    oracle_connection_string = context.solid_config["oracle_connection_string"]
    
    # Establish a connection to Oracle
    connection = cx_Oracle.connect(oracle_connection_string)
    cursor = connection.cursor()

    try:
        # Replace 'YOUR_PROCEDURE_NAME' with the actual name of your Oracle procedure
        procedure_name = 'YOUR_PROCEDURE_NAME'
        
        # Execute the Oracle procedure
        cursor.callproc(procedure_name)

        # Commit the changes
        connection.commit()

        context.log.info(f"Oracle procedure '{procedure_name}' executed successfully.")
    except Exception as e:
        context.log.error(f"Error executing Oracle procedure: {str(e)}")
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

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
            solid_subset=["run_oracle_procedure"],
            config={"solids": {"run_oracle_procedure": {"config": {"oracle_connection_string": "YOUR_CONNECTION_STRING"}}}},
        )
    ],
)
def oracle_procedure_pipeline():
    run_oracle_procedure()

# Note: Replace 'YOUR_CONNECTION_STRING' with the actual Oracle connection string.
# The connection string format: "username/password@hostname:port/service_name"

# my_dagster_repository.py

from dagster import RepositoryDefinition, daily_schedule

from my_dag import my_dag  # Import your Dag definition

repository = RepositoryDefinition(
    name='my_repository',
    pipelines=[my_dag],
    schedules={
        'my_daily_schedule': daily_schedule(
            pipeline_name='my_dag',
            start_date='2024-01-01',  # Replace with the desired start date
            execution_timezone='UTC',  # Adjust the timezone accordingly
            cron_schedule='0 7 * * *',  # Schedule to run at 7 AM every day
        )
    },
)
