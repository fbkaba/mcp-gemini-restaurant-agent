#!/usr/bin/env python3

import sys
print("Importing from restaurant_server...")
from restaurants_mcp_server.restaurants_server import main
print("Import successful!")

if __name__ == "__main__":
    print("Starting main function ...")
    sys.exit(main()) 