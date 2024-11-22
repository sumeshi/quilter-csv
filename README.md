# Quilter-CSV
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![PyPI version](https://badge.fury.io/py/qsv.svg)](https://badge.fury.io/py/qsv)

![quilter-csv](https://gist.githubusercontent.com/sumeshi/644af27c8960a9b6be6c7470fe4dca59/raw/4115bc2ccf9ab5fb40a455c34ac0be885b7f263d/quilter-csv.svg)

A tool that provides elastic and rapid filtering for efficient analysis of huge CSV files, such as eventlogs.

This project is inspired by [xsv](https://github.com/BurntSushi/xsv). We are currently developing a tool that can process hundreds of gigabytes of data, which is challenging for many tools, and apply filters according to predefined configurations.

> [!NOTE]  
> This project is in the early stages of development. Please be aware that frequent changes and updates are likely to occur.

## Description
### Motivation
In digital forensics and log analysis, we often have to examine extremely large CSV files, sometimes amounting to tens or hundreds of gigabytes across dozens or even hundreds of machines.  
Most of these tasks are standardized processes, but accomplishing them usually requires using analysis tools so large and complex that understanding their specifications or definitions is nearly impossible, or writing intricate shell scripts that are difficult to debug.  
The core feature of this tool is the Quilt command, which simply and faithfully executes tasks that can be performed via the CLI.  
We hope this tool will serve as a solution for anyone facing similar challenges.

### Architecture
This tool processes CSV (comma-separated values) files by connecting three processes: initializer, chainable functions, and finalizer.  
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
```
Arguments:
  *path: tuple[str]

Options:
  separator: str = ','
  low_memory: bool = False
```

examples
```
$ qsv load ./Security.csv
```

```
$ qsv load ./logs/*.csv
```

### Chainable Functions
#### select
Selects only the specified columns.

```
Arguments:
  colnames: Union[str, tuple[str]]
```

examples
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

```
Arguments:
  colname: str
  values: list
```

examples
```
$ qsv load ./Security.csv - isin 'Event ID' 4624,4634
```

#### contains
Filters rows where the specified column matches the given regex.

```
Arguments:
  colname: str
  regex: str
  ignorecase: bool = False
```

examples
```
$ qsv load ./Security.csv - contains 'Date and Time' '10/6/2016'
```

#### sed
Replaces values using the specified regex.

```
Arguments:
  colname: str
  regex: str
  replaced_text: str
  ignorecase: bool = False
```

examples
```
$ qsv load ./Security.csv - sed 'Date and Time' '/' '-'
```

#### grep
Treats all columns as strings and filters rows where any column matches the specified regex.  
This function is similar to running a grep command while preserving the header row.

```
Arguments:
  regex: str
  ignorecase: bool = False
```

examples
```
$ qsv load ./Security.csv - grep 'LogonType'
```

#### head
Selects only the first N lines.

```
Options:
  number: int = 5
```

examples
```
$ qsv load ./Security.csv - head 10
```

#### tail
Selects only the last N lines.

```
Options:
  number: int = 5
```

examples
```
$ qsv load ./Security.csv - tail 10
```

#### sort
Sorts all rows by the specified column values.

```
Arguments:
  colnames: Union[str, tuple[str], list[str]]

Options:
  desc: bool = False
```

examples
```
$ qsv load ./Security.csv - sort 'Date and Time'
```

#### uniq
Remove duplicate rows based on the specified column names.

```
Arguments:
  colnames: Union[str, tuple[str], list[str]]
```

examples
```
$ qsv load ./Security.csv - uniq 'Event ID'
```

#### changetz
Changes the timezone of the specified date column.

The datetime format strings follow the same conventions as [Python](https://docs.python.org/3/library/datetime.html)'s datetime module (based on the C99 standard).

```
Arguments:
  colname: str

Options:
  timezone_from: str = "UTC"
  timezone_to: str = "Asia/Tokyo"
  datetime_format: str = None
```

examples
```
$ qsv load ./Security.csv - changetz 'Date and Time' --timezone_from=UTC --timezone_to=Asia/Tokyo --datetime_format="%m/%d/%Y %I:%M:%S %p"
```

#### renamecol
Renames the specified column.

```
Arguments:
  colname: str
  new_colname: str
```

examples
```
$ qsv load ./Security.csv - renamecol 'Event ID' 'EventID'
```

### Finalizer
#### headers
Displays the column names of the data.

```
Options:
  plain: bool = False
```

examples
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

examples
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

examples
```
qsv load Security.csv - showquery
naive plan: (run LazyFrame.explain(optimized=True) to see the optimized plan)

  Csv SCAN Security.csv
  PROJECT */5 COLUMNS
```

#### show
Displays the processing results in a table format to standard output.

examples
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

examples
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

```
Options:
  path: str = yyyymmdd-HHMMSS_{QUERY}.csv
```

examples
```
$ qsv load Security.csv - dump ./Security-qsv.csv
```


### Quilt
Quilt is a command that allows you to predefine a series of Initializer, Chainable Functions, and Finalizer processes in a YAML configuration file, and then execute them all at once.

e.g
```
$ qsv quilt rules ./Security.csv
```

```
Arguments:
  config: str
  *path: tuple[str]
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

## Planned Features:
- CSV cache (.pkl, duckdb, etc.)
- Filtering based on specific conditions (OR, AND conditions)
- Grouping for operations like count
- Joining with other tables

## Installation
### from PyPI
```
$ pip install qsv
```

### from GitHub Releases
A version a Nuitka-compiled binary version is also [available](https://github.com/sumeshi/quilter-csv/releases).

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
