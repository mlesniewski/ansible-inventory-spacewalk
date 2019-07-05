#!/usr/bin/python
#
# blame: Michal Lesniewski


import xmlrpclib
import os
import json
import sys
from ansible.module_utils.six.moves import configparser

class SpacewalkInventory(object):

    def __init__(self):
	self.spacewalk_url = None
	spacewalk_login = None
	self.spacewalk_password = None
	self.read_config()

        if sys.argv[1] == '--list': 
            self.authentication()
            data = self.get_list()
            print json.dumps(data,indent=4)
        elif sys.argv[1] == '--host' and len(sys.argv) > 2:
            self.authentication()
            data = self.get_host(sys.argv[2])
            print json.dumps(data,indent=4)
        else:
            print("usage: --list  ..OR.. --host <hostname>")
            sys.exit(1)
        
        self.client.auth.logout(self.key)

    def authentication(self):
        self.client = xmlrpclib.Server(self.spacewalk_url,verbose=0)
        self.key = self.client.auth.login(self.spacewalk_login, self.spacewalk_password)
       
    def get_list(self):
	
        list = self.client.systemgroup.listAllGroups(self.key)
        data = {'_meta': {'hostvars': {}}}
        
        for group in list:
            name = group.get('name')
            systems = self.client.systemgroup.listSystems(self.key,name)
            data[name] = {}
            data[name]['hosts'] = []
            for host in systems:
                hostname = host['hostname']
                data[name]['hosts'].append(hostname)
                details = self.client.system.search.hostname(self.key,hostname)
                #data['_meta']['hostvars'][hostname] = {}
                data['_meta']['hostvars'][hostname] = self.get_host(hostname)
                #data['_meta']['hostvars'][hostname]['ansible_ssh_host'] = details[0]['ip']
        return data    				

    def get_host(self,inventory_hostname):
        data = {}   
        details = self.client.system.search.hostname(self.key,inventory_hostname)
        data['ansible_ssh_host'] = details[0]['ip']
        return data
         
    def read_config(self):
        config = configparser.SafeConfigParser()
        conf_path = './spacewalk.ini'
        if not os.path.exists(conf_path):
            conf_path = '/etc/ansible/custom/spacewalk.ini'
        if os.path.exists(conf_path):
            config.read(conf_path)
        # URL
        if config.has_option('spacewalk', 'URL'):
            self.spacewalk_url = config.get('spacewalk', 'URL')
        # login
        if config.has_option('spacewalk', 'login'):
            self.spacewalk_login = config.get('spacewalk', 'login')
        # password
        if config.has_option('spacewalk', 'password'):
            self.spacewalk_password = config.get('spacewalk', 'password')


SpacewalkInventory()
