import keyring.util.platform_ as keyring_platform
from config import Configuration
import tkinter as tk
import keyring
import log


MAIL = 'EMAIL'
PSWD = 'PASSWORD'
NAMESPACE = 'LANDE-AutoInvest'


def saveCredentials(config: Configuration):
    log.i(config, 'prompting for user credentials ...')
    root = tk.Tk()
    root.title('LANDE Credentials')
    tk.Label(root, text='E-Mail:').grid(row=0, column=0, pady=2)
    tk.Label(root, text='Password:').grid(row=1, column=0, pady=2)
    mail = tk.Entry(root)
    mail.grid(row=0, column=1, pady=2)
    pswd = tk.Entry(root, show='*')
    pswd.grid(row=1, column=1, pady=2)
    def submit():
        storeCredentials(mail.get(), pswd.get())
        root.destroy()
    tk.Button(root, text='Save', command=submit).grid(row=2, column=0, pady=2, columnspan=2)
    root.mainloop()


def storeCredentials(mail: str, pswd: str):
    keyring.set_password(NAMESPACE, MAIL, mail)
    keyring.set_password(NAMESPACE, PSWD, pswd)
    log.i('saved credentials to %s' % keyring_platform.config_root())
    


def getCredentials(config: Configuration):
    log.i(config, 'loading credentials ...')
    mail = keyring.get_password(NAMESPACE, MAIL)
    pswd = keyring.get_password(NAMESPACE, PSWD)
    if mail in [None, ''] or pswd in [None, '']:
        log.w('loading credentials retuned null')
        saveCredentials()
        return getCredentials()
    return {'email': mail, 'password': pswd}


if __name__ == '__main__':
    saveCredentials(Configuration())