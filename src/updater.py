from config import Configuration
import requests
import json
import log

URL = 'https://api.github.com/repos/STREBER24/pythonLANDE/releases/latest'
VERSION = 'v1.2.0'

def latest(config: Configuration):
    log.v(config, 'checking for updates ...')
    result = requests.get(URL)
    if not result.ok:
        log.w(config, 'failed to check for updates (status %d)' % result.status_code)
        return
    data = json.loads(result.text)
    if data.get('tag_name') == VERSION:
        return True
    log.w(config, 'this is not the latest version; check %s' % data.get('html_url'))
    return False

if __name__ == '__main__':
    print(latest(Configuration()))