CREATE OR REPLACE PACKAGE YOUR_SCHEMA.MDX_ETL_DEMO IS

    -- This is a sample Oracle package for MDX ETL, please see https://github.com/DataBooster/PyWebApi#mdx-etl for details.

    TYPE DATE_ARRAY IS TABLE OF DATE INDEX BY SIMPLE_INTEGER;

    EMPTY_DATE_ARRAY   DATE_ARRAY;
    EMPTY_STRING_ARRAY DBMS_UTILITY.LNAME_ARRAY;
    EMPTY_NUMBER_ARRAY DBMS_UTILITY.NUMBER_ARRAY;

----------------------------------------------------------------------------------------------------------------------------------------------------------------

    -- This is the entry procedure of a MDX ETL. The characteristic that distinguishes it from an ordinary procedure is that:
    -- it has an MDX_QUERY column and a corresponding CALLBACK_SP column in at least one output result set (OUT SYS_REFCURSOR).
    PROCEDURE GET_MDX_TASKS
    (
        -- Input Parameters are only used internally by the procedure. There are no regulations. For example,
        inParam1 DATE,
        inParam2 VARCHAR2,
        inParam3 SIMPLE_INTEGER := 0,

        -- The essential characteristic of MDX ETL is reflected in the output result set, all of other parameters are optional.
        RC1 OUT SYS_REFCURSOR,   -- The result set should contain the following 4 columns:
                -- MDX_QUERY: (required) A string (VARCHAR2/NVARCHAR2 or CLOB/NCLOB) of valid MDX query;
                -- COLUMN_MAPPING: (optional) This is a string of JSON dictionary for specifying the mapping from the column name of the MDX result to the input parameter name of the corresponding CALLBACK_SP, if they are different;
                -- CALLBACK_SP: (required) The fully qualified name of the procedure for processing the MDX query results;
                -- CALLBACK_ARGS: (required) A string of JSON dictionary that contains the input parameters to be passed to the CALLBACK_SP procedure. 
                --                           All results of this MDX and the above pipeline parameters will be merged into the input parameters of this CALLBACK_SP.
                -- Every MDX_QUERY->CALLBACK_SP ​​task flows in the same result set will be executed in parallel.
                -- The names of Above 4 colums are a convention with the end client, and can also be specified by options. Any extra columns other than these 4 columns will be ignored.

        -- If multiple result sets satisfy the above characteristics, every task group of the results set will be launched in series.
        -- If the procedure does not have any result set, or no result record satisfies the above characteristic,
        --     the MDX ETL engine treats the procedure as an ordinary procedure and just returns the result of the procedure to the end client without launching any MDX task flow.

        -- The following two output parameters indicate the post-processing procedure that will be called after all MDX subtasks are completed.
        -- The parameter names are a convention with the end client, and can also be specified by options.
        OUT_POST_SP      OUT VARCHAR2,  -- The output value should be the fully qualified name of the post-processing procedure, even if it is in the same package.
                                        -- You can also append any URL query string supported by dbwebapi to it, such as '?NamingCase=None'
                                        -- If the post-processing procedure is pointed to another MDX ETL entry (or even recursively pointed to itself), 
                                        -- that process will be chained to the current process, so on and so forth.
        OUT_POST_SP_ARGS OUT VARCHAR2,  -- The output value must be a string of JSON dictionary that contains the input parameters to be passed to the post-processing procedure.

        -- All the remaining output parameters will be pipelined into the input parameters of every MDX task procedures and the post-processing procedure if their parameter names match.
        BATCH_ID         OUT PLS_INTEGER
    );

----------------------------------------------------------------------------------------------------------------------------------------------------------------
    -- Please go to the PACKAGE BODY to facilitate the interpretation in the following parts.
----------------------------------------------------------------------------------------------------------------------------------------------------------------

    PROCEDURE PROCESS_MDX_RESULT_1              -- Referenced from above GET_MDX_TASKS's 1st CALLBACK_SP: 'YOUR_SCHEMA.MDX_ETL_DEMO.PROCESS_MDX_RESULT_1'
    (
        BATCH_ID    SIMPLE_INTEGER,             -- From the output parameter BATCH_ID of GET_MDX_TASKS above
        inTerritory VARCHAR2,                   -- From above GET_MDX_TASKS's 1st CALLBACK_ARGS: '{"inTerritory": "Southwest"}'

        -- All parameters received from the MDX result must be some kind of array (PL/SQL Associative Array Parameters)
        inYears     DBMS_UTILITY.NUMBER_ARRAY,  -- From the "Fiscal Year" column of MDX result - COLUMN_MAPPING: "Fiscal Year"=>"inYears"
        inSales     DBMS_UTILITY.NUMBER_ARRAY,  -- From the "Sales Amount" column of MDX result - COLUMN_MAPPING: "Sales Amount"=>"inSales"
        inTaxes     DBMS_UTILITY.NUMBER_ARRAY   -- From the "Tax Amount" column of MDX result - COLUMN_MAPPING: "Tax Amount"=>"inTaxes"
    );

    PROCEDURE PROCESS_MDX_RESULT_2                  -- Referenced from above GET_MDX_TASKS's 2nd CALLBACK_SP: 'YOUR_SCHEMA.MDX_ETL_DEMO.PROCESS_MDX_RESULT_2'
    (
        BATCH_ID       SIMPLE_INTEGER,              -- From the output parameter BATCH_ID of GET_MDX_TASKS above

        -- All parameters received from the MDX result must be some kind of array (PL/SQL Associative Array Parameters)
        CALENDAR       DBMS_UTILITY.LNAME_ARRAY,    -- From the "Calendar" column of MDX result
        INTERNET_SALES DBMS_UTILITY.NUMBER_ARRAY    -- From the "Internet Sales Amount" column of MDX result - COLUMN_MAPPING: "Internet Sales Amount"=>"INTERNET_SALES"
    );

    PROCEDURE FINAL_POST_PROCESSING     -- Referenced from above GET_MDX_TASKS's OUT_POST_SP: 'YOUR_SCHEMA.MDX_ETL_DEMO.FINAL_POST_PROCESSING'
    (
        BATCH_ID  SIMPLE_INTEGER,       -- From the output parameter BATCH_ID of GET_MDX_TASKS above
        inComment VARCHAR2              -- From GET_MDX_TASKS's output parameter OUT_POST_SP_ARGS: '{"inComment": "This is an example of argument passed from the bootloader"}'
    );

END MDX_ETL_DEMO;
/
CREATE OR REPLACE PACKAGE BODY YOUR_SCHEMA.MDX_ETL_DEMO IS

----------------------------------------------------------------------------------------------------------------------------------------------------------------

    PROCEDURE GET_MDX_TASKS
    (
        inParam1 DATE,
        inParam2 VARCHAR2,
        inParam3 SIMPLE_INTEGER := 0,

        RC1 OUT SYS_REFCURSOR,

        OUT_POST_SP      OUT VARCHAR2,
        OUT_POST_SP_ARGS OUT VARCHAR2,
        BATCH_ID         OUT PLS_INTEGER
    ) IS
    BEGIN

        OUT_POST_SP      := 'YOUR_SCHEMA.MDX_ETL_DEMO.FINAL_POST_PROCESSING';                               -- Fully qualified name
        OUT_POST_SP_ARGS := '{"inComment": "This is an example of argument passed from the bootloader"}';   -- JSON dictionary

        IF inParam3 > 0 THEN
            BATCH_ID := inParam3;
            YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Enter GET_MDX_TASKS');
        ELSE
            BATCH_ID := YOUR_SCHEMA.UTIL_LOG.CREATE_BATCH('MDX_ETL_DEMO');
            YOUR_SCHEMA.UTIL_LOG.PROGRESS_START(BATCH_ID, 100, 'Start GET_MDX_TASKS');
        END IF;

        OPEN RC1 FOR
            SELECT 'SELECT
	{ [Measures].[Sales Amount], [Measures].[Tax Amount] } ON 0,
	{ [Date].[Fiscal].[Fiscal Year].&[2002], [Date].[Fiscal].[Fiscal Year].&[2003] } ON 1
FROM [Adventure Works]
WHERE ( [Sales Territory].[Southwest] )'                                                            AS MDX_QUERY,
                   '{"Sales Amount": "inSales", "Tax Amount": "inTaxes", "Fiscal Year": "inYears"}' AS COLUMN_MAPPING,
                   'YOUR_SCHEMA.MDX_ETL_DEMO.PROCESS_MDX_RESULT_1'                                  AS CALLBACK_SP,
                   '{"inTerritory": "Southwest"}'                                                   AS CALLBACK_ARGS
            FROM   DUAL
            UNION  ALL
            SELECT 'SELECT
	{[Measures].[Internet Sales Amount]} ON COLUMNS,
	NON EMPTY {[Date].[Calendar].MEMBERS} ON ROWS
FROM [Adventure Works]'                                                                             AS MDX_QUERY,
                   '{"Internet Sales Amount": "INTERNET_SALES"}'                                    AS COLUMN_MAPPING,
                   'YOUR_SCHEMA.MDX_ETL_DEMO.PROCESS_MDX_RESULT_2'                                  AS CALLBACK_SP,
                   '{}'                                                                             AS CALLBACK_ARGS
            FROM   DUAL;

        YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Exit GET_MDX_TASKS');
    END GET_MDX_TASKS;

----------------------------------------------------------------------------------------------------------------------------------------------------------------

    PROCEDURE PROCESS_MDX_RESULT_1              -- Referenced from above GET_MDX_TASKS's 1st CALLBACK_SP: 'YOUR_SCHEMA.MDX_ETL_DEMO.PROCESS_MDX_RESULT_1'
    (
        BATCH_ID    SIMPLE_INTEGER,             -- From the output parameter BATCH_ID of GET_MDX_TASKS above
        inTerritory VARCHAR2,                   -- From above GET_MDX_TASKS's 1st CALLBACK_ARGS: '{"inTerritory": "Southwest"}'

        -- All parameters received from the MDX result must be some kind of array (PL/SQL Associative Array Parameters)
        inYears     DBMS_UTILITY.NUMBER_ARRAY,  -- From the "Fiscal Year" column of MDX result - COLUMN_MAPPING: "Fiscal Year"=>"inYears"
        inSales     DBMS_UTILITY.NUMBER_ARRAY,  -- From the "Sales Amount" column of MDX result - COLUMN_MAPPING: "Sales Amount"=>"inSales"
        inTaxes     DBMS_UTILITY.NUMBER_ARRAY   -- From the "Tax Amount" column of MDX result - COLUMN_MAPPING: "Tax Amount"=>"inTaxes"
    ) IS
    BEGIN
        YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Enter PROCESS_MDX_RESULT_1 - ' || inTerritory || ' : ' || TO_CHAR(inVegas.COUNT));

        FORALL i IN inSales.FIRST .. inSales.LAST
            INSERT INTO YOUR_SCHEMA.TEMP_TABLE_1
                (BATCH_ID, TERRITORY, FISCAL_YEAR, SALES_AMOUNT, TAX_AMOUNT)
            VALUES
                (BATCH_ID, inTerritory, inYears(i), inSales(i), inTaxes(i));

        YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Exit PROCESS_MDX_RESULT_1');
    END PROCESS_MDX_RESULT_1;

    PROCEDURE PROCESS_MDX_RESULT_2                  -- Referenced from above GET_MDX_TASKS's 2nd CALLBACK_SP: 'YOUR_SCHEMA.MDX_ETL_DEMO.PROCESS_MDX_RESULT_2'
    (
        BATCH_ID       SIMPLE_INTEGER,              -- From the output parameter BATCH_ID of GET_MDX_TASKS above

        -- All parameters received from the MDX result must be some kind of array (PL/SQL Associative Array Parameters)
        CALENDAR       DBMS_UTILITY.LNAME_ARRAY,    -- From the "Calendar" column of MDX result
        INTERNET_SALES DBMS_UTILITY.NUMBER_ARRAY    -- From the "Internet Sales Amount" column of MDX result - COLUMN_MAPPING: "Internet Sales Amount"=>"INTERNET_SALES"
    ) IS
    BEGIN
        YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Enter PROCESS_MDX_RESULT_2 ' || TO_CHAR(INTERNET_SALES.COUNT));

        FORALL i IN INTERNET_SALES.FIRST .. INTERNET_SALES.LAST
            INSERT INTO YOUR_SCHEMA.TEMP_TABLE_2 (BATCH_ID, CALENDAR, INTERNET_SALES) VALUES (BATCH_ID, CALENDAR(i), INTERNET_SALES(i));

        YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Exit PROCESS_MDX_RESULT_2');
    END PROCESS_MDX_RESULT_2;


    PROCEDURE FINAL_POST_PROCESSING     -- Referenced from above GET_MDX_TASKS's OUT_POST_SP: 'YOUR_SCHEMA.MDX_ETL_DEMO.FINAL_POST_PROCESSING'
    (
        BATCH_ID  SIMPLE_INTEGER,       -- From the output parameter BATCH_ID of GET_MDX_TASKS above
        inComment VARCHAR2              -- From GET_MDX_TASKS's output parameter OUT_POST_SP_ARGS: '{"inComment": "This is an example of argument passed from the bootloader"}'
    ) IS
    BEGIN
        YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Enter FINAL_POST_PROCESSING: ' || inComment);

        YOUR_SCHEMA.UTIL_LOG.PROGRESS_UPDATE(BATCH_ID, 'Enter FINAL_POST_PROCESSING');
    END FINAL_POST_PROCESSING;

END MDX_ETL_DEMO;
/
