# snip-snap-csv
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![PyPI version](https://badge.fury.io/py/sscsv.svg)](https://badge.fury.io/py/sscsv)
[![Python Versions](https://img.shields.io/pypi/pyversions/sscsv.svg)](https://pypi.org/project/sscsv/)

A tool designed for rapid CSV file processing and filtering, specifically designed for log analysis.

## Description


> [!NOTE]  
> This project is in the early stages of development. Please be aware that frequent changes and updates are likely to occur.


## Usage
```bash
$ sscsv {{initializer}} {{Arguments}} - {{chainable}} {{Arguments}} - {{chainable}} {{Arguments}} - {{finalizer}} {{Arguments}}
```

e.g.
Below is an example of reading a CSV file, extracting rows that contain 4624 in the EventID column, and displaying the top 3 rows them sorted by the Timestamp column.
```bash
$ sscsv load Security.csv - isin 'Event ID' 4624 - sort 'Date and Time' - head 3
2024-06-26T17:29:19+0000 [DEBUG] 1 files are loaded. Security.csv
2024-06-26T17:29:19+0000 [DEBUG] filter condition: 4624 in Event ID
2024-06-26T17:29:19+0000 [DEBUG] sort by Date and Time (asc).
2024-06-26T17:29:19+0000 [DEBUG] heading 3 lines.
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


## Archtecture
This tool processes csv by connecting three processes: initializer, chainable, and finalizer.  
For example, the initializer reads in the file, goes through multiple chainable processing steps, and then outputs the file using the finalizer.  

Also, each process is explicitly separated from the others by "-".

![](https://gist.githubusercontent.com/sumeshi/644af27c8960a9b6be6c7470fe4dca59/raw/74764568e282ad173a9a51659c65c9f0a029ae38/sscsv.svg)

### initializer
#### load
Loads the specified CSV files.

```
Arguments:
  path*: str
```

examples

```
$ sscsv load ./Security.evtx
```

```
$ sscsv load ./logs/*.evtx
```

### chainable manipulation
#### select
Displays the specified columns.

```
Arguments:
  columns: Union[str, tuple[str]]
```

examples

```
$ sscsv load ./Security.evtx - select 'Event ID'
```

```
$ sscsv load ./Security.evtx - select "Date and Time-Event ID"
```

```
$ sscsv load ./Security.evtx - select "'Date and Time,Event ID'"
```

#### isin

Displays rows that contain the specified values.

```
Arguments:
  colname: str
  values: list
```

examples

```
$ sscsv load ./Security.evtx - isin 'Event ID' 4624,4634
```

#### contains

Displays rows that contain the specified string.

```
Arguments:
  colname: str
  regex: str
```

examples

```
$ sscsv load ./Security.evtx - contains 'Date and Time' '10/6/2016'
```

#### head

Displays the first specified number of rows of the data.

```
Options:
  number: int = 5
```

examples

```
$ sscsv load ./Security.evtx - head 10
```

#### tail

Displays the last specified number of rows of the data.

```
Options:
  number: int = 5
```

examples

```
$ sscsv load ./Security.evtx - tail 10
```

#### sort

Sorts the data by the values of the specified column.

```
Arguments:
  columns: str

Options:
  desc: bool = False
```

examples

```
$ sscsv load ./Security.evtx - sort 'Date and Time'
```

#### changetz

Changes the timezone of the specified date column.

```
Arguments:
  columns: str

Options:
  timezone_from: str = "UTC"
  timezone_to: str = "Asia/Tokyo"
  new_colname: str = None
```

examples

```
$ sscsv load ./Security.evtx - changetz 'Date and Time' --timezone_from=UTC --timezone_to=Asia/Tokyo --new_colname='Date and Time(JST)'
```

### finalizer
#### headers

Displays the column names of the data.

```
Options:
  plain: bool = False
```

examples

```
$ sscsv load ./Security.evtx - headers
2024-06-30T13:17:53+0000 [DEBUG] 1 files are loaded. Security.csv
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
$ sscsv load ./Security.evtx - stats
2024-06-30T13:25:53+0000 [DEBUG] 1 files are loaded. Security.csv
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
sscsv load Security.csv - showquery
2024-06-30T13:26:54+0000 [DEBUG] 1 files are loaded. Security.csv
naive plan: (run LazyFrame.explain(optimized=True) to see the optimized plan)

  Csv SCAN Security.csv
  PROJECT */5 COLUMNS
```

#### show
Outputs the processing results to the standard output.

examples

```
$ sscsv load Security.csv - show
2024-06-30T13:27:34+0000 [DEBUG] 1 files are loaded. Security.csv
2024-06-30T13:27:34+0000 [DEBUG] heading 5 lines.
Level,Date and Time,Source,Event ID,Task Category
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4658,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4656,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4658,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4656,File System
Information,10/7/2016 06:38:24 PM,Microsoft-Windows-Security-Auditing,4658,File System
```

#### dump
Outputs the processing results to a CSV file.

```
Options:
  path: str = yyyymmdd-HHMMSS_{QUERY}.csv
```

examples

```
$ sscsv load Security.csv - dump ./Security-sscsv.csv
```

## Planned Features:
- CSV cache (.pkl)
- Filtering based on specific conditions (OR, AND conditions)
- Grouping for operations like count
- Joining with other tables
- Config Batch
- Export Config

## Installation
### from PyPI
```
$ pip install sscsv
```

### from GitHub Releases
The version compiled into a binary using Nuitka is also available for use.

#### Ubuntu
```
$ chmod +x ./sscsv
$ ./sscsv {{options...}}
```

#### Windows
```
> sscsv.exe {{options...}}
```

## License
snip-snap-csv is released under the [MIT](https://github.com/sumeshi/snip-snap-csv/blob/master/LICENSE) License.
