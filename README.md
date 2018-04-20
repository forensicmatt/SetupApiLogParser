# SetupApiLogParser
Parse Setup API Logs

## Usage
```
usage: SetupApiLogParser.py [-h] -s SOURCE [--debug {ERROR,WARN,INFO,DEBUG}]

Parse Setup API log files to JSONL.

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        Source file.
  --debug {ERROR,WARN,INFO,DEBUG}
                        Debug level [default=ERROR]
```

## Output
Output is in JSONL format.

Example record (formatted):
```json
{
  "boot_session": "2013-09-23 16:07:48.498",
  "section_title": "SetupCopyOEMInf",
  "instance_identifier": "C:\\WINDOWS\\System32\\DriverStore\\FileRepository\\usbaapl64.inf_amd64_ca639d07023cb608\\usbaapl64.inf",
  "section_start": "2013-09-26 13:52:51.343",
  "body": [{
      "message_level": "info",
      "event_category": "cmd",
      "indent_level": 0,
      "content": "C:\\Windows\\System32\\MsiExec.exe -Embedding 27EDA8EA7D1C805F3C5546CF52884F47 M Global\\MSI0000"
    }, {
      "message_level": "info",
      "event_category": "inf",
      "indent_level": 0,
      "content": "Driver Store Path: C:\\WINDOWS\\System32\\DriverStore\\FileRepository\\usbaapl64.inf_amd64_ca639d07023cb608\\usbaapl64.inf"
    }, {
      "message_level": "info",
      "event_category": "inf",
      "indent_level": 0,
      "content": "Published Inf Path: C:\\WINDOWS\\INF\\oem54.inf"
    }
  ],
  "section_end": "2013-09-26 13:52:51.346",
  "exit_status": "SUCCESS"
}
```
