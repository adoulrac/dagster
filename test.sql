CREATE OR REPLACE PACKAGE Your_Package_Name AS
  PROCEDURE refreshData;
END Your_Package_Name;
/

CREATE OR REPLACE PACKAGE BODY Your_Package_Name AS
  PROCEDURE refreshData IS
    -- Declare variables for logging
    v_log_message VARCHAR2(4000);
    v_log_timestamp TIMESTAMP := SYSTIMESTAMP;

    -- Other variables for your logic
    v_table_name VARCHAR2(30);
    v_output_table_name VARCHAR2(30) := 'your_output_table';
    v_sql_query VARCHAR2(1000);

    -- Variables for dynamic column check
    v_column_count NUMBER;

  BEGIN
    -- Log start of the procedure
    v_log_message := 'Refresh Procedure started at ' || TO_CHAR(v_log_timestamp, 'YYYY-MM-DD HH24:MI:SS');
    DBMS_OUTPUT.PUT_LINE(v_log_message);

    -- Your logic to query metadata, loop through tables, and insert data
    FOR table_rec IN (SELECT table_name FROM your_metadata_table WHERE your_rules_condition) LOOP
      v_table_name := table_rec.table_name;

      -- Check if columns to insert are available on the table
      SELECT COUNT(*)
      INTO v_column_count
      FROM all_tab_columns
      WHERE table_name = v_table_name
        AND column_name IN ('column1', 'column2', 'column3'); -- Replace with your column names

      -- Proceed with insert only if all columns are available
      IF v_column_count = 3 /* Replace with the actual number of columns */ THEN
        v_sql_query := 'INSERT INTO ' || v_output_table_name || ' SELECT * FROM ' || v_table_name || ' WHERE NOT EXISTS (SELECT 1 FROM ' || v_output_table_name || ' WHERE your_condition)';
        EXECUTE IMMEDIATE v_sql_query;

        -- Log table processing
        v_log_message := 'Processed table ' || v_table_name || ' at ' || TO_CHAR(SYSTIMESTAMP, 'YYYY-MM-DD HH24:MI:SS');
        DBMS_OUTPUT.PUT_LINE(v_log_message);
      ELSE
        -- Log a message if columns are not available
        v_log_message := 'Skipped table ' || v_table_name || ' due to missing columns';
        DBMS_OUTPUT.PUT_LINE(v_log_message);
      END IF;
    END LOOP;

    -- Log completion of the procedure
    v_log_message := 'Refresh Procedure completed at ' || TO_CHAR(SYSTIMESTAMP, 'YYYY-MM-DD HH24:MI:SS');
    DBMS_OUTPUT.PUT_LINE(v_log_message);
  EXCEPTION
    WHEN OTHERS THEN
      -- Log any exceptions
      v_log_message := 'Error: ' || SQLERRM;
      DBMS_OUTPUT.PUT_LINE(v_log_message);
  END refreshData;
END Your_Package_Name;
/