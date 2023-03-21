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

        # logging threshold from 0 (errors) to 3 (verbose)
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
        self.autoinvestCollateral = ['land', 'financial', 'livestock', 'machinery', 'harvest', 'cattle']
