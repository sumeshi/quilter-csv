# Quilter-CSV
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![PyPI version](https://badge.fury.io/py/qsv.svg)](https://badge.fury.io/py/qsv)
![PyPI - Downloads](https://img.shields.io/pypi/dm/qsv)

![quilter-csv](https://gist.githubusercontent.com/sumeshi/644af27c8960a9b6be6c7470fe4dca59/raw/00d774e6814a462eb48e68f29fc6226976238777/quilter-csv.svg)

A tool that provides elastic and rapid filtering for efficient analysis of huge CSV files, such as eventlogs.

This project is inspired by [xsv](https://github.com/BurntSushi/xsv). We are currently developing a tool that can process hundreds of gigabytes of data, which is challenging for many tools, and apply filters according to predefined configurations.

> [!NOTE]  
> This project is in the early stages of development. Please be aware that frequent changes and updates are likely to occur.

## Description
### Motivation
In digital forensics and log analysis, it’s common to deal with extremely large CSV files—sometimes tens or even hundreds of gigabytes spread across dozens or hundreds of machines.  
While many of these tasks are standardized, they often require using large, complex analysis tools with opaque specifications, or else writing intricate shell scripts that are difficult to maintain and debug.  
The core feature of this tool is the `quilt` command, which directly and reliably executes predefined command-line tasks.  
We hope this tool will serve as a solution for anyone facing similar challenges.

### Architecture
This tool processes CSV files through three stages: an initializer, one or more chainable functions, and a finalizer.
For example, you can load a csv file in the initializer, use chainable functions to filter, sort, and select columns, and then output the resulting csv file in the finalizer.

![](https://gist.githubusercontent.com/sumeshi/644af27c8960a9b6be6c7470fe4dca59/raw/2a19fafd4f4075723c731e4a8c8d21c174cf0ffb/qsv.svg)

```bash
$ qsv {{INITIALIZER}} {{Arguments}} - {{CHAINABLE}} {{Arguments}} - {{FINALIZER}} {{Arguments}}
```
Each process must be explicitly separated by a hyphen ("-").


## Usage
e.g.
Below is an example of reading a CSV file, extracting rows that contain 4624 in the 'Event ID' column, and displaying the top 3 rows sorted by the 'Date and Time' column.

```bash
$ qsv load Security.csv - isin 'Event ID' 4624 - sort 'Date and Time' - head 3
shape: (3, 5)
┌─────────────┬───────────────────────┬─────────────────────────────────┬──────────┬───────────────┐
│ Level       ┆ Date and Time         ┆ Source                          ┆ Event ID ┆ Task Category │
│ ---         ┆ ---                   ┆ ---                             ┆ ---      ┆ ---           │
│ str         ┆ str                   ┆ str                             ┆ i64      ┆ str           │
╞═════════════╪═══════════════════════╪═════════════════════════════════╪══════════╪═══════════════╡
│ Information ┆ 10/6/2016 01:00:55 PM ┆ Microsoft-Windows-Security-Aud… ┆ 4624     ┆ Logon         │
│ Information ┆ 10/6/2016 01:04:05 PM ┆ Microsoft-Windows-Security-Aud… ┆ 4624     ┆ Logon         │
│ Information ┆ 10/6/2016 01:04:10 PM ┆ Microsoft-Windows-Security-Aud… ┆ 4624     ┆ Logon         │
└─────────────┴───────────────────────┴─────────────────────────────────┴──────────┴───────────────┘
```


### Initializers
#### load
Loads the specified CSV files.

| Category | Parameter  | Data Type  | Default Value | Description                                                                                |
| -------- | ---------- | ---------- | ------------- | ------------------------------------------------------------------------------------------ |
| Argument | path       | tuple[str] |               | The character used to separate fields within the CSV file.                                 |
| Option   | separator  | str        | ","             | The character used to split values.                                                        |
| Option   | low_memory | bool       | False         | If True, enables a lower-memory processing mode, beneficial for handling very large files. |

```
$ qsv load ./Security.csv
```

```
$ qsv load ./logs/*.csv
```

### Chainable Functions
#### select
Selects only the specified columns.

| Category | Parameter | Data Type              | Default Value | Description                                   |
| -------- | --------- | ---------------------- | ------------- | --------------------------------------------- |
| Argument | colnames  | Union[str, tuple[str]] |               | Specifies the column(s) to keep. Accepts a single column name or multiple column names. |

```
$ qsv load ./Security.csv - select 'Event ID'
```

```
$ qsv load ./Security.csv - select "Date and Time-Event ID"
```

```
$ qsv load ./Security.csv - select "'Date and Time,Event ID'"
```

#### isin
Filters rows containing the specified values.

| Category | Parameter | Data Type | Default Value | Description                                                                              |
| -------- | --------- | --------- | ------------- | ---------------------------------------------------------------------------------------- |
| Argument | colname   | str       |               | The name of the column to filter.                                                        |
| Argument | values    | list[str] |               | A list of values to match. Rows that contain any of these values in the column are kept. |

```
$ qsv load ./Security.csv - isin 'Event ID' 4624,4634
```

#### contains
Filters rows where the specified column matches the given regex.

| Category | Parameter  | Data Type | Default Value | Description                                                          |
| -------- | ---------- | --------- | ------------- | -------------------------------------------------------------------- |
| Argument | colname    | str       |               | The name of the column to test against the regex pattern.            |
| Argument | pattern    | str       |               | A regular expression pattern used for matching values in the column. |
| Option   | ignorecase | bool      | False         | If True, performs case-insensitive pattern matching.                 |

```
$ qsv load ./Security.csv - contains 'Date and Time' '10/6/2016'
```

#### sed
Replaces values using the specified regex.

| Category | Parameter   | Data Type | Default Value | Description                                                            |
| -------- | ----------- | --------- | ------------- | ---------------------------------------------------------------------- |
| Argument | colname     | str       |               | The name of the column whose values will be modified.                  |
| Argument | pattern     | str       |               | A regular expression pattern identifying substrings to replace.        |
| Argument | replacement | str       |               | The text that replaces matched substrings.                             |
| Option   | ignorecase  | bool      | False         | If True, the regex matching is performed in a case-insensitive manner. |

```
$ qsv load ./Security.csv - sed 'Date and Time' '/' '-'
```

#### grep
Treats all columns as strings and filters rows where any column matches the specified regex.  
This function is similar to running a grep command while preserving the header row.

| Category | Parameter  | Data Type | Default Value | Description                                                                     |
| -------- | ---------- | --------- | ------------- | ------------------------------------------------------------------------------- |
| Argument | pattern    | str       |               | A regular expression pattern used to filter rows. Any row with a match is kept. |
| Option   | ignorecase | bool      | False         | If True, the regex match is case-insensitive.                                   |

```
$ qsv load ./Security.csv - grep 'LogonType'
```

#### head
Selects only the first N lines.

| Category | Parameter | Data Type | Default Value | Description                                   |
| -------- | --------- | --------- | ------------- | --------------------------------------------- |
| Option   | number    | int       | 5             | The number of rows to display from the start. |

```
$ qsv load ./Security.csv - head 10
```

#### tail
Selects only the last N lines.

| Category | Parameter | Data Type | Default Value | Description                                 |
| -------- | --------- | --------- | ------------- | ------------------------------------------- |
| Option   | number    | int       | 5             | The number of rows to display from the end. |

```
$ qsv load ./Security.csv - tail 10
```

#### sort
Sorts all rows by the specified column values.

| Category | Parameter | Data Type                         | Default Value | Description                                               |
| -------- | --------- | --------------------------------- | ------------- | --------------------------------------------------------- |
| Argument | colnames  | Union[str, tuple[str], list[str]] |               | One or more columns to sort by.                           |
| Option   | desc      | bool                              | False         | If True, sorts in descending order rather than ascending. |


```
$ qsv load ./Security.csv - sort 'Date and Time'
```

#### sort
Counts duplicate rows, grouping by all columns.

```
$ qsv load ./Security.csv - count
```

#### uniq
Remove duplicate rows based on the specified column names.

| Category | Parameter | Data Type                         | Default Value | Description                                                                     |
| -------- | --------- | --------------------------------- | ------------- | ------------------------------------------------------------------------------- |
| Argument | colnames  | Union[str, tuple[str], list[str]] |               | Column(s) used to determine uniqueness. Rows with duplicate values are removed. |

```
$ qsv load ./Security.csv - uniq 'Event ID'
```

#### changetz
Changes the timezone of the specified date column.

The datetime format strings follow the same conventions as [Python](https://docs.python.org/3/library/datetime.html)'s datetime module (based on the C99 standard).

| Category | Parameter | Data Type | Default Value | Description                                                                                    |
| -------- | --------- | --------- | ------------- | ---------------------------------------------------------------------------------------------- |
| Argument | colname   | str       |               | The name of the date/time column to convert.                                                   |
| Option   | tz_from   | str       | "UTC"         | The original timezone of the column's values.                                                  |
| Option   | tz_to     | str       | "UTC"         | The target timezone to convert values into.                                                    |
| Option   | dt_format | str       | AutoDetect    | The datetime format for parsing values. If not provided, the format is automatically inferred. |

```
$ qsv load ./Security.csv - changetz 'Date and Time' --timezone_from=UTC --timezone_to=Asia/Tokyo --datetime_format="%m/%d/%Y %I:%M:%S %p"
```

#### renamecol
Renames the specified column.

| Category | Parameter   | Data Type | Default Value | Description                               |
| -------- | ----------- | --------- | ------------- | ----------------------------------------- |
| Argument | colname     | str       |               | The current name of the column to rename. |
| Argument | new_colname | str       |               | The new name for the specified column.    |

```
$ qsv load ./Security.csv - renamecol 'Event ID' 'EventID'
```

### Finalizer
#### headers
Displays the column names of the data.

| Category | Parameter | Data Type | Default Value | Description                                                             |
| -------- | --------- | --------- | ------------- | ----------------------------------------------------------------------- |
| Option   | plain     | bool      | False         | If True, displays the column headers as plain text rather than a table. |

```
$ qsv load ./Security.csv - headers
┏━━━━┳━━━━━━━━━━━━━━━┓
┃ #  ┃ Column Name   ┃
┡━━━━╇━━━━━━━━━━━━━━━┩
│ 00 │ Level         │
│ 01 │ Date and Time │
│ 02 │ Source        │
│ 03 │ Event ID      │
│ 04 │ Task Category │
└────┴───────────────┘
```

#### stats
Displays the statistical information of the data.

```
$ qsv load ./Security.csv - stats
shape: (9, 6)
┌────────────┬─────────────┬───────────────────────┬─────────────────────────────────┬─────────────┬─────────────────────────┐
│ statistic  ┆ Level       ┆ Date and Time         ┆ Source                          ┆ Event ID    ┆ Task Category           │
│ ---        ┆ ---         ┆ ---                   ┆ ---                             ┆ ---         ┆ ---                     │
│ str        ┆ str         ┆ str                   ┆ str                             ┆ f64         ┆ str                     │
╞════════════╪═════════════╪═══════════════════════╪═════════════════════════════════╪═════════════╪═════════════════════════╡
│ count      ┆ 62031       ┆ 62031                 ┆ 62031                           ┆ 62031.0     ┆ 62031                   │
│ null_count ┆ 0           ┆ 0                     ┆ 0                               ┆ 0.0         ┆ 0                       │
│ mean       ┆ null        ┆ null                  ┆ null                            ┆ 5058.625897 ┆ null                    │
│ std        ┆ null        ┆ null                  ┆ null                            ┆ 199.775419  ┆ null                    │
│ min        ┆ Information ┆ 10/6/2016 01:00:35 PM ┆ Microsoft-Windows-Eventlog      ┆ 1102.0      ┆ Credential Validation   │
│ 25%        ┆ null        ┆ null                  ┆ null                            ┆ 5152.0      ┆ null                    │
│ 50%        ┆ null        ┆ null                  ┆ null                            ┆ 5156.0      ┆ null                    │
│ 75%        ┆ null        ┆ null                  ┆ null                            ┆ 5157.0      ┆ null                    │
│ max        ┆ Information ┆ 10/7/2016 12:59:59 AM ┆ Microsoft-Windows-Security-Aud… ┆ 5158.0      ┆ User Account Management │
└────────────┴─────────────┴───────────────────────┴─────────────────────────────────┴─────────────┴─────────────────────────┘
```

#### showquery
Displays the data processing query.

```
$ qsv load Security.csv - showquery
naive plan: (run LazyFrame.explain(optimized=True) to see the optimized plan)

  Csv SCAN Security.csv
  PROJECT */5 COLUMNS
```

#### show
Displays the processing results in a table format to standard output.

```
$ qsv load Security.csv - show
Level,Date and Time,Source,Event ID,Task Category
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4658,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4656,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4658,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4656,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4658,File System
```

#### showtable
Outputs the processing results table to the standard output.

```
$ qsv load Security.csv - showtable
shape: (3, 5)
┌─────────────┬───────────────────────┬─────────────────────────────────┬──────────┬───────────────┐
│ Level       ┆ Date and Time         ┆ Source                          ┆ Event ID ┆ Task Category │
│ ---         ┆ ---                   ┆ ---                             ┆ ---      ┆ ---           │
│ str         ┆ str                   ┆ str                             ┆ i64      ┆ str           │
╞═════════════╪═══════════════════════╪═════════════════════════════════╪══════════╪═══════════════╡
│ Information ┆ 10/6/2016 01:00:55 PM ┆ Microsoft-Windows-Security-Aud… ┆ 4624     ┆ Logon         │
│ Information ┆ 10/6/2016 01:04:05 PM ┆ Microsoft-Windows-Security-Aud… ┆ 4624     ┆ Logon         │
│ Information ┆ 10/6/2016 01:04:10 PM ┆ Microsoft-Windows-Security-Aud… ┆ 4624     ┆ Logon         │
└─────────────┴───────────────────────┴─────────────────────────────────┴──────────┴───────────────┘
```

#### dump
Outputs the processing results to a CSV file.

| Category | Parameter | Data Type | Default Value               | Description                                                                                                           |
| -------- | --------- | --------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Option   | path      | str       | yyyymmdd-HHMMSS_{QUERY}.csv | The file path where the filtered/output CSV data will be saved. If not specified, a timestamp-based filename is used. |

```
$ qsv load Security.csv - dump ./Security-qsv.csv
```


### Quilt
Quilt is a command-line tool that allows you to define a sequence of **Initializer**, **Chainable Functions**, and **Finalizer** processes in a YAML configuration file and execute them in a single pipeline.

#### Usage

| Category | Parameter | Data Type  | Default Value | Description                                                                                                 |
| -------- | --------- | ---------- | ------------- | ----------------------------------------------------------------------------------------------------------- |
| Argument | config    | str        |               | Path to a YAML configuration file/directory that defines initializers, chainable functions, and finalizers steps.     |
| Argument | path      | tuple[str] |               | One or more paths to CSV files to be processed according to the predefined rules in the configuration file. |

#### Command Example
```bash
$ qsv quilt rules/test.yaml ./Security.csv
```

#### Configuration Example
`rules/test.yaml`

```yaml
title: 'test'
description: 'test processes'
version: '0.1.0'
author: 'John Doe <john@example.com>'
stages:
  test_stage: # arbitrary stage name
    type: process # operation type
    steps:
      load: 
      isin:
        colname: EventId
        values:
          - 4624
      head:
        number: 5
      select:
        colnames:
          - RecordNumber
          - TimeCreated
      changetz:
        colname: TimeCreated
        tz_from: UTC
        tz_to: Asia/Tokyo
        dt_format: "%Y-%m-%d %H:%M:%S%.f"
      showtable:
```

The above configuration file defines the following sequence of operations:
1. Load a CSV file.
2. Filter rows where the `EventId` column contains the value `4624`.
3. Retrieve the first 5 rows.
4. Extract the `RecordNumber` and `TimeCreated` columns.
5. Convert the time zone of the `TimeCreated` column from `UTC` to `Asia/Tokyo`.
6. Display the processing results in a table format.

#### Pipeline Operations
| Operation Type | Description                                                | Parameters                                                                                                                                    |
| -------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| process        | Executes a series of operations on the dataset.            | `steps`: A dict of operations (e.g., `load`, `select`, `dump`) to apply.                                                                      |
| concat         | Concatenates multiple datasets vertically or horizontally. | `sources`: List of stages to concat. <br>`params.how`: `vertical`, `vertical_relaxed`, `horizontal`, `diagonal`, `align`, etc.                       |
| join           | Joins multiple datasets using keys.                        | `sources`: List of stages to join.<br>`params.key`: Column(s) used for joining.<br>`params.how`: `inner`, `left`, `right`, `full`, `semi`, `anti`, `cross`.<br>`params.coalesce`: bool |

#### Sample YAML (`rules/test.yaml`):
```yaml
title: 'test'
description: 'test pipelines'
version: '0.1.0'
author: 'John Doe <john@example.com>'
stages:
  load_stage:
    type: process
    steps:
      load:

  stage_1:
    type: process
    source: load_stage
    steps:
      select:
        colnames: 
          - TimeCreated
          - PayloadData1

  stage_2:
    type: process
    source: load_stage
    steps:
      select:
        colnames: 
          - TimeCreated
          - PayloadData2

  merge_stage:
    type: join
    sources:
      - stage_1
      - stage_2
    params:
      how: full
      key: TimeCreated
      coalesce: True
  
  stage_3:
    type: process
    source: merge_stage
    steps:
      showtable:
```

#### Note: Step Duplication
Quilt supports YAML configurations with duplicate keys in steps.

```yaml
stages:
test_stage:
  steps:
    load:
    renamecol: # duplicate key
      from: old_col1
      to: new_col1
    renamecol: # duplicate key
      from: old_col2
      to: new_col2
    renamecol: # duplicate key
      from: old_col3
      to: new_col3
    show:
```

Internally, these keys are handled as:

```yaml
renamecol
renamecol_
renamecol__
```

This ensures that each steps is treated as a distinct operation in the pipeline.


## Installation
### from PyPI
```
$ pip install qsv
```

### from GitHub Releases
A Nuitka-compiled binary version is also [available](https://github.com/sumeshi/quilter-csv/releases).

#### Ubuntu
```
$ chmod +x ./qsv
$ ./qsv {{options...}}
```

#### Windows
```
> qsv.exe {{options...}}
```

## License
Quilter-CSV is released under the [MIT](https://github.com/sumeshi/quilter-csv/blob/master/LICENSE) License.
