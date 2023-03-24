from config import Configuration
import log
import bs4
import re


class Offer():
    def __init__(self, config: Configuration):
        self.data: list[bs4.element.Tag] = []
        self.config = config
        self.id = None
        self.collateral = None
        self.remaining = None
        self.ltv = None
        self.amount = None
        self.buyLink = None
    def parseSecondary(self, html: bs4.element.Tag):
        self.data = list(html.find_all('td'))
        self.id = self.data[2].text.strip().lower()
        self.collateral = self.data[3].text.strip().lower()
        self.interest = self.parseInterest(self.data[4].text.strip().lower())
        self.remaining = self.parseRemaining(self.data[5].text.strip().lower())
        self.ltv = self.parseLtv(self.data[6].text.strip().lower())
        self.status = self.data[7].text.strip().lower()
        self.amount = self.data[8].text.strip().lower()
        self.buyLink = str(self.data[9].find('a').get('href'))
        return self
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
        if re.fullmatch('^€[0-9]+(,[0-9][0-9][0-9])*.[0-9][0-9]+$', text): 
            return float(text[1:].replace(',',''))
        log.w(self.config, 'invalid amount: "%s"' % text)
    def matchesAutoinvest(self):
        if self.config.autoinvestAmount[0] > self.amount: return False
        if not matchRange(self.config.autoinvestRemaining, self.remaining): return False
        if not matchRange(self.config.autoinvestInterest, self.interest): return False
        if not matchRange(self.config.autoinvestLtv, self.ltv): return False
        if self.status not in self.config.autoinvestStatus: return False
        if self.collateral not in self.config.autoinvestCollateral: return False
        return True       
    def to_text_list(self):
        return [i.text.strip().lower() for i in self.data]
    def to_dict(self):
        return {'id': self.id,
                'collateral': self.collateral,
                'interest': self.interest,
                'remaining': self.remaining,
                'ltv': self.ltv,
                'status': self.status,
                'amount': self.amount,
                'buyLink': self.buyLink}
    

def matchRange(range: tuple[int|float|None, int|float|None], value: int|float):
      if range[0] != None and range[0] > value:
            return False
      if range[1] != None and range[1] < value:
            return False
      return True
