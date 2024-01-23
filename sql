WITH LabelValueSplit AS (
    SELECT
        REGEXP_SUBSTR(labels, '[^[-]]+', 1, LEVEL) AS label,
        REGEXP_SUBSTR(values, '[^[-]]+', 1, LEVEL) AS value,
        ROWNUM AS rn
    FROM your_table
    CONNECT BY LEVEL <= REGEXP_COUNT(labels, '[-]') + 1
    AND PRIOR labels = labels
    AND PRIOR DBMS_RANDOM.VALUE IS NOT NULL
)
SELECT label, value
FROM LabelValueSplit
ORDER BY rn;

WITH LabelValueSplit AS (
    SELECT
        REGEXP_SUBSTR(labels || '[-]', '[^[-]]+', 1, LEVEL) AS label,
        REGEXP_SUBSTR(values || '[-]', '[^[-]]+', 1, LEVEL) AS value,
        ROWNUM AS rn
    FROM your_table
    CONNECT BY LEVEL <= LEAST(REGEXP_COUNT(labels, '[-]') + 1, REGEXP_COUNT(values, '[-]') + 1)
    AND PRIOR labels = labels
    AND PRIOR values = values
    AND PRIOR DBMS_RANDOM.VALUE IS NOT NULL
)
SELECT label, value
FROM LabelValueSplit
ORDER BY rn;

WITH LabelValueSplit AS (
    SELECT
        REGEXP_SUBSTR(labels || '[-]', '[^[-]]+', 1, LEVEL) AS label,
        REGEXP_SUBSTR(values || '[-]', '[^[-]]+', 1, LEVEL) AS value,
        ROWNUM AS rn
    FROM your_table
    CONNECT BY LEVEL <= LEAST(REGEXP_COUNT(labels, '[-]') + 1, REGEXP_COUNT(values, '[-]') + 1)
    AND PRIOR labels = labels
    AND PRIOR values = values
)
SELECT label, value
FROM LabelValueSplit
ORDER BY rn;

WITH LabelValueSplit (label, value, label_part, value_part, rn) AS (
    SELECT
        TRIM(REGEXP_SUBSTR(labels, '[^[-]]+', 1, 1)) AS label,
        TRIM(REGEXP_SUBSTR(values, '[^[-]]+', 1, 1)) AS value,
        SUBSTR(labels, INSTR(labels, '[-]', 1, 1) + 1) AS label_part,
        SUBSTR(values, INSTR(values, '[-]', 1, 1) + 1) AS value_part,
        1 AS rn
    FROM your_table
    WHERE labels IS NOT NULL AND values IS NOT NULL

    UNION ALL

    SELECT
        TRIM(REGEXP_SUBSTR(label_part, '[^[-]]+', 1, 1)),
        TRIM(REGEXP_SUBSTR(value_part, '[^[-]]+', 1, 1)),
        SUBSTR(label_part, INSTR(label_part, '[-]', 1, 1) + 1),
        SUBSTR(value_part, INSTR(value_part, '[-]', 1, 1) + 1),
        rn + 1
    FROM LabelValueSplit
    WHERE label_part IS NOT NULL AND value_part IS NOT NULL
)
SELECT label, value
FROM LabelValueSplit
ORDER BY rn;

