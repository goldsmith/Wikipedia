import requests
import sys
import random
from bs4 import BeautifulSoup
from wikipedia import wikipedia
from datetime import datetime
import config
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

'''
    Need to pip install azure 
    Run python setup.py install

    Get Wikipedia Article Titles and process data calls from Article Titles
'''

DATASET_MARKER=sys.argv[1]
AZURE_TABLE=sys.argv[2]
CAMPAIGN_NAME = "Random Sample"

def get_random_articles():
    '''
        Gets random articles sets
    '''
    requests.packages.urllib3.disable_warnings()

    _titles = wikipedia.random_id(pages=500)
    
    return _titles

def is_deleted(item):
    try:
        if wikipedia.page(item):
            return False
    except:
        return True

def has_date(item):
    try:
        _page = wikipedia.page(title=None,pageid=item)
        _dt = datetime.strptime(_page.touched,'%Y-%m-%dT%H:%M:%SZ')
        if _dt.year >= 2015:
            _revs = get_revisions(_page.pageid,False)
            _tmpdt = datetime.strptime(_revs[0]['timestamp'],'%Y-%m-%dT%H:%M:%SZ')
            if _tmpdt.year >= 2015 and _tmpdt.year <= 2017:
                return _page
            else:
                return ""
        else:
            return ""
    except:
        return ""

def get_logdata(item, logtype):
    try:
        _logs = wikipedia.logsearch(item,logtype)
        return list(_logs['query']['logevents'])
    except:
        return list()

def get_templates(item):
    try:
        _templates = wikipedia.templatesearch(item)
        return _templates
    except:
        return list()

def get_revisions(item,title):
    try:
        _revs = wikipedia.revisionsearch(item, title=title)
        return _revs
    except: 
        return list()

def create_task(dataset_marker,camp_name,created,row_key,part_key,page_id,title,logs,temps,revs,url):
    task = {
        'PartitionKey': part_key, 
        'RowKey': row_key, 
        'PAGEID': page_id, 
        'TOUCHED': created,
        'TITLE': title, 
        'CAMPAIGN': camp_name,
        'URL': url,
        'DATASET': dataset_marker
    }

    _ltmp = []
    for l in logs:
        _ltmp.append(l)

    if _ltmp:
        task.update({"LOGS": str(_ltmp)})

    _ttmp = []
    for t in temps:
        _ttmp.append(t['title'])

    if _ttmp:
        task.update({"TEMPLATES": str(_ttmp)})
    
    _rtmp = []
    for r in revs:
        _rtmp.append(r)

    if _rtmp:
        task.update({"REVISIONS": str(_rtmp)})

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

    collection=get_random_articles()

    print ("Article Count:" + str(len(collection)))

    table_data = {}

    count = len(collection)

    for r in collection:
        print (r)
        _tmppge = has_date(r)
        if _tmppge != "":
            table_data.update({_tmppge.title:{'PAGEID': str(_tmppge.pageid),'TOUCHED': str(_tmppge.touched), 'URL': str(_tmppge.url), 'TITLE': str(_tmppge.title)}})
            print ("Date Match")
        else:
            print ("Date Not Match")

    tableservice = table_service()

    keys = [x for x in table_data.keys()]
    values = [x for x in table_data.values()]

    for index, t in enumerate(keys):
        logs = [l for l in get_logdata(str(t), 'delete') if "delet" in str(l)]
        temps = [s for s in get_templates(str(t)) if "delet" in str(s)]
        revs = [r for r in get_revisions(str(t),True) if "delet" in str(r)]
        task = create_task(str(DATASET_MARKER),str(CAMPAIGN_NAME),str(values[index]['TOUCHED']),str(CAMPAIGN_NAME),str(random.randint(100000,99999999)),str(values[index]['PAGEID']),str(values[index]['TITLE']),logs,temps,revs,str(values[index]['URL']))
        print (task)
        tableservice.insert_entity(AZURE_TABLE, task)

if __name__ == '__main__':
    main()


