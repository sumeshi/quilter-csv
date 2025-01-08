# Quilter-CSV
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![PyPI version](https://badge.fury.io/py/qsv.svg)](https://badge.fury.io/py/qsv)
![PyPI - Downloads](https://img.shields.io/pypi/dm/qsv)

![quilter-csv](https://gist.githubusercontent.com/sumeshi/644af27c8960a9b6be6c7470fe4dca59/raw/4115bc2ccf9ab5fb40a455c34ac0be885b7f263d/quilter-csv.svg)

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
| Argument | ignorecase | bool      | False         | If True, performs case-insensitive pattern matching.                 |

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
| Argument | ignorecase  | bool      | False         | If True, the regex matching is performed in a case-insensitive manner. |

```
$ qsv load ./Security.csv - sed 'Date and Time' '/' '-'
```

#### grep
Treats all columns as strings and filters rows where any column matches the specified regex.  
This function is similar to running a grep command while preserving the header row.

| Category | Parameter  | Data Type | Default Value | Description                                                                     |
| -------- | ---------- | --------- | ------------- | ------------------------------------------------------------------------------- |
| Argument | pattern    | str       |               | A regular expression pattern used to filter rows. Any row with a match is kept. |
| Argument | ignorecase | bool      | False         | If True, the regex match is case-insensitive.                                   |

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

| Category | Parameter       | Data Type | Default Value | Description                                                                                    |
| -------- | --------------- | --------- | ------------- | ---------------------------------------------------------------------------------------------- |
| Argument | colname         | str       |               | The name of the date/time column to convert.                                                   |
| Option   | timezone_from   | str       | "UTC"         | The original timezone of the column's values.                                                  |
| Option   | timezone_to     | str       | "UTC"  | The target timezone to convert values into.                                                    |
| Option   | datetime_format | str       | AutoDetect    | The datetime format for parsing values. If not provided, the format is automatically inferred. |

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
Quilt is a command that allows you to predefine a series of Initializer, Chainable Functions, and Finalizer processes in a YAML configuration file, and then execute them all at once.

| Category | Parameter | Data Type  | Default Value | Description                                                                                                     |
| -------- | --------- | ---------- | ------------- | --------------------------------------------------------------------------------------------------------------- |
| Argument | config    | str        |               | The path to a YAML configuration file defining a set of initialization, transformation, and finalization steps. |
| Argument | path      | tuple[str] |               | One or more paths to CSV files to be processed according to the predefined rules in the configuration file.     |
| Option   | debug     | bool       | False         | Enabling this option will output each rule and its intermediate processing results to the standard output.      |

```
$ qsv quilt rules ./Security.csv
```

rules/test.yaml
```yaml
title: test
description: test filter
version: 0.1.0
author: John Doe <john@example.com>
rules:
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
    timezone_from: UTC
    timezone_to: Asia/Tokyo
    datetime_format: "%Y-%m-%d %H:%M:%S%.f"
  showtable:
```

Note: While the standard YAML specification does not permit duplicate key names, Quilt rules allow for duplicate keys under the rules section. Specifically, even when multiple renamecol entries are listed, they are internally replaced and processed as renamecol, renamecol_, renamecol__, and so on. This approach enables each entry to be recognized and handled as distinct rules.

## Planned Features:
- CSV cache (.pkl, duckdb, etc.)
- Logical condition-based filtering (e.g., OR, AND) for more complex queries.
- Grouping for operations like count
- Support for joining data with other tables.

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
