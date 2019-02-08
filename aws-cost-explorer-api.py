# /home/ec2-user/anaconda3
import argparse
import boto3
from boto3 import client
import datetime 
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import xlsxwriter 
import matplotlib.pyplot as plt 
from openpyxl import Workbook 
from openpyxl import load_workbook 
from openpyxl.drawing.image import Image 
 

access_key = 'put your aws access key'
secret_key = 'put your aws secret key' 

cd = boto3.client('ce', region_name='us-east-1',
				aws_access_key_id= access_key,
                                aws_secret_access_key= secret_key ) 


parser = argparse.ArgumentParser()
parser.add_argument('--days', type=int, default=30)
args = parser.parse_args()


now = datetime.datetime.utcnow()
start = (now - datetime.timedelta(days=args.days)).strftime('%Y-%m-%d')
end = now.strftime('%Y-%m-%d')  

data = cd.get_cost_and_usage(TimePeriod={'Start': start, 'End':  end}, 
 	Granularity='DAILY', Metrics=['BlendedCost'], 
 	GroupBy=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}]) 

ls = data['ResultsByTime']



am = []
act=[]
dt = []
for i in ls:

    for group in i['Groups']:
        amount = group['Metrics']['BlendedCost']['Amount']
        linked_account = "\t".join(group['Keys'])
        date=i['TimePeriod']['Start']
        am.append(amount)
        act.append(linked_account)
        dt.append(date)
    
    dic = {'Date': dt, 'Linkedaccount': act, 'Amount': am}
    df = pd.DataFrame(dic) 
# convert the datatype of col amount to numeric 
# round amount col into 2 decimal places 

df["Amount"] = pd.to_numeric(df["Amount"])   
df['Amount']=df['Amount'].map(lambda x: round(x,2))

# change dataframe into a pivot table 

df2 = df.pivot(index = 'Linkedaccount', columns='Date',values='Amount' )  

# add a col which is the sum of all the 
df2['sum'] = df2[list(df2)].sum(axis=1) 
# sort the dataframe in descending order based on sum col value
df2 = df2.sort_values('sum',ascending=False)



df2['AWS_AccountID'] = pd.to_numeric(df2.index)  

fig = df_pic.plot(kind='bar', stacked=True, title = 'Top 10 Users Spend').get_figure()

fig.savefig(r'path to save the pic', bbox_inches = 'tight')

img = Image(r'path to save the pic')

#######################################################################
###################Conditional format of the cells in df###############

# hightlight the cell > 2 * last 6 days avgerage and exclude the sum colum  
df_final.style.apply(lambda x: ["background-color: yellow" if (v > 2.0 * x.iloc[:6].mean(axis=0))
	else "" for i, v in enumerate(x)],axis = 1, subset = list(df_final)[4:len(df_final.columns)-1])\
	.to_excel(r'path to save your formated report\result.xlsx',engine='xlsxwriter') 

# load the saved xlsx file  

wb = load_workbook(filename = r'same path as the path saved above\result.xlsx')
sheet = wb.active 
sheet.add_image(img,'P5') 
sheet['Q1'] = 'Any cell larger than twice of the past 6 days average spent is higlighted'

wb.save(r'the final path to save your completted report\report.xlsx') 



 

