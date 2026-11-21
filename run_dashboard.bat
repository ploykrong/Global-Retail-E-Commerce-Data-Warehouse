@echo off
title Global Retail Data Warehouse ^& Executive Dashboard
echo Starting Streamlit Dashboard on http://localhost:8501 ...
cd /d "%~dp0"
call env\Scripts\activate.bat
python -m streamlit run dashboard\app.py --server.port=8501 --server.address=localhost
pause
