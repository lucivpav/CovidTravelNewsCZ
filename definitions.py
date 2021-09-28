STATUS_FILE = 'status.csv'
MOST_RECENT_FILE = 'most_recent.csv'
MAIN_URL = 'https://www.mzv.cz/jnp/cz/cestujeme/aktualni_doporuceni_a_varovani/x2020_04_25_rozcestnik_informaci_k_cestovani.html'

class CountryData:
    def __init__(self, country, updateTime, updateTimestamp, link):
        self.country = country
        self.updateTime = updateTime # human readable
        self.updateTimestamp = updateTimestamp
        self.link = link

class MailData:
    def __init__(self, name, nameInHelloForm, email, daily, weekly):
        self.name = name
        self.nameInHelloForm = nameInHelloForm
        self.email = email
        self.daily = daily
        self.weekly = weekly