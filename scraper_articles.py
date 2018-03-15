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
PROGRAM = sys.argv[5]

def get_campaign_articles(web,program):
    '''
        Gets the outreachdashboard page and scrapes for WikiPedia Titles
    '''
    requests.packages.urllib3.disable_warnings()
    
    items = []

    if program == 'program':

        r = requests.get(web, verify=False)
        parsed = BeautifulSoup(r.text, 'html.parser')
        #titles = parsed.find_all('td','title')
        tbody = parsed.find('tbody','list')
        tr = tbody.findChildren("tr")
        
        print ("Program Count: "+str(len(tr)))
        
        for t in tr:
            _url = "https://outreachdashboard.wmflabs.org" + t.get("data-link") +"/articles/details.json"   

            try:   
                _c = requests.get(_url, verify=False)
                print (_c.url)
                _art = _c.json()["course"]["articles"]
                _items = [x["title"] for x in _art if x["new_article"] is True and x["language"] == 'en']
                items.append(_items)
            except:
                print('Error loading URL: ' + _url)

        _titles = [t for x in items for t in x]
        
        return _titles

    else:
        _url = web +"/articles/details.json"
        try:
            _c = requests.get(_url, verify=False)
            print (_c.url)
            _art = _c.json()["course"]["articles"]
            _items = [x["title"] for x in _art if x["new_article"] is True and x["language"] == 'en']
            items.append(_items)
        except:
            print('Error loading URL: ' + _url)
        
        _titles = [t for x in items for t in x]
        
        return _titles

def is_deleted(item):
    try:
        if wikipedia.page(item):
            return False
    except:
        return True

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

def get_revisions(item):
    try:
        _revs = wikipedia.revisionsearch(item, title=True)
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

    collection=get_campaign_articles(WEB_URL,PROGRAM)

    print ("Article Count:" + str(len(collection)))

    table_data = {}

    count = len(collection)

    for r in collection:
        if is_deleted(r):
            table_data.update({r:{'PAGEID': "Deleted",'TOUCHED': "Deleted", 'URL': "Deleted"}})
        else:
            p = wikipedia.page(r)
            table_data.update({r:{'PAGEID': str(p.pageid),'TOUCHED': str(p.touched), 'URL': str(p.url)}})
        count -= 1
        sys.stdout.write("\r%d%%" % count)
        sys.stdout.flush()

    tableservice = table_service()

    keys = [x for x in table_data.keys()]
    values = [x for x in table_data.values()]

    for index, t in enumerate(keys):

        logs = [l for l in get_logdata(str(t), 'delete') if "delet" in str(l)]
        temps = [s for s in get_templates(str(t)) if "delet" in str(s)]
        revs = [r for r in get_revisions(str(t)) if "delet" in str(r)]
        task = create_task(str(DATASET_MARKER),str(CAMPAIGN_NAME),str(values[index]['TOUCHED']),str(CAMPAIGN_NAME),str(random.randint(100000,99999999)),str(values[index]['PAGEID']),str(t),logs,temps,revs,str(values[index]['URL']))
        print (task)
        tableservice.insert_entity(AZURE_TABLE, task)

if __name__ == '__main__':
    main()


