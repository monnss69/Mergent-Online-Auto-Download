import pandas as pd
import numpy as np

def extract_data_from_excel(file_path):
    # Read the Excel file
    data = pd.read_excel(file_path)
    
    # Initialize lists to store data
    last_name = []
    first_name = []
    analys_id = []
    IBES_id = []
    company = []
    
    # Process rows until first empty company name
    for index, row in data.iterrows():
        # Get company name first
        if pd.isna(row['report_broker_name']):
            break
            
        broker_name = str(row['report_broker_name'])
        company_name = broker_name.split(' ', 1)[1] if ' ' in broker_name else broker_name
        
        # If company name is empty, stop processing
        if not company_name:
            break
            
        # Add company name
        company.append(company_name)
        
        # Process other fields
        last_name.append(str(row['name_last']) if not pd.isna(row['name_last']) else '')
        
        if pd.isna(row['report_author_clean']):
            first_name.append('')
        else:
            author_name = str(row['report_author_clean'])
            first_name.append(author_name.split(' ')[0])
        
        analys_id.append(str(row['analys']) if not pd.isna(row['analys']) else '')
        IBES_id.append(str(row['IBES_id']) if not pd.isna(row['IBES_id']) else '')
    
    print(f"\nProcessed {len(company)} rows with valid company names")
    
    return last_name, first_name, analys_id, IBES_id, company

# Example usage:
# file_path = "broker_analyst_2_1.xlsx"
# last_name, first_name, analys_id, IBES_id, company = extract_data_from_excel(file_path)
# print("last_name=", last_name)
# print("first_name=", first_name)
# print("analys_id=", analys_id)
# print("IBES_id=", IBES_id)
# print("company=", company)
