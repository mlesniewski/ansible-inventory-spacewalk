#!/usr/bin/python
import xmlrpclib
import os
import json
from ansible.module_utils.six.moves import configparser


config = configparser.SafeConfigParser()
conf_path = './spacewalk.ini'
if not os.path.exists(conf_path):
    conf_path = '/etc/ansible/custom/spacewalk.ini'
if os.path.exists(conf_path):
    config.read(conf_path)
# URL
if config.has_option('spacewalk', 'URL'):
    spacewalk_url = config.get('spacewalk', 'URL')
# login
if config.has_option('spacewalk', 'login'):
    spacewalk_login = config.get('spacewalk', 'login')
# password
if config.has_option('spacewalk', 'password'):
    spacewalk_password = config.get('spacewalk', 'password')


client = xmlrpclib.Server(spacewalk_url,verbose=0)

key = client.auth.login(spacewalk_login, spacewalk_password)
list = client.systemgroup.listAllGroups(key)

data = {'_meta': {'hostvars': {}}}

for group in list:
   #print '#',group.get('description')
   name = group.get('name')
   #print '['+name+']'
   systems = client.systemgroup.listSystems(key,name)
   data[name] = {}
   data[name]['hosts'] = []
   for host in systems:
	hostname = host['hostname']
	data[name]['hosts'].append(hostname)
	details = client.system.search.hostname(key,hostname)
	data['_meta']['hostvars'][hostname] = {}
	data['_meta']['hostvars'][hostname]['ansible_ssh_host'] = details[0]['ip']

data_json = json.dumps(data,indent=4)
print data_json

client.auth.logout(key)
