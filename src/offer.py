from config import Configuration
from datetime import datetime
from abc import ABC, abstractmethod
import requests
import log
import bs4
import re


def getLink(tag: bs4.Tag):
    a = tag.find('a')
    if isinstance(a, bs4.element.Tag): return str(a.get('href'))

class Offer(ABC):
    def __init__(self, config: Configuration):
        self.data: list[bs4.element.Tag] = []
        self.config = config
        self.id: str
        self.collateral: str
        self.remaining: int|None
        self.ltv = None
        self.availableAmount = None
        self.buyLink = None
        self.fullAmount = None
        self.status: str|None = None
        self.interest = None
        self.minimumInvest: int|None
        self.updates: list[dict] = []
        self.nextPayment = None
    def toDict(self):
        return {
            'id': self.id,
            'collateral': self.collateral,
            'interest': self.interest,
            'remaining': self.remaining,
            'ltv': self.ltv,
            'status': self.status,
            'updates': self.updates,
            'nextPayment': self.nextPayment,
            'amount': {
                'available': self.availableAmount,
                'full': self.fullAmount,
                'minimum': self.minimumInvest}}
    def parseInterest(self, text: str):
        if re.fullmatch('^[0-9]+%$', text): 
            return int(text[:-1])
        log.w(self.config, 'invalid interest: "%s"' % text)
    def parseRemaining(self, text: str):
        if re.fullmatch('^[0-9]+ m.$', text): 
            return int(text[:-3])
        log.w(self.config, 'invalid remaining terms: "%s"' % text)
    def parseLtv(self, text: str):
        if re.fullmatch('^[0-9]+%$', text): 
            return int(text[:-1])
        log.w(self.config, 'invalid ltv: "%s"' % text)
    def parseAmount(self, text: str):
        text = text.replace('€','').strip().lower()
        if re.fullmatch('^[0-9]+(,[0-9][0-9][0-9])*.[0-9][0-9]+$', text): 
            return float(text.replace(',',''))
        log.w(self.config, 'invalid amount: "%s"' % text)
    def parsePartialAmount(self, text: str):
        parts = text.split('/')
        if len(parts) != 2:
            log.w(self.config, 'invalid partial amount: "%s"' % text)
        funded = self.parseAmount(parts[0])
        full = self.parseAmount(parts[1])
        return (full-funded, full)
    def matchesAutoinvest(self):
        if self.config.autoinvestAmount[0] > self.availableAmount: return False
        if not matchRange(self.config.autoinvestNextPayment, self.nextPayment, allowNone=True): return False
        if not matchRange(self.config.autoinvestRemaining, self.remaining): return False
        if not matchRange(self.config.autoinvestInterest, self.interest): return False
        if not matchRange(self.config.autoinvestLtv, self.ltv): return False
        if self.status not in self.config.autoinvestStatus: return False
        if self.collateral not in self.config.autoinvestCollateral: return False
        if type(self.updates) is list and len(self.updates)>0 and not self.config.autoinvestAllowUpdates: return False
        if self.buyLink == None: return False
        return True 
    def parseWebsite(self, html):
        log.v(self.config, 'parsing loan file ...')
        soup = bs4.BeautifulSoup(html, 'html.parser')
        self.updates = []
        modal = soup.find('div', {'id': 'loanUpdate'})
        if isinstance(modal, bs4.element.Tag):
            div = modal.find('div', {'class': 'modal-body'})
            if isinstance(div, bs4.element.Tag):
                for date, text in zip(div.find_all('span', {'class': 'small'}), div.find_all('div')):
                    self.updates.append({'text': text.text.strip(), 'date': date.text.strip()})
        schedule = soup.find('div', {'id': 'schedule'})
        if not isinstance(schedule, bs4.element.Tag):
            log.w(self.config, f'no schedule found for offer with id {self.id}'); return
        payments = schedule.find_all('tbody')[-1].find_all('tr')
        self.nextPayment = None
        for i in payments:
            cells = i.find_all('td')
            date = datetime.strptime(cells[1].text.strip(), '%d.%m.%Y').toordinal() - datetime.now().toordinal()
            if cells[5].find('img') == None and (self.nextPayment == None or self.nextPayment > date):
                self.nextPayment = date
    @abstractmethod
    def buy(self, session: requests.Session, amount: float):
        raise NotImplementedError('Offer is an abstract class')


class SecondaryOffer(Offer):
    def __init__(self, config: Configuration, html: bs4.element.Tag):
        super().__init__(config)
        self.data = list(html.find_all('td'))
        self.id = self.data[2].text.strip().lower()
        self.collateral = self.data[3].text.strip().lower()
        self.interest = self.parseInterest(self.data[4].text.strip().lower())
        self.remaining = self.parseRemaining(self.data[5].text.strip().lower())
        self.ltv = self.parseLtv(self.data[6].text.strip().lower())
        self.status = self.data[7].text.strip().lower()
        self.availableAmount = self.parseAmount(self.data[8].text)
        self.buyLink = getLink(self.data[9])
        self.minimumInvest = 0
    def buy(self, session: requests.Session, amount: float):
        if self.buyLink is None:
            log.e(self.config, 'tried to buy offer without buyLink')
            return
        response = session.get(self.buyLink)
        token = None
        for form in bs4.BeautifulSoup(response.content , 'html.parser').find_all('form'):
            if form.get('action') == self.buyLink + '/purchase':
                for i in form.find_all('input'):
                    if i.get('name') == '_token':
                        token = i.get('value')
                    break
        if token == None:
            log.e(self.config, 'no token on purchase form found')
        else:
            log.i(self.config, 'sending amount of %.2f to %s ...' % (amount, self.buyLink + '/purchase'))
            response = session.post(self.buyLink + '/purchase', data={'_token': token, 'amount': amount})
            if response.ok: 
                log.pop(self.config, 'Executed purchase.')
                log.i(self.config, 'finished with status code %d' % response.status_code)
            else:
                log.e(self.config, 'failed with status code %d' % response.status_code)


class PrimaryOffer(Offer):
    def __init__(self, config: Configuration, html: bs4.element.Tag):
        super().__init__(config)
        self.data = list(html.find_all('td'))
        self.id = self.data[2].find('a').text.strip().lower()
        self.collateral = self.data[2].find('div').text.strip().lower()
        self.interest = self.parseInterest(self.data[4].text.strip().lower())
        self.remaining = self.parseRemaining(self.data[6].text.strip().lower())
        self.ltv = self.parseLtv(self.data[5].text.strip().lower())
        self.availableAmount, self.fullAmount = self.parsePartialAmount(self.data[3].text)
        self.buyLink = getLink(self.data[7])
        self.status = 'funding' if self.data[7].find('a').text.strip().lower()=='invest' else None
        self.minimumInvest = 50
    def buy(self, session: requests.Session, amount: float):
        response = session.get(self.config.link + 'loans/' + self.id)
        token = None
        investmentCount = None
        form = bs4.BeautifulSoup(response.content , 'html.parser').find('form', {'id': 'investment-form'})
        if not isinstance(form, bs4.element.Tag):
            log.e(self.config, 'no investment form found'); return
        for i in form.find_all('input'):
            if i.get('name') == '_token':
                token = i.get('value')
            elif i.get('name') == 'investment_count':
                investmentCount = i.get('value')
        if token == None:
            log.e(self.config, 'no token on purchase form found')
        elif investmentCount == None:
            log.e(self.config, 'no investmentCount on purchase form found')
        else:
            log.i(self.config, 'sending request to %s with id %s and amount %.2f to ...' % (self.config.link + '/investor/investments', self.id, amount))
            raise NotImplementedError
    

def matchRange(range: tuple[int|float|None, int|float|None], value: int|float|None, allowNone=False):
    if value is None:
        return allowNone
    left, right = range
    if left is not None and left > value:
        return False
    if right is not None and right < value:
        return False
    return True
