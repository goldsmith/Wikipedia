import requests
import sys
import re
import random
from bs4 import BeautifulSoup
from wikipedia import wikipedia
import config
from selenium import webdriver
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

'''
    Need to pip install azure 
    Need to pip install selenium
    Run python setup.py install
    Install PhantomJS
    - https://www.vultr.com/docs/how-to-install-phantomjs-on-ubuntu-16-04

    Get Wikipedia Users and process data calls from Article Titles
'''

CAMPAIGN_NAME=sys.argv[1]
DATASET_MARKER=sys.argv[2]
WEB_URL=sys.argv[3]
AZURE_TABLE=sys.argv[4]
PROGRAM = sys.argv[5]

def get_campaign_users(web,program):
    '''
        Gets the outreachdashboard page and scrapes for WikiPedia Titles
    '''
    requests.packages.urllib3.disable_warnings()
    
    users = []

    if program == 'program':

        r = requests.get(web, verify=False)
        parsed = BeautifulSoup(r.text, 'html.parser')
        tbody = parsed.find('tbody','list')
        tr = tbody.findChildren("tr")

        print ("Program Count: "+str(len(tr)))
        
        for t in tr:
            __url = "https://outreachdashboard.wmflabs.org" + t.get("data-link") +"/students"   

            try:   
                driver = webdriver.PhantomJS()
                driver.get(__url)
                print (__url)
                p = driver.find_elements_by_class_name("students")
                __temp = [x.text.split("\n")[0] for x in p]
                users.append(__temp)
            except:
                print('Error loading URL: ' + __url)

        __users = [t for x in users for t in x]
        
        return __users

    else:

        try:
            driver = webdriver.PhantomJS()
            driver.get(web)
            p = driver.find_elements_by_class_name("students")
            __users = [x.text.split("\n")[0] for x in p]
        except:
            print('Error loading URL: ' + web)
        
        return __users

def create_task(part_key,row_key,campaign,dataset,userid,name,editcount,registration,gender,groups):
    task = {
        'PartitionKey': part_key,
        'RowKey': row_key,
        'CAMPAIGN': campaign,
        'DATASET': dataset,
        'USERID': userid, 
        'NAME': name, 
        'EDITCOUNT': editcount, 
        'REGISTRATION': registration,
        'GENDER': gender,
        'GROUPS': groups
    }

    return task

def table_service():
    # Get storage connection string from config.py
    account_connection_string = config.STORAGE_CONNECTION_STRING
    # Split into key=value pairs removing empties, then split the pairs into a dict
    config_update = dict(s.split('=', 1) for s in account_connection_string.split(';') if s)
        
    # Authentication
    account_name = config_update.get('AccountName')
    account_key = config_update.get('AccountKey')

    # Instance of TableService
    __table_service__ = TableService(account_name=account_name, account_key=account_key)

    return __table_service__

def main():

    collection=get_campaign_users(WEB_URL,PROGRAM)

    print ("Collection Length:"+str(len(collection)))

    table_data = {}

    count = len(collection)

    for r in collection:
        tmp = wikipedia.usersearch(r)
        p = [x for x in tmp['query']['users'][0].values()]
        if len(p) == 6:
            table_data.update({r:{'USERID': str(p[0]),'NAME': str(p[1]), 'EDITCOUNT': str(p[2]), 'REGISTRATION': str(p[3]),'GENDER': str(p[5]), 'GROUPS':list(p[4])}})
        count -= 1
        sys.stdout.write("\r%d%%" % count)
        sys.stdout.flush()

    tableservice = table_service()

    keys = [x for x in table_data.keys()]
    values = [x for x in table_data.values()]

    for index, t in enumerate(keys):

        task = create_task(str(random.randint(100000,99999999)),str(values[index]['USERID']),str(CAMPAIGN_NAME),str(DATASET_MARKER),str(values[index]['USERID']),str(values[index]['NAME']),str(values[index]['EDITCOUNT']),str(values[index]['REGISTRATION']),str(values[index]['GENDER']),str(values[index]['GROUPS']))
        print (task)
        tableservice.insert_entity(AZURE_TABLE, task)

if __name__ == '__main__':
    main()


