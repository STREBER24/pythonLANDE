import json
import io
import os

FILENAME = os.path.expanduser('~/.lande')

class Configuration:
    def __init__(self):
        # paths with %s being a loan info
        self.contractsFile = './data/contracts/contract-%s.pdf'
        self.loanFile = './data/loans/loan-%s.html'

        # paths with %s being a date string
        self.profileFile = './data/profiles/profile_%s.json'
        self.transactionsFile = './data/transactions/transactions_%s.csv'
        self.investmentsFile = './data/investments/investments_%s.csv'
        self.secondaryMarketFile = './data/secondary_market/secondary_market_%s.json'
        self.logFile = './logs/log_%s.txt'
        
        # can be daily (3), monthly (2), annual (1), never (0)
        self.newFileFrequency = 3

        # logging threshold from 0 (error) to 3 (verbose)
        self.loggingLevelPopup = 0
        self.loggingLevelFile = 2
        self.loggingLevelConsole = 3

        # base link
        self.link = 'https://lande.finance/'

        # autoinvest settings
        self.autoinvestEnabled = True
        self.autoinvestAmount = (5,20)
        self.autoinvestRemaining = (2, 36)
        self.autoinvestInterest = (11, None)
        self.autoinvestLtv = (None, 55)
        self.autoinvestStatus = ['current']
        self.autoinvestCollateral = ['land', 'financial', 'livestock', 'machinery', 'harvest']
        
    def save(self):
        data = {
            'contractsFile': self.contractsFile,
            'loanFile': self.loanFile,
            'profileFile': self.profileFile,
            'transactionsFile': self.transactionsFile,
            'investmentsFile': self.investmentsFile,
            'secondaryMarketFile': self.secondaryMarketFile,
            'logFile': self.logFile,
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
            'autoinvestCollateral': self.autoinvestCollateral}
        file = io.open(FILENAME, 'w', encoding='utf8')
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.close()
    
    def load(self):
        if not os.path.isfile(FILENAME):
            return False
        
        file = io.open(FILENAME, encoding='utf8')
        data: dict = json.load(file)
        file.close()
        
        self.contractsFile = data.get('contractsFile')
        self.loanFile = data.get('loanFile')
        self.profileFile = data.get('profileFile')
        self.transactionsFile = data.get('transactionsFile')
        self.investmentsFile = data.get('investmentsFile')
        self.secondaryMarketFile = data.get('secondaryMarketFile')
        self.logFile = data.get('logFile')
        self.loggingLevelPopup = data.get('loggingLevelPopup')
        self.loggingLevelFile = data.get('loggingLevelFile')
        self.loggingLevelConsole = data.get('loggingLevelConsole')
        self.link = data.get('link')
        self.autoinvestEnabled = data.get('autoinvestEnabled')
        self.autoinvestAmount = data.get('autoinvestAmount')
        self.autoinvestRemaining = data.get('autoinvestRemaining')
        self.autoinvestInterest = data.get('autoinvestInterest')
        self.autoinvestLtv = data.get('autoinvestLtv')
        self.autoinvestStatus = data.get('autoinvestStatus')
        self.autoinvestCollateral = data.get('autoinvestCollateral')
        return True
    
if __name__ == '__main__':
    config = Configuration()
    print(config.load())

