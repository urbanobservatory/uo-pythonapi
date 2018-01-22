# uoapi-python
A python3 module for accessing and querying the Urban Observatory REST API


## Usage

```
    import uoapi            # Import it
    urbs = uoapi.UrbanAPI() # Construct it

    # Get timeseries data from single entity (using datetime objects):
    res = self.get_timeseries("bd0cc46d-ba2e-4924-a66e-b032d7ca33a5",
                              start_time=datetime.datetime(2018, 1, 20, 0),
                              end_time=datetime.datetime(2018, 1, 20, 1))
```

## Testing
A full set of tests is included under UrbanAPI.test(), and will be run if you run the module as a script:
```
    $ python3 uoapi.py
```