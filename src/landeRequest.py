from config import Configuration
from offer import Offer
import pandas as pd
import credentials
import requests
import json
import log
import bs4
import io


def saveJson(data, filename: str, config: Configuration):
      log.v(config, 'saving json to "%s" ...' % filename)
      log.ensureDir(config, filename)
      file = io.open(filename, 'w', encoding='utf-8')
      json.dump(data, file, indent=2, ensure_ascii=False)
      file.close()


class Profile():
      def __init__(self, config: Configuration, keys: list=[], values: list=[]):
            self.keys = keys
            self.values = values
            self.config = config
      def to_dict(self):
            return {key: value for key, value in zip(self.keys, self.values)}
      def to_json(self, filename: str):
            saveJson(self.to_dict(), filename, self.config)
      def to_csv(self, filename: str, sep: str=','):
            log.ensureDir(self.config, filename)
            file = io.open(filename, 'w', encoding='utf-8')
            file.write(sep.join([str(i) for i in self.keys]))
            file.write('\n')
            file.write(sep.join([str(i) for i in self.values]))
            file.close()
      def get(self, index):
            if len(self.values) > index:
                  return self.values[index]


class LandeSession(requests.Session):
      def __init__(self, config: Configuration, auth: dict=None):
            if auth == None:
                  auth = credentials.getCredentials(config)
            self.config = config
            self.authenticated = False
            log.i(self.config, 'initiating LandeSession ...')
            super().__init__()
            response = self.get(self.config.link + 'login')
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            for input in soup.find_all('input'):
                  if input.get('name') == '_token':
                        auth['_token'] = input.get('value')
            log.v(self.config, 'found token ' + str(auth['_token']))
            response = self.post(self.config.link + 'login', data=auth)
            if bs4.BeautifulSoup(response.content, 'html.parser').find('form', attrs={'action': 'https://lande.finance/logout'}) == None:
                  log.e(self.config, 'login failed')
            else:
                  self.authenticated = True
                  log.v(self.config, 'login finished')
      def getTransactions(self):
            log.i(self.config, 'fetching transaction export ...')
            response = self.get(self.config.link + 'investor/transactions/export')
            dataframe = pd.read_excel(response.content)
            log.v(self.config, 'fetching finished')
            return dataframe
      def getInvestments(self):
            log.i(self.config, 'fetching investments export ...')
            response = self.get(self.config.link + 'investor/reports/investments')
            dataframe = pd.read_excel(response.content)
            log.v(self.config, 'fetching finished')
            return dataframe
      def getProfile(self):
            log.i(self.config, 'fetching profile ...')
            response = self.get(self.config.link + 'settings/profile')
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            for element in soup.find_all('div'):
                  if element.get('class') == ['card', 'border-0', 'rounded-1', 'p-4', 'shadow-lg', 'mb-4']:
                        wrapper = element
            keys = [i.string for i in wrapper.find_all('small')]
            values = [i.string for i in wrapper.find_all('div')]
            log.v(self.config, 'fetching finished: found %d keys and %d values' % (len(keys), len(values)))
            if len(keys) != len(values): log.w(self.config, 'mismatch between keys and values of profile')
            return Profile(self.config, keys, values)
      def getContractLinks(self):
            log.i(self.config, 'fetching all contract links ...')
            response = self.get(self.config.link + 'investor/investments')
            soup = bs4.BeautifulSoup(response.content , 'html.parser')
            links = []
            for tag in soup.find_all('a'):
                  if tag.find('i') and tag.get('href')[:len(self.config.link)+21] == self.config.link + 'investor/investments/':
                        links.append(tag.get('href')[len(self.config.link)+21:])
            log.v(self.config, 'fetching finished: found %d links' % len(links))
            return links
      def download(self, link: str, filename: str):
            log.v(self.config, 'downloading file from %s' % link)
            log.ensureDir(self.config, filename)
            response = self.get(link)
            io.open(filename, 'wb').write(response.content)
      def downloadLoan(self, id: str, filePattern: str):
            log.i(self.config, 'downloading raw loan page %s' % id)
            self.download(self.config.link + 'loans/' + id, filePattern % id)
      def getContracts(self, filename: str=''):
            links = self.getContractLinks()
            log.i(self.config, 'downloading all contracts ...')
            for link in links:
                  self.download(self.config.link + 'investor/investments/' + link, filename % link)
      def purchase(self, buyLink: str, amount: float):
            response = self.get(buyLink)
            token = None
            for form in bs4.BeautifulSoup(response.content , 'html.parser').find_all('form'):
                  if form.get('action') == buyLink + '/purchase':
                        for i in form.find_all('input'):
                              if i.get('name') == '_token':
                                    token = i.get('value')
                        break
            if token == None:
                  log.e(self.config, 'no token on purchase form found')
            else:
                  log.i(self.config, 'sending amount of %.2f to %s ...' % (amount, buyLink + '/purchase'))
                  response = self.post(buyLink + '/purchase', data={'_token': token, 'amount': amount})
                  if response.ok: 
                        log.pop('Executed purchase.')
                        log.i(self.config, 'finished with status code %d' % response.status_code)
                  else:
                        log.e(self.config, 'failed with status code %d' % response.status_code)
      def getSecondaryMarketInfo(self):
            log.i(self.config, 'fetching secondary market info ...')
            newOffers = [None]
            offers: list[Offer] = []
            page = 1
            while len(newOffers) > 0:
                  log.v(self.config, 'loading page %d ...' % page)
                  response = self.get(self.config.link + 'investor/secondary-market', params={'page': page})
                  soup = bs4.BeautifulSoup(response.content , 'html.parser')
                  table = soup.find('table').find('tbody')
                  newOffers = [Offer(self.config).parseSecondary(i) for i in table.find_all('tr')]
                  offers += newOffers
                  page += 1
            log.v(self.config, 'fetching finished: found %d offers' % len(offers))
            return offers
      def getPrimaryMarketInfo(self, all=False):
            log.i(self.config, 'fetching primary market info ...')
            newOffers = [None]
            offers: list[Offer] = []
            page = 1
            while len(newOffers) > 0:
                  log.v(self.config, 'loading page %d ...' % page)
                  response = self.get(self.config.link + 'investor/loans', params={'page': page})
                  soup = bs4.BeautifulSoup(response.content , 'html.parser')
                  table = soup.find('table')
                  newOffers = [Offer(self.config).parsePrimary(i) for i in table.find_all('tr')[1:]]
                  if not all:
                        newOffers = list(filter(lambda x: x.status != None, newOffers))
                  offers += newOffers
                  page += 1
            log.v(self.config, 'fetching finished: found %d offers' % len(offers))
            return offers
      def autoinvest(self, offers: list[Offer], investments: pd.DataFrame, balance: float):
            if not self.config.autoinvestEnabled:
                  log.i(self.config, 'autoinvest is disabled')
                  return False
            if balance < self.config.autoinvestAmount[0]:
                  log.i(self.config, 'balance is below minimum autoinvest amount')
                  return False
            log.i(self.config, 'starting autoinvest ...')
            for i in offers:
                  if i.matchesAutoinvest():
                        amount = self.config.autoinvestAmount[1]
                        for j in investments.index:
                              if investments['ID'][j] == i.id:
                                    amount -= investments['Remaining Investment Amount'][j]
                        if amount > self.config.autoinvestAmount[0]:
                              self.downloadLoan(i.id, self.config.loanFile)
                              amount = min(amount, i.availableAmount, balance)
                              log.i(self.config, 'investing %.2f€ in loan %s ...' % (amount, i.id))
                              self.purchase(i.buyLink, amount)
                              return True
            log.v(self.config, 'autoinvest finished because no matching offer was found')
            return False
            

if __name__ == '__main__':
      config = Configuration()
      session = LandeSession(config)
      session.getPrimaryMarketInfo()
      session.close()
      