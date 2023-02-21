# WorkDiary

A commandline tool made with python used to create logs in a `SQLite3` database and export those logs in csv format.

## Installation

It only has simple functionality created using built-in python libraries.

## Usage

- For help using this tool
```
python3 log.py -h
```
- To create a log entry
```
python3 log.py
```
or alternatively you can use
```
python3 log.py log
```
- To export all entries to `.csv`
```
python3 log.py export-all
```
- To export entries related to a specific date to `.csv`
```
python3 log.py export-date -d dd-mm-yyyy
```
or alternatively you can use
```
python3 log.py export-date -date dd-mm-yyyy
```
replace the dd-mm-yyyy with your own specific date

- To get visualizations of your records in csv file
```
python3 visualize.py
```

## Note

This is still a prototype and I'm planning to include more functionality like GUI