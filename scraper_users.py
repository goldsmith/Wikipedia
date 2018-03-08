import requests
import sys
import re
import random
from bs4 import BeautifulSoup
from wikipedia import wikipedia
import config
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

'''
    Need to pip install azure 
    Run python setup.py install

    Get Wikipedia Article Titles and process data calls from Article Titles
'''

CAMPAIGN_NAME=sys.argv[1]
DATASET_MARKER=sys.argv[2]
WEB_URL=sys.argv[3]
AZURE_TABLE=sys.argv[4]

def get_campaign_users():
    '''
        Gets the outreachdashboard page and scrapes for WikiPedia Titles
    '''
    requests.packages.urllib3.disable_warnings()
    r = requests.get(WEB_URL, verify=False)
    parsed = BeautifulSoup(r.text, 'html.parser')
    titles = parsed.find_all('td','title')

    items = []

    # Regex for string with "Q" and at least 2 numbers
    p = re.compile(r'^(?![Q]\d{2})')

    for t in titles:
        for c in t.children:
            if c.string != "\n" and c.string != "\n(deleted)\n" and p.search(c.string):
                items.append(c.string)

    return items

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
        'GENDER': gender
    }

    __ltmp = []
    for l in groups:
        __ltmp.append(l)

    if __ltmp:
        task.update({"GROUPS": str(__ltmp)})

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

    collection=get_campaign_users(CAMPAIGN_NAME)

    print ("Collection Length:"+str(len(collection)))

    table_data = {}

    count = len(collection)

    for r in collection:
        p = wikipedia.user(r)
        table_data.update({r:{'USERID': str(p.userid),'NAME': str(p.name), 'EDITCOUNT': str(p.editcount), 'REGISTRATION': str(p.registration),'GENDER': str(p.gender), 'GROUPS':list(p.groups)}})
        count -= 1
        sys.stdout.write("\r%d%%" % count)
        sys.stdout.flush()

    tableservice = table_service()

    keys = [x for x in table_data.keys()]
    values = [x for x in table_data.values()]

    for index, t in enumerate(keys):

        task = create_task(str(random.randint(100000,99999999)),str(values[index]['USERID']),str(CAMPAIGN_NAME),str(DATASET_MARKER),str(values[index]['NAME']),str(values[index]['EDITCOUNT']),str(values[index]['REGISTRATION']),str(values[index]['GENDER']),str(values[index]['GROUPS']))
        print (task)
        tableservice.insert_entity(AZURE_TABLE, task)

if __name__ == '__main__':
    main()


