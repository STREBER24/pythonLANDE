import privateConfig
import pandas as pd
import requests
import config
import json
import log
import bs4
import io
import re

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
       
       
class SecondaryOffer():
      def __init__(self):
            self.data: list[bs4.element.Tag] = []
      def parse(self, html: bs4.element.Tag):
            self.data = list(html.find_all('td'))
            return self
      def id(self):
            return self.data[2].text.strip().lower()
      def collateral(self):
            return self.data[3].text.strip().lower()
      def interest(self):
            text = self.data[4].text.strip().lower()
            if not re.fullmatch('^[0-9]+%$', text): log.w('invalid interest: "%s"' % text)
            return int(text[:-1])
      def remaining(self):
            text = self.data[5].text.strip().lower()
            if not re.fullmatch('^[0-9]+ m.$', text): log.w('invalid remaining terms: "%s"' % text)
            return int(text[:-3])
      def ltv(self):
            text = self.data[6].text.strip().lower()
            if not re.fullmatch('^[0-9]+%$', text): log.w('invalid ltv: "%s"' % text)
            return int(text[:-1])
      def status(self):
            return self.data[7].text.strip().lower()
      def amount(self):
            text = self.data[8].text.strip().lower()
            if not re.fullmatch('^€[0-9]+(,[0-9][0-9][0-9])*.[0-9][0-9]+$', text): log.w('invalid amount: "%s"' % text)
            return float(text[1:].replace(',',''))
      def buyLink(self):
            return str(self.data[9].find('a').get('href'))
      def to_text_list(self):
            return [i.text.strip().lower() for i in self.data]
      def to_json(self, filename: str):
            log.ensureDir(filename)
            file = io.open(filename, 'w', encoding='utf-8')
            json.dump(self.to_dict(), file, indent=2, ensure_ascii=False)
            file.close()
      def to_dict(self):
            return {'id': self.id(),
                    'collateral': self.collateral(),
                    'interest': self.interest(),
                    'remaining': self.remaining(),
                    'ltv': self.ltv(),
                    'status': self.status(),
                    'amount': self.amount(),
                    'buyLink': self.buyLink()}


class LandeSession(requests.Session):
      def __init__(self, auth: dict):
            log.i('initiating LandeSession ...')
            super().__init__()
            response = self.get(config.link + 'login')
            soup = bs4.BeautifulSoup(response.content , 'html.parser')
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
            soup = bs4.BeautifulSoup(response.content , 'html.parser')
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
            soup = bs4.BeautifulSoup(response.content , 'html.parser')
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
      def downloadLoan(self, id: str, filePattern: str):
            self.download(config.link + 'loans/' + id, filePattern % id)
      def getContracts(self, filename: str=''):
            links = self.getContractLinks()
            log.i('downloading all contracts ...')
            for link in links:
                  self.download(config.link + 'investor/investments/' + link, filename % link)
      def getSecondaryMarketInfo(self):
            log.i('fetching secondary market info ...')
            newOffers = [None]
            offers: list[SecondaryOffer] = []
            page = 1
            while len(newOffers) > 0:
                  log.v('loading page %d ...' % page)
                  response = self.get(config.link + 'investor/secondary-market', params={'page': page})
                  soup = bs4.BeautifulSoup(response.content , 'html.parser')
                  table = soup.find('table').find('tbody')
                  newOffers = [SecondaryOffer().parse(i) for i in table.find_all('tr')]
                  offers += newOffers
                  page += 1
            log.v('fetching finished: found %d offers' % len(offers))
            return offers
      def saveSecondaryMarketInfo(self, filename: str):
            offers = [i.to_dict() for i in self.getSecondaryMarketInfo()]
            log.ensureDir(filename)
            file = io.open(filename, 'w', encoding='utf-8')
            json.dump(offers, file, indent=2, ensure_ascii=False)
            file.close()
            log.v('saving offers finished')

if __name__ == '__main__':
      date = log.getDateString()
      log.i('start main routine of "landeRequest.py"')
      session = LandeSession(privateConfig.auth)
      session.saveSecondaryMarketInfo(config.secondaryMarketFile % date)
      session.getContracts(config.contractsFile)
      session.getProfile().to_json(config.profileFile % date)
      log.ensureDir(config.transactionsFile % date)
      session.getTransactions().to_csv(config.transactionsFile % date, index=False)
      log.ensureDir(config.investmentsFile % date)
      session.getInvestments().to_csv(config.investmentsFile % date, index=False)
      session.downloadLoan('230220-510996', config.loanFile)
      session.close()
      log.i('finished main routine of "landeRequest.py"')