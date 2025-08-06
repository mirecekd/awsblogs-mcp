#!/usr/bin/env python3
"""
AWS Blogs MCP Server - HTTP Entry Point

Starts MCP server for AWS Blog and News articles on HTTP transport (port 8807).
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from awsblogs_mcp_server.server_http import main

if __name__ == "__main__":
    main()
