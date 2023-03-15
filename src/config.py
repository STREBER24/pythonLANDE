from os.path import expanduser as path

# paths with %s being a loan info
contractsFile = path('~/Documents/Python/lande_reports/data/contracts/contract-%s.pdf')
loanFile = path('~/Documents/Python/lande_reports/data/loans/loan-%s.html')

# paths with %s being a date string
profileFile = path('~/Documents/Python/lande_reports/data/profiles/profile_%s.json')
transactionsFile = path('~/Documents/Python/lande_reports/data/transactions/transactions_%s.csv')
investmentsFile = path('~/Documents/Python/lande_reports/data/investments/investments_%s.csv')
secondaryMarketFile = path('~/Documents/Python/lande_reports/data/secondary_market/secondary_market_%s.json')
logFile = path('~/Documents/Python/lande_reports/logs/log_%s.txt')

# logging threshold from 0 (errors) to 3 (verbose)
loggingLevelPopup = 0
loggingLevelFile = 2
loggingLevelConsole = 3

# base link
link = 'https://lande.finance/'

# autoinvest settings
autoinvestEnabled = True
autoinvestAmount = (5,20)
autoinvestRemaining = (2, 36)
autoinvestInterest = (11, None)
autoinvestLtv = (None, 55)
autoinvestStatus = ['current']
autoinvestCollateral = ['land', 'financial', 'livestock', 'machinery', 'harvest']