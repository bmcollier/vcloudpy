import xml.etree.ElementTree as ET
import requests
import base64
import logging
import pytest

class VCloudSession:
    
    def __init__(self, username, password, organisation, endpoint):
        
        self.headers = {}
        self.username = username
        self.password = password
        self.organisation = organisation
        self.endpoint = endpoint
        
        logging.getLogger().setLevel(logging.INFO)
        
        login = {'Accept':'application/*+xml;version=5.1', \
           'Authorization':'Basic '+ base64.b64encode(username + "@" + organisation + ":" + password)}
        response = requests.post(endpoint + 'sessions', headers = login)
        for key, value in response.headers.iteritems():
            if key == "x-vcloud-authorization":
                self.headers[key]=value
        logging.info("Headers: %s", self.headers)
        logging.info("Status code %s", response.status_code)
        self.last_status = response.status_code
    
    def organisation_url(self):
        
        response = requests.get(self.endpoint + 'org', data=None, headers = self.headers)
        root = ET.fromstring(response.content)
        for child in root:
                self.organisation = child.get("href")
        
        response = requests.get(self.organisation, data=None, headers = self.headers)
        self.root = ET.fromstring(response.content)
        
        return self.organisation
    
    def get_catalogue(self):
        response = requests.get(self.endpoint + 'vms/query', data=None, headers = self.headers)
        return response.text
    
    def list_vapps(self):
        payload = {"page": "1", "pageSize":"25", "format":"idrecords"}
        response = requests.get(self.endpoint + 'vApps/query', data=None, headers = self.headers, params=payload)
        return response.text
    
    def list_vapp_templates(self):
        response = requests.get(self.endpoint + 'vAppTemplates/query', data=None, headers = self.headers)
        return response.text
    
    def get_vapp(self, vapp_id):
        response = requests.get(self.endpoint + "/vApp/" + vapp_id, data=None, headers = self.headers)
        return response.text
    
    def suspend_vapp(self, vapp_id):
        response = requests.post(self.endpoint + "/vApp/" + vapp_id + "/power/action/suspend", data=None, headers=self.headers)
        return response.text
    
    def get_memory_config(self, vapp_id):
        response = requests.get(self.endpoint + "/vApp/" + vapp_id + '/virtualHardwareSection/memory', data=None, headers=self.headers)
        tree = ET.fromstring(response.content)
        return tree
    
    def set_memory_config(self, vapp_id):
        tree = ET.parse("3gb_mem.xml")
        root = tree.getroot() 
        xmlstring = ET.tostring(root, encoding='utf8', method='xml')
        response = requests.put(self.endpoint + "/vApp/" + vapp_id + "/virtualHardwareSection/memory", data=xmlstring, headers=self.headers)
        return response.text

if __name__ == "__main__":
    """Fire off main test if vcloudpy called directly"""
    import tests.test_memchange
    tests.test_memchange.test_main()