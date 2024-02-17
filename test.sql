DECLARE
  l_clob CLOB := 'Your CLOB string here';
  l_separator VARCHAR2(10) := ','; -- Set your separator here
  l_substr VARCHAR2(4000);
  l_start_pos PLS_INTEGER := 1;
  l_end_pos PLS_INTEGER;
BEGIN
  -- Loop through the CLOB string
  WHILE l_start_pos <= DBMS_LOB.GETLENGTH(l_clob) LOOP
    -- Find the position of the separator
    l_end_pos := DBMS_LOB.INSTR(l_clob, l_separator, l_start_pos);

    -- If separator is found, extract substring
    IF l_end_pos > 0 THEN
      l_substr := DBMS_LOB.SUBSTR(l_clob, l_end_pos - l_start_pos, l_start_pos);
      l_start_pos := l_end_pos + LENGTH(l_separator);
    ELSE
      -- If no separator found, extract the remaining part
      l_substr := DBMS_LOB.SUBSTR(l_clob, DBMS_LOB.GETLENGTH(l_clob) - l_start_pos + 1, l_start_pos);
      l_start_pos := DBMS_LOB.GETLENGTH(l_clob) + 1;
    END IF;

    -- Process the extracted substring (replace this with your logic)
    DBMS_OUTPUT.PUT_LINE('Substring: ' || l_substr);

    -- Continue looping
  END LOOP;
END;
/