from config import Configuration
import landeRequest as request
import credentials
import log

if __name__ == '__main__':
      config = Configuration()
      if not config.load(): 
            config.autoinvestEnabled = log.confirm('Enable AutoInvest?')
            config.save()
      
      log.i(config, 'start main routine')
      session = request.LandeSession(config)
      date = log.getTimeString(config)
      
      while not session.authenticated:
            credentials.saveCredentials()
            session = request.LandeSession(config)
      
      invest = True
      while invest:
            profile = session.getProfile()
            balance = float(profile.to_dict().get('Balance').replace('€',''))
            transactions = session.getTransactions()
            investments = session.getInvestments()
            offers = session.getSecondaryMarketInfo()
            invest = session.autoinvest(offers, investments, balance)
            
      log.ensureDir(config.investmentsFile % date)   
      log.ensureDir(config.transactionsFile % date) 
      transactions.to_csv(config.transactionsFile % date, index=False)
      investments.to_csv(config.investmentsFile % date, index=False)
      profile.to_json(config.profileFile % date)
      session.getContracts(config.contractsFile)
      request.saveJson([i.to_dict() for i in offers], config.secondaryMarketFile % date, config)
                        
      session.close()
      log.i(config, 'finished main routine')
      log.pop('Executed LANDE AutoInvest sucessfully.')