import json
import io
import os

FILENAME = os.path.expanduser('~/.lande')
DEFAULT = {
    'contractsFile': './data/contracts/contract-%s.pdf',
    'loanFile': './data/loans/loan-%s.html',
    'profileFile': './data/profiles/profile_%s.json',
    'transactionsFile': './data/transactions/transactions_%s.csv',
    'investmentsFile': './data/investments/investments_%s.csv',
    'secondaryMarketFile': './data/secondary_market/secondary_market_%s.json',
    'primaryMarketFile': './data/primary_market/primary_market_%s.json',
    'logFile': './logs/log_%s.txt',
    'newFileFrequency': 3,
    'loggingLevelPopup': 1,
    'loggingLevelFile': 2,
    'loggingLevelConsole': 3,
    'link': 'https://lande.finance/',
    'autoinvestEnabled': True,
    'autoinvestAmount': (5,20),
    'autoinvestRemaining': (2, 36),
    'autoinvestInterest': (11, None),
    'autoinvestLtv': (None, 55),
    'autoinvestStatus': ['current'],
    'autoinvestCollateral': ['land', 'financial', 'livestock', 'machinery', 'harvest'],
    'checkUpdates': True}

class Configuration:
    def __init__(self):
        self.parse(DEFAULT)
        
    def save(self):
        data = {
            'contractsFile': self.contractsFile,
            'loanFile': self.loanFile,
            'profileFile': self.profileFile,
            'transactionsFile': self.transactionsFile,
            'investmentsFile': self.investmentsFile,
            'secondaryMarketFile': self.secondaryMarketFile,
            'primaryMarketFile': self.primaryMarketFile,
            'logFile': self.logFile,
            'newFileFrequency': self.newFileFrequency,
            'loggingLevelPopup': self.loggingLevelPopup,
            'loggingLevelFile': self.loggingLevelFile,
            'loggingLevelConsole': self.loggingLevelConsole,
            'link': self.link,
            'autoinvestEnabled': self.autoinvestEnabled,
            'autoinvestAmount': self.autoinvestAmount,
            'autoinvestRemaining': self.autoinvestRemaining,
            'autoinvestInterest': self.autoinvestInterest,
            'autoinvestLtv': self.autoinvestLtv,
            'autoinvestStatus': self.autoinvestStatus,
            'autoinvestCollateral': self.autoinvestCollateral,
            'checkUpdates': self.checkUpdates}
        file = io.open(FILENAME, 'w', encoding='utf8')
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.close()
        
    def load(self):
        if not os.path.isfile(FILENAME):
            return False
        
        file = io.open(FILENAME, encoding='utf8')
        data: dict = json.load(file)
        file.close()
        self.parse(data)
        return True
    
    def get(self, data: dict, key: str):
        value = data.get(key)
        if value == None:
            return DEFAULT.get(key)
        return value
    
    def parse(self, data: dict):
        self.contractsFile = self.get(data, 'contractsFile')
        self.loanFile = self.get(data, 'loanFile')
        self.profileFile = self.get(data, 'profileFile')
        self.transactionsFile = self.get(data, 'transactionsFile')
        self.investmentsFile = self.get(data, 'investmentsFile')
        self.secondaryMarketFile = self.get(data, 'secondaryMarketFile')
        self.primaryMarketFile = self.get(data, 'primaryMarketFile')
        self.logFile = self.get(data, 'logFile')
        self.newFileFrequency = self.get(data, 'newFileFrequency')
        self.loggingLevelPopup = self.get(data, 'loggingLevelPopup')
        self.loggingLevelFile = self.get(data, 'loggingLevelFile')
        self.loggingLevelConsole = self.get(data, 'loggingLevelConsole')
        self.link = self.get(data, 'link')
        self.autoinvestEnabled = self.get(data, 'autoinvestEnabled')
        self.autoinvestAmount = self.get(data, 'autoinvestAmount')
        self.autoinvestRemaining = self.get(data, 'autoinvestRemaining')
        self.autoinvestInterest = self.get(data, 'autoinvestInterest')
        self.autoinvestLtv = self.get(data, 'autoinvestLtv')
        self.autoinvestStatus = self.get(data, 'autoinvestStatus')
        self.autoinvestCollateral = self.get(data, 'autoinvestCollateral')
        self.checkUpdates = self.get(data, 'checkUpdates')

if __name__ == '__main__':
    config = Configuration()
    print(config.load())

