# pythonLANDE
This repo enables automated access to the P2P-loan plattform [LANDE](https://lande.finance) with python. This is usefull to download reports automated and to implement an costum autoinvest for the secondary market without the minimum of 250€ for the built-in autoinvest.

## Setup
Execute ``src/main.py`` or build an executable with

> pyinstaller --onefile --windowed src/main.py

On the first execution and on ever failed login attemt you should be requested to enter your credentials for LANDE. If this failed you can manually execute ``src/credentials.py``. Preferences are set to the values in ``src/config.py`` by default but stored in and loaded from ``~/.lande`` after the first execution and can be manipulated there.

## Versioning
Releases are named as ``X.Y.Z`` with *X* counting major updates, *Y* counting minor changes and *Z* counting bug fixes.

## Licence
The Software is published with the [MIT Licence](LICENCE.txt).