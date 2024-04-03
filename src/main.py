from config import Configuration, FILENAME
import landeRequest as request
import credentials
import traceback
import updater
import log

def run(config: Configuration):
      if not config.load(): 
            config.autoinvestEnabled = log.confirm(config, 'Enable AutoInvest?')
            config.save()
            log.pop(config, 'saved config to %s' % FILENAME)
      
      if config.checkUpdates:
            updater.latest(config)
      
      log.i(config, 'start main routine')
      session = request.LandeSession(config)
      date = log.getTimeString(config)
      
      while not session.authenticated:
            credentials.saveCredentials(config)
            session = request.LandeSession(config)
      
      invest = True
      while invest:
            profile = session.getProfile()
            balance = float(profile.to_dict().get('Balance').replace('€',''))
            transactions = session.getTransactions()
            investments = session.getInvestments()
            primaryOffers = session.getPrimaryMarketInfo()
            secondaryOffers = session.getSecondaryMarketInfo()
            invest = session.autoinvest(secondaryOffers, investments, balance)
            
      log.ensureDir(config, config.investmentsFile % date)   
      log.ensureDir(config, config.transactionsFile % date) 
      transactions.to_csv(config.transactionsFile % date, index=False)
      investments.to_csv(config.investmentsFile % date, index=False)
      profile.to_json(config.profileFile % date)
      session.getContracts(config.contractsFile)
      request.saveJson([i.toDict() for i in primaryOffers], config.primaryMarketFile % date, config)
      request.saveJson([i.toDict() for i in secondaryOffers], config.secondaryMarketFile % date, config)
                 
      session.logout()       
      session.close()
      log.i(config, 'finished main routine')
      log.pop(config, 'Executed LANDE AutoInvest sucessfully.')
      
if __name__ == '__main__':
      try:
            config = Configuration()
            run(config)
      except Exception as e:
            log.e(config, traceback.format_exc())
