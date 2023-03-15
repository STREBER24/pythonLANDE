# pythonLANDE

This repo enables automated access to the P2P-loan plattform [LANDE](https://lande.finance) with python. This is usefull to download reports automated and to implement an costum autoinvest for the secondary market without the minimum of 250€ for the built-in autoinvest.

## Setup
To start the service change the values in ``src/config.py`` to your preferences and add a ``src/privateConfig.py`` with your login data like this:

> auth = {'email': 'test@test.test', 'password': 'SUPER_SECURE_PASSWORD'}

Then you can execute ``src/landeRequest.py``