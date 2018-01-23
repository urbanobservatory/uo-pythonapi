# Urban Observatory Python3 API Module
A python3 module for accessing and querying the Urban Observatory REST API

## Installation
The best way to use this repo is probably to check it out as a submodule: 

  `git submodule add https://github.com/urbanobservatory/uo-pythonapi uoapi`
  
 Then, install the pip requirements (into your virtualenv, probably):
 
 `pip install -r requirements.txt`
 
## Usage
```python3
from uoapi.uoapi import UrbanAPI  # Import it
urb = UrbanAPI()                  # Construct it

# Get timeseries data from single entity (using datetime objects):
res = urb.get_timeseries("bd0cc46d-ba2e-4924-a66e-b032d7ca33a5",
                         start_time=datetime.datetime(2018, 1, 20, 0),
                         end_time=datetime.datetime(2018, 1, 20, 1))
```

## Testing
A full set of tests is included under UrbanAPI.test(), and will be run if you run the module as a script:
```bash
$ python3 uoapi.py
```
