#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 04:01:10 2024

@author: user
"""
import requests
import pandas as pd

# Function to fetch company metadata from SEC EDGAR API using CIK
def fetch_company_metadata(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        'User-Agent': 'YourNameHere (your-email@example.com)',  # Replace with your details
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            company_name = data.get('name', 'N/A')
            industry = data.get("ownerOrg", 'N/A')
            recent_filings = data.get('filings', {}).get('recent', {})
            filings = []
            for form, date, doc in zip(recent_filings.get('form', []),
                                       recent_filings.get('filingDate', []),
                                       recent_filings.get('primaryDocument', [])):
                base_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                filing_url = base_url + doc
                filings.append({
                    'Form Type': form,
                    'Filing Date': date,
                    'Filing URL': filing_url
                })
            return {
                'CIK': cik,
                'Company Name': company_name,
                'industry': industry,
                'Filings': filings
            }
        else:
            print(f"Failed to retrieve data for CIK {cik}: HTTP {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred while fetching metadata for CIK {cik}: {e}")
        return None

# Function to fetch financial data from the new XBRL JSON endpoint
def fetch_xbrl_data(cik):
    """
    Fetches financial data using the XBRL JSON endpoint from the SEC API.

    Parameters:
        cik (str): The CIK of the company to fetch data for.

    Returns:
        dict: Financial metrics extracted from the JSON response.
    """
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {
        'User-Agent': 'YourNameHere (your-email@example.com)',  # Replace with your details
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()

            # Extract specific financial metrics
            financial_data = {}

            # Example financial metrics using XBRL tags
            financial_data['Revenue'] = data.get('facts', {}).get('us-gaap', {}).get('Revenues', {}).get('units', {}).get('USD', [])
            financial_data['Net Income'] = data.get('facts', {}).get('us-gaap', {}).get('NetIncomeLoss', {}).get('units', {}).get('USD', [])
            financial_data['Total Assets'] = data.get('facts', {}).get('us-gaap', {}).get('Assets', {}).get('units', {}).get('USD', [])
            financial_data['Total Liabilities'] = data.get('facts', {}).get('us-gaap', {}).get('Liabilities', {}).get('units', {}).get('USD', [])
            financial_data['Equity'] = data.get('facts', {}).get('us-gaap', {}).get('StockholdersEquity', {}).get('units', {}).get('USD', [])

            return financial_data
        else:
            print(f"Failed to retrieve XBRL data for CIK {cik}: HTTP {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred while fetching XBRL data for CIK {cik}: {e}")
        return None

# Function to process multiple companies and extract their financial data
def process_companies(cik_list):
    all_financials = []

    for cik in cik_list:
        print(f"\nProcessing CIK: {cik}")
        metadata = fetch_company_metadata(cik)
        if metadata:
            company_name = metadata['Company Name']
            industry_name = metadata['industry']
            print(f"Company Name: {company_name}")

            # Fetch financial data from the XBRL JSON endpoint
            xbrl_data = fetch_xbrl_data(cik)
            if xbrl_data:
                for metric, values in xbrl_data.items():
                    if values:
                        # Extracting only the most recent value for each metric
                        latest_value = values[-1]['val'] if values else 'N/A'
                        xbrl_data[metric] = latest_value
                    else:
                        xbrl_data[metric] = 'N/A'

                # Append the financials data to the list
                financials = {
                    'CIK': cik,
                    'Company Name': company_name,
                    'industry': industry_name,
                    **xbrl_data
                }
                all_financials.append(financials)

    # Convert the list of financials into a pandas DataFrame
    financials_df = pd.DataFrame(all_financials)
    return financials_df

# Main execution
if __name__ == "__main__":
    # List of CIKs for the companies you want to process
    cik_list = [
        '0000320193',  # Apple Inc.
        '0000789019',  # Microsoft Corporation
        '0001652044'   # Alphabet Inc. (Google)
    ]

    financials_df = process_companies(cik_list)

    print("\nFinal Financial DataFrame:")
    print(financials_df.head())

    # Optionally, save the DataFrame to a JSON file for further use
    financials_df.to_json('financial_data.json', orient='records', indent=4)
    print("\nFinancial data has been saved to 'financial_data.json'.")

