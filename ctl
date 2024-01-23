LOAD DATA
INFILE 'your_data_file.dat'
APPEND
INTO TABLE your_table
FIELDS TERMINATED BY ',' optionally enclosed by '"'
TRAILING NULLCOLS
(
  COLUMN1,
  COLUMN2,
  COLUMN3
)
WHEN (1:15) = 'YourExpectedHeader'

  import subprocess

# Your data file
data_file = 'your_data_file.dat'

# Define the expected header string
expected_header = 'YourExpectedHeader'

# Read the first row to check if it matches the expected header
with open(data_file, 'r') as file:
    header = file.readline().strip()

# Check if the header matches the expected header
if header != expected_header:
    print("Error: Header does not match the expected value.")
    exit(1)

# If the header is correct, proceed with SQL*Loader
sqlldr_command = f'sqlldr username/password control=your_control_file.ctl'
subprocess.run(sqlldr_command, shell=True)
