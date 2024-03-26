from dagster import ModeDefinition, daily_schedule, job, op, pipeline, repository, schedule
from dagster import asset, AssetMaterialization, OutputDefinition, InputDefinition
from dagster_oracle import OracleResource
import cx_Oracle

# Define Oracle resources for each environment
oracle_dev = OracleResource(config={"connection_string": "dev_connection_string"})
oracle_uat = OracleResource(config={"connection_string": "uat_connection_string"})
oracle_prod = OracleResource(config={"connection_string": "prod_connection_string"})

# Define operation to pull data from the database
@op
def pull_data_from_db(context):
    oracle_connection = context.resources.oracle.get_connection()
    cursor = oracle_connection.cursor()

    # Pull data from the database
    cursor.execute("SELECT * FROM your_table_name")
    data = cursor.fetchall()

    cursor.close()
    oracle_connection.close()

    return data

# Define operation to run Oracle procedure
@op
def run_oracle_procedure(context, pulled_data):
    # Placeholder for running Oracle procedure
    pass

# Define operation to process result
@op
def process_result(context, result):
    # Placeholder for processing result
    pass

# Define operation to insert into Oracle table
@op
def insert_into_oracle_table(context, processed_result):
    # Placeholder for inserting into Oracle table
    pass

# Define asset for pulled data
@asset
def pulled_data_asset(pulled_data):
    return AssetMaterialization(asset_key="pulled_data", description="Data pulled from the database", metadata={"pulled_data": pulled_data})

# Define pipeline
@pipeline
def oracle_pipeline():
    data = pull_data_from_db()
    result = run_oracle_procedure(data)
    processed_result = process_result(result)
    insert_into_oracle_table(processed_result)

# Define mode definitions for each environment
dev_mode = ModeDefinition(resource_defs={"oracle": oracle_dev})
uat_mode = ModeDefinition(resource_defs={"oracle": oracle_uat})
prod_mode = ModeDefinition(resource_defs={"oracle": oracle_prod})

# Define dependencies
oracle_pipeline.with_dependencies(
    {
        run_oracle_procedure: {
            "pulled_data": InputDefinition("pulled_data", dagster_type=DataType)
        },
        pulled_data_asset: {
            "pulled_data": OutputDefinition(dagster_type=DataType)
        }
    }
)

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