# Quilter-CSV
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![PyPI version](https://badge.fury.io/py/qsv.svg)](https://badge.fury.io/py/qsv)
[![Python Versions](https://img.shields.io/pypi/pyversions/qsv.svg)](https://pypi.org/project/qsv/)

A tool provides elastic and rapid filtering for efficient analysis of huge CSV files like eventlogs.

This project is inspired by [xsv](https://github.com/BurntSushi/xsv). We are currently developing a tool that can process hundreds of GB of data, which is difficult for many tools, and apply filters according to pre-defined configurations.

> [!NOTE]  
> This project is in the early stages of development. Please be aware that frequent changes and updates are likely to occur.

## Description
### Archtecture
This tool processes csv(comma-separated values) file by connecting three processes: initializer, chainable functions, and finalizer.  
For example, you can load a csv file in the initializer, use a chainable functions to filter, sort, and select columns, and then output the resulting csv file in the finalizer.

![](https://gist.github.com/sumeshi/644af27c8960a9b6be6c7470fe4dca59/raw/2a19fafd4f4075723c731e4a8c8d21c174cf0ffb/qsv.svg)

```bash
$ qsv {{INITIALIZER}} {{Arguments}} - {{CHAINABLE}} {{Arguments}} - {{FINALIZER}} {{Arguments}}
```
Each process must be explicitly separated by a “-”.


## Usage
e.g.
Below is an example of reading a CSV file, extracting rows that contain 4624 in the EventID column, and displaying the top 3 rows them sorted by the Timestamp column.

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
  path*: str
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
Filter only on the specified columns.

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
Filter rows containing the specified values.

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
Filter rows containing the specified regex.

```
Arguments:
  colname: str
  regex: str
```

examples
```
$ qsv load ./Security.csv - contains 'Date and Time' '10/6/2016'
```

#### head
Filters only the specified number of lines from the first line.

```
Options:
  number: int = 5
```

examples
```
$ qsv load ./Security.csv - head 10
```

#### tail
Filters only the specified number of lines from the last line.

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
  colnames: Union[str, tuple[str]]

Options:
  desc: bool = False
```

examples
```
$ qsv load ./Security.csv - sort 'Date and Time'
```

#### uniq
Remove duplicated rows by the specified column names.

```
Arguments:
  colnames: Union[str, list[str]]
```

examples
```
$ qsv load ./Security.csv - uniq 'Event ID'
```

#### changetz
Changes the timezone of the specified date column.

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
$ qsv load ./Security.csv - changetz 'Date and Time' --timezone_from=UTC --timezone_to=Asia/Tokyo --new_colname='Date and Time(JST)'
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
Outputs the processing results to the standard output.

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
Quilt is a command that pre-defines a series of the above Initializer - Chainable Functions - Finalizer processes in a yaml rule and executes them all at once.

e.g
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
The version compiled into a binary using Nuitka is also available for use.

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
Quilter-csv is released under the [MIT](https://github.com/sumeshi/quilter-csv/blob/master/LICENSE) License.
