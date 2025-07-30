#!/bin/bash
set -e

# Run the Python script
python src/extract.py
# Run the next step in the pipeline
python src/transform_load.py
# Print a success message
echo "Pipeline completed successfully."


find logs/ -type f -name "*.log" -mtime +7 -exec rm {} \;
echo "Old logs cleaned up."