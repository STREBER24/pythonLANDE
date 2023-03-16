import keyring.util.platform_ as keyring_platform
import keyring
import getpass
import log


MAIL = 'EMAIL'
PSWD = 'PASSWORD'
NAMESPACE = 'LANDE-AutoInvest'


def saveCredentials():
    log.i('prompting for user credentials ...')
    keyring.set_password(NAMESPACE, MAIL, input('Mail: '))
    keyring.set_password(NAMESPACE, PSWD, getpass.getpass())
    log.i('saved credentials to %s' % keyring_platform.config_root())


def getCredentials():
    log.i('loading credentials ...')
    mail = keyring.get_password(NAMESPACE, MAIL)
    pswd = keyring.get_password(NAMESPACE, PSWD)
    if mail in [None, ''] or pswd in [None, '']:
        log.w('loading credentials retuned null')
        saveCredentials()
        return getCredentials()
    return {'email': mail, 'password': pswd}


if __name__ == '__main__':
    saveCredentials()