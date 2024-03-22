
import pandas as pd
import tldextract
from email_validator import validate_email, EmailNotValidError
import Levenshtein as lev
import streamlit as st
import requests

st.title(" Welcome to Nodi! 👋")
st.markdown(
                """This mean viability product is intended to flesh out the use cases and processes that would need data validation.
                Our goal with each page is to test the robustness and ability to solve business use cases that these services are intended for.     
                """
)

url = 'https://github.com/brownpaperboi/nodi_streamlit/blob/03e16503a09d7c9826ce1e82d5d6834dbee02889/disposable_email_blocklist.conf'

response =  requests.get(url)
if response.status_code == 200:
    blocklist_content = {line.strip() for line in response.text.split('\n')}
else:
    st.error('Failed to load the blocklist file from GitHub.')
    blocklist_content = set()

known_domains = ['gmail.com', 'yahoo.com', 'udel.edu',  'hotmail.com']
results_df = pd.DataFrame(columns=['Email', 'Validation_Status', 'Blocklist_flag'])


tab1,tab2 = st.tabs(["Single Email Input","CSV File Upload"])

with tab1:
    input= st.text_input("Input A Single Email",placeholder='Enter Email')
    if input:
        def closest_domain(domain, known_domains):
            """Find the closest domain from the list of known domains using Levenshtein distance."""
            closest, min_distance = None, float('inf')
            for known_domain in known_domains:
                distance = lev.distance(domain, known_domain)
                if distance < min_distance:
                    closest, min_distance = known_domain, distance
            return closest

        try:
                # Validate the email address
            validate_email(input)
            validation_status = 'Valid'
        except EmailNotValidError as e:
            validation_status = f'Invalid - {e}'
                
        blocklist_flag = 1 if input.partition('@')[2] in blocklist_content else 0
        domain = tldextract.extract(input).domain + '.' + tldextract.extract(input).suffix 
        suggested_domain = closest_domain(domain, known_domains)
        
        results_df = results_df.append({
            'Email': input,
            'Validation_Status': validation_status,
            'Blocklist_flag': blocklist_flag,
            'Suggested_Domain': suggested_domain if validation_status != 'Valid' else 'No Suggestion'
        }, ignore_index=True)

        st.dataframe(results_df)
    
## This is to capture CSV input of email usersg
with tab2:
    st.header("Validate CSV File of Emails")

    upload = st.file_uploader('Upload CSV of emails')
    
    if upload is not None:
        df = pd.read_csv(upload, header=None, names=['Email'])
        series = df['Email']
        resultscsv_df = pd.DataFrame(columns=['Email', 'Validation_Status', 'Blocklist_flag'])
        
        def closest_domain(domain, known_domains):
            """Find the closest domain from the list of known domains using Levenshtein distance."""
            closest, min_distance = None, float('inf')
            for known_domain in known_domains:
                distance = lev.distance(domain, known_domain)
                if distance < min_distance:
                    closest, min_distance = known_domain, distance
            return closest
        
        # Loop through the Series, validate email addresses, and check blocklist
        for index, email in series.items():
            try:
                # Validate the email address
                validate_email(email)
                validation_status = 'Valid'
            except EmailNotValidError as e:
                validation_status = f'Invalid - {e}'

            # Check if the domain part of the email is in the blocklist
            blocklist_flag = 1 if email.partition('@')[2] in blocklist_content else 0
            domain = tldextract.extract(email).domain + '.' + tldextract.extract(email).suffix
            suggested_domain = closest_domain(domain, known_domains)

            resultscsv_df = resultscsv_df._append({
                'Email': email,
                'Validation_Status': validation_status,
                'Blocklist_flag': blocklist_flag,
                'Suggested_Domain': suggested_domain if validation_status != 'Valid' else 'No Suggestion'
            }, ignore_index=True)

        st.dataframe(resultscsv_df)

