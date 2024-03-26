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

from dagster import ModeDefinition, daily_schedule, job, op, pipeline, repository, schedule
from dagster_oracle import OracleResource
import cx_Oracle

# Define Oracle resources for each environment
oracle_dev = OracleResource(config={"connection_string": "dev_connection_string"})
oracle_uat = OracleResource(config={"connection_string": "uat_connection_string"})
oracle_prod = OracleResource(config={"connection_string": "prod_connection_string"})

@op
def run_oracle_procedure(context):
    oracle_connection = context.resources.oracle.get_connection()
    cursor = oracle_connection.cursor()

    # Execute your Oracle procedure
    cursor.callproc("your_procedure_name", args=())

    cursor.close()
    oracle_connection.close()

@op
def process_result(context, result):
    # Process the result from the Oracle procedure
    processed_result = result  # Placeholder for actual processing logic
    return processed_result

@op
def insert_into_oracle_table(context, processed_result):
    oracle_connection = context.resources.oracle.get_connection()
    cursor = oracle_connection.cursor()

    # Insert processed result into another Oracle table
    cursor.execute("INSERT INTO your_table_name VALUES (:1, :2)", processed_result)

    cursor.close()
    oracle_connection.commit()
    oracle_connection.close()

@pipeline
def oracle_pipeline():
    result = run_oracle_procedure()
    processed_result = process_result(result)
    insert_into_oracle_table(processed_result)

# Define mode definitions for each environment
dev_mode = ModeDefinition(resource_defs={"oracle": oracle_dev})
uat_mode = ModeDefinition(resource_defs={"oracle": oracle_uat})
prod_mode = ModeDefinition(resource_defs={"oracle": oracle_prod})

# Define your Dagster schedules here
# Example: Run the job daily at midnight
@daily_schedule(
    pipeline_name="oracle_pipeline",
    start_date="2024-03-26T00:00:00",
    execution_time="00:00:00",
    mode="dev_mode",  # Specify the mode to use
)
def oracle_daily_schedule(date):
    return {}

# Define the repository that contains the pipeline and schedule
@repository
def my_repository():
    return [oracle_pipeline, oracle_daily_schedule]
