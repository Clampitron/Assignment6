# -*- coding: utf-8 -*-
#! python3

"""
Program to start a microservice that will find recipes on the internet given a specific lifestyle,
cuisine, and type.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps
from urllib.parse import parse_qs
from serpapi import GoogleSearch        # pip install google-search-results


HOST = "localhost"
PORT = 5001
params = {
        "q": "",
        "location": "United States",
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": ""
        }


class NoAPIKeyError(Exception):
    """
    Exception raised for search engine api key errors.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message="No API key or incorrect API key in api.key file"):
        self.message = message
        super().__init__(self.message)


class MServer(BaseHTTPRequestHandler):
    """
    Class to create a HTTP server that serves as a microservice for getting the type of recipes
    the user wanted.
    """

    def do_POST(self):
        """
        A method to handle HTTP POST requests to the server.

        :param self: current instance of the class

        :returns: None
        """
        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length)  # Read the data
        result_dict = json.loads(post_data.decode('utf-8'))  # Decode and load JSON data

        lifestyle = result_dict.get("lifestyle")
        cuisine = result_dict.get("cuisine")
        food_type = result_dict.get("type")

        if lifestyle and cuisine and food_type:
            params["q"] = f"{lifestyle} {cuisine} {food_type} recipes"
            links = self.__get_recipes()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            json_data = dumps({"links": links})
            self.wfile.write(json_data.encode())
        else:
            # If required data isn't provided, send an error response
            self.send_response(400)  # Bad Request status code
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_message = dumps({"error": "Missing lifestyle, cuisine, or food type in request."})
            self.wfile.write(error_message.encode())


    def __get_recipes(self) -> list[str]:
        """
        Microservice to get recipes based on user preferences.

        :returns: list of recipe urls
        """
        search_results = GoogleSearch(params).get_dict()
        links = []
        # Add general search results to links
        if "recipes_results" in search_results.keys():
            for recipe in search_results["recipes_results"]:
                links.append(recipe["link"])
        if search_results["organic_results"]:
            for recipe in search_results["organic_results"]:
                links.append(recipe["link"])
        return links


if __name__ == "__main__":
    with open(r".\api.key", "r", encoding="utf8") as file:
        params["api_key"] = file.readline()
        if not params["api_key"]:
            raise NoAPIKeyError
    webServer = HTTPServer((HOST, PORT), MServer)
    print(f"Server started http://{HOST}:{PORT}")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
