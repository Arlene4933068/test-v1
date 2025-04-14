#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dashboard application runner
"""

import os
import sys
import logging
import argparse

# Adjust the Python path to include the project root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the dashboard app
from src.dashboard.app import DashboardApp

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run the AIoT Edge Security Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def main():
    """Main function to run the dashboard"""
    args = parse_arguments()
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('dashboard.log')
        ]
    )
    
    logger = logging.getLogger("dashboard_runner")
    logger.info(f"Starting dashboard application on {args.host}:{args.port}")
    
    try:
        # Initialize and run the dashboard app
        app = DashboardApp()
        app.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        logger.error(f"Failed to start dashboard application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()