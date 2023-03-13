from tabula import read_pdf
import PyPDF2
import pandas as pd
import re

def AppleStatementRead(filename:str):
    """Read Apple Card Statements from 2020-2023. Last 2 tables are not useful: Daily Cash and Interest Charged

    Args:
        filename (str): _description_
    """
    headers = ["date", "description", "daily cash percentage", "daily cash", "amount"]
    max_pages = len(PyPDF2.PdfReader(filename).pages)
    pdf_tables = read_pdf(filename,pages=list(range(2,max_pages+1)),multiple_tables=True, guess=False)

    if len(pdf_tables) >2:  #drop last 2 tables
        del pdf_tables[-1]
        del pdf_tables[-1]
        del pdf_tables[-1]

    date_description_cashback_cashback_credit = re.compile(r'([0-9]{2}/[0-9]{2}/[0-9]{4})(.*)[\s].*([0-9]%).*([+-]?[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2}$)')
    
    returns_regex = re.compile(r'([0-9]{2}/[0-9]{2}/[0-9]{4})[\s](.*)')

    for i in range(len(pdf_tables)):
        df = pdf_tables[i]
        if len(df.index[df['Unnamed: 0'] == "Transactions"]) >0:
            index_where_transaction_appears = df.index[df['Unnamed: 0'] == "Transactions"][0]
            df = df.drop(list(range(index_where_transaction_appears+2)))
            df = df.drop(df.index [ [len(df)-1, len(df)-2] ]) 
            
            df = df[~df['Unnamed: 0'].str.contains(r'Daily Cash Adjustment')]
            returns = df[df['Unnamed: 0'].str.contains(r'(RETURN)', na=True)]
            disputes = df[df['Unnamed: 0'].str.contains(r'DISPUTE', na=True)]
            df = df[~df['Unnamed: 0'].str.contains(r'RETURN')]
            df = df[~df['Unnamed: 0'].str.contains(r'DISPUTE')]

            val = df.iloc[0][0]
            m = date_description_cashback_cashback_credit.match(val)
            # Normal Transaction
            if m:
                # Drop the first entry which should be the header,  Drop the last entry which should be Total Daily Cash this month
                temp = df['Unnamed: 0'].str.split(pat='([0-9]{2}/[0-9]{2}/[0-9]{4})(.*)[\s].*([0-9]%).*([+-]?[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2}$)',expand=True)
                temp = temp.iloc[: , 1:-1]
                temp1 = pd.concat([temp,df.Statement],axis=1)
                temp1.columns = headers
            else:            
                df = df.drop(df.index [ [len(df)-1, len(df)-2,len(df)-3 ] ]) 
                temp = df['Unnamed: 0'].str.split(pat='([0-9]{2}/[0-9]{2}/[0-9]{4}\s)(.*)',expand=True)     # Unnamed: 0 should feature the date and description, we extract those            
                temp = temp.iloc[: , 1:-1]

                temp1 = df['Unnamed: 1'].str.split(pat='([0-9]%)(.*)',expand=True)     # Unnamed: 0 should feature the date 
                temp1 = temp1.iloc[: , 1:-1]
                temp1 = pd.concat([temp,temp1,df.Statement],axis=1)
                temp1.columns = headers


            
            # Return
            if len(returns)>0:
                rtemp = returns['Unnamed: 0'].str.split(pat='([0-9]{2}/[0-9]{2}/[0-9]{4}\s)(.*)',expand=True)
                rtemp = rtemp.iloc[: , 1:-1]
                rtemp['daily cash percentage'] = 0
                rtemp['daily cash'] = 0
                
                rtemp1 = pd.concat([rtemp,returns.Statement],axis=1)
                rtemp1.columns = headers
                temp1 = pd.concat([temp1,rtemp1],axis=0)

            pdf_tables[i] = temp1

    return pd.concat(pdf_tables, axis=0)