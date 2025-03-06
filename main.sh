#!/bin/sh

conda activate grant-parser

rm results/*

python source_scripts/EuropeanCommission_parser.py
python source_scripts/Research_Professional_parser.py
python source_scripts/snf_parser.py
python source_scripts/volkswagen_parser.py

python combine_results.py
python sort_results.py

conda deactivate
