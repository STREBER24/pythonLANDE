# pythonLANDE

This repo enables automated access to the P2P-loan plattform [LANDE](https://lande.finance) with python. This is usefull to download reports automated and to implement an costum autoinvest for the secondary market without the minimum of 250€ for the built-in autoinvest.

## Setup
To start the service change the values in ``src/config.py`` to your preferences.
Then you can execute ``src/landeRequest.py`` or build an executable with

> pyinstaller --onefile --windowed src/landeRequest.py

On the first execution and on ever failed login attemt you should be requested to enter your credentials for LANDE. If this failed you can manually execute ``src/credentials.py``.