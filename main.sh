#!/bin/bash

# Clear previous results
rm -f results/*.csv

# Run parsers with error handling
echo "Running European Commission parser..."
python source_scripts/EuropeanCommission_parser.py || echo "European Commission parser failed"

echo "Running Research Professional parser..."
python source_scripts/Research_Professional_parser.py || echo "Research Professional parser failed"

echo "Running SNF parser..."
python source_scripts/snf_parser.py || echo "SNF parser failed"

echo "Running Volkswagen parser..."
python source_scripts/volkswagen_parser.py || echo "Volkswagen parser failed"

# Combine and sort results
echo "Combining results..."
python combine_results.py

echo "Sorting results..."
python sort_results.py

echo "Parsing complete!"
