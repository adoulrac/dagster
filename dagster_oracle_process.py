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