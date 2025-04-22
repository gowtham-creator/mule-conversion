# MuleSoft to AWS Code Converter

This repository contains a prototype implementation of a tool that converts MuleSoft code to AWS code.

## Features
- Takes MuleSoft code from a text file as input
- Generates AWS code based on the provided MuleSoft code
- Provides a summary of the conversion process

## Prerequisites
- Python 3.x
- Streamlit library

## Installation
1. Clone the repository:
git clone https://github.com/your-username/mule-to-aws-converter.git


2. Navigate to the project directory:
cd mule-to-aws-converter


3. Install the required dependencies:
pip install -r requirements.txt


## Usage
1. Place your MuleSoft code in the `mule_code.txt` file located in the repository.

2. Run the Streamlit application:
streamlit run app.py


3. Open your web browser and visit http://localhost:8501 to access the application.

4. Upload the `mule_code.txt` file containing your MuleSoft code.

5. Select the desired conversion option:
- Hit "AWS Code" to generate the AWS code.
- Hit "Summary" to get a summary of the conversion process.

6. View the generated AWS code or summary in the application interface.
