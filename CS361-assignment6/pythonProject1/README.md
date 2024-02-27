# Webscraper Microservice

This file serves as documentation for the webscraper microservice that was implemented to the website to search for URL's to recipes given the users input

## How it works

First, the file `api.key` was added to put your api key to serpapi (a search engine api) which is important to the functionality of the service. All code provided throughout this document will be from the `mservice.py` file in the `Website/` directory.

### Errors

If a key is not provided or whatever is in the file is not 64 characters long a custom exception will be raised telling you the error.
```python
class NoAPIKeyError(Exception):
    """
    Exception raised for search engine api key errors.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message = "No API key or incorrect API key in api.key file"):
        self.message = message
        super().__init__(self.message)
```
When it comes to validating that a key is valid, the call to the search engine API will handle that.

### MServer

The `MServer` class is there to create a HTTP server that the website will call upon for the link retrieval functionality. For handling the POST requests that the server sends, the method `do_POST` will handle HTTP POST requests to the server as it reads the incoming data, processes it, and sends a HTTP response with JSON data. This server will only listen for HTTP POST requests and then do the following things:
1. It will read the data passed to it
2. Parse the data passed
3. Add data to the global parameters that will get passed to the search engine API
4. Call upon the search engine API (through the function `get_recipes()` which will be talked about in a moment)
5. Craft the response and have the data be in the form of JSON data
6. Lastly to send the data back to the server

### get_recipes

The get_recipes function is the