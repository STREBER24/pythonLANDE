from bs4 import BeautifulSoup
import privateConfig
import pandas as pd
import requests
import config
import time
import json
import os
import io

def getDateString():
      date = time.localtime()
      return str(date.tm_year).zfill(4) + '_' + str(date.tm_mon).zfill(2) + '_' + str(date.tm_mday).zfill(2)

def ensureDir(file: str):
      dir = os.path.dirname(file)
      if not os.path.isdir(dir):
            os.mkdir(dir)

class Profile():
      def __init__(self, keys: list=[], values: list=[]):
            self.keys = keys
            self.values = values
      def to_dict(self):
            return {key: value for key, value in zip(self.keys, self.values)}
      def to_json(self, filename: str):
            ensureDir(filename)
            file = io.open(filename, 'w', encoding='utf-8')
            json.dump(self.to_dict(), file, indent=2, ensure_ascii=False)
            file.close()
      def to_csv(self, filename: str, sep: str=','):
            ensureDir(filename)
            file = io.open(filename, 'w', encoding='utf-8')
            file.write(sep.join([str(i) for i in self.keys]))
            file.write('\n')
            file.write(sep.join([str(i) for i in self.values]))
            file.close()
      def get(self, index):
            if len(self.values) > index:
                  return self.values[index]
            

class LandeSession(requests.Session):
      def __init__(self, auth: dict):
            super().__init__()
            response = self.get(config.link + 'login')
            soup = BeautifulSoup( response.content , 'html.parser')
            for input in soup.find_all('input'):
                  if input.get('name') == '_token':
                        auth['_token'] = input.get('value')
            self.post(config.link + 'login', data=auth)
      def getTransactions(self):
            response = self.get(config.link + 'investor/transactions/export')
            dataframe = pd.read_excel(response.content)
            return dataframe
      def getInvestments(self):
            response = self.get(config.link + 'investor/reports/investments')
            dataframe = pd.read_excel(response.content)
            return dataframe
      def getProfile(self):
            response = self.get(config.link + 'settings/profile')
            soup = BeautifulSoup( response.content , 'html.parser')
            for element in soup.find_all('div'):
                  if element.get('class') == ['card', 'border-0', 'rounded-1', 'p-4', 'shadow-lg', 'mb-4']:
                        wrapper = element
            keys = [i.string for i in wrapper.find_all('small')]
            values = [i.string for i in wrapper.find_all('div')]
            return Profile(keys, values)
      def getContractLinks(self):
            response = self.get(config.link + 'investor/investments')
            soup = BeautifulSoup(response.content , 'html.parser')
            links = []
            for tag in soup.find_all('a'):
                  if tag.find('i') and tag.get('href')[:len(config.link)+21] == config.link + 'investor/investments/':
                        links.append(tag.get('href')[46:])
            return links
      def download(self, link: str, filename: str):
            ensureDir(filename)
            response = self.get(link)
            io.open(filename, 'wb').write(response.content)
      def getContracts(self, dir: str=''):
            links = self.getContractLinks()
            for link in links:
                  self.download(config.link + 'investor/investments/' + link, dir + link + '.pdf')

if __name__ == '__main__':
      session = LandeSession(privateConfig.auth)
      session.getContracts(config.contractsFile)
      session.getProfile().to_json(config.profileFile % getDateString())
      ensureDir(config.transactionsFile % getDateString())
      session.getTransactions().to_csv(config.transactionsFile % getDateString(), index=False)
      ensureDir(config.investmentsFile % getDateString())
      session.getInvestments().to_csv(config.investmentsFile % getDateString(), index=False)
      session.close()