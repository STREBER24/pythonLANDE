from bs4 import BeautifulSoup
import privateConfig
import pandas as pd
import requests
import config
import json
import log
import io

class Profile():
      def __init__(self, keys: list=[], values: list=[]):
            self.keys = keys
            self.values = values
      def to_dict(self):
            return {key: value for key, value in zip(self.keys, self.values)}
      def to_json(self, filename: str):
            log.ensureDir(filename)
            file = io.open(filename, 'w', encoding='utf-8')
            json.dump(self.to_dict(), file, indent=2, ensure_ascii=False)
            file.close()
      def to_csv(self, filename: str, sep: str=','):
            log.ensureDir(filename)
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
            log.i('initiating LandeSession ...')
            super().__init__()
            response = self.get(config.link + 'login')
            soup = BeautifulSoup( response.content , 'html.parser')
            for input in soup.find_all('input'):
                  if input.get('name') == '_token':
                        auth['_token'] = input.get('value')
            log.v('found token ' + str(auth['_token']))
            self.post(config.link + 'login', data=auth)
            log.v('login finished')
      def getTransactions(self):
            log.i('fetching transaction export ...')
            response = self.get(config.link + 'investor/transactions/export')
            dataframe = pd.read_excel(response.content)
            log.v('fetching finished')
            return dataframe
      def getInvestments(self):
            log.i('fetching investments export ...')
            response = self.get(config.link + 'investor/reports/investments')
            dataframe = pd.read_excel(response.content)
            log.v('fetching finished')
            return dataframe
      def getProfile(self):
            log.i('fetching profile ...')
            response = self.get(config.link + 'settings/profile')
            soup = BeautifulSoup( response.content , 'html.parser')
            for element in soup.find_all('div'):
                  if element.get('class') == ['card', 'border-0', 'rounded-1', 'p-4', 'shadow-lg', 'mb-4']:
                        wrapper = element
            keys = [i.string for i in wrapper.find_all('small')]
            values = [i.string for i in wrapper.find_all('div')]
            log.v('fetching finished: found %d keys and %d values' % (len(keys), len(values)))
            if len(keys) != len(values): log.w('mismatch between keys and values of profile')
            return Profile(keys, values)
      def getContractLinks(self):
            log.i('fetching all contract links ...')
            response = self.get(config.link + 'investor/investments')
            soup = BeautifulSoup(response.content , 'html.parser')
            links = []
            for tag in soup.find_all('a'):
                  if tag.find('i') and tag.get('href')[:len(config.link)+21] == config.link + 'investor/investments/':
                        links.append(tag.get('href')[46:])
            log.v('fetching finished: found %d links' % len(links))
            return links
      def download(self, link: str, filename: str):
            log.v('downloading file from %s' % link)
            log.ensureDir(filename)
            response = self.get(link)
            io.open(filename, 'wb').write(response.content)
      def getContracts(self, dir: str=''):
            links = self.getContractLinks()
            log.i('downloading all contracts ...')
            for link in links:
                  self.download(config.link + 'investor/investments/' + link, dir + link + '.pdf')

if __name__ == '__main__':
      date = log.getDateString()
      log.i('start main routine of "landeRequest.py"')
      session = LandeSession(privateConfig.auth)
      session.getContracts(config.contractsFile)
      session.getProfile().to_json(config.profileFile % date)
      log.ensureDir(config.transactionsFile % date)
      session.getTransactions().to_csv(config.transactionsFile % date, index=False)
      log.ensureDir(config.investmentsFile % date)
      session.getInvestments().to_csv(config.investmentsFile % date, index=False)
      session.close()
      log.i('finished main routine of "landeRequest.py"')