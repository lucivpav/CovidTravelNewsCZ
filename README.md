# CovidTravelNewsCZ
Get notified in case of a change in international travel restrictions for Czech citizens.

This tool analyzes publicly available information from Ministry of Foreign Affairs of the Czech Republic related to Covid-19 restrictions for Czech Citizens in individual countries, as known to the Ministry and embassies of the Czech Republic across the globe.

Source of information: https://www.mzv.cz/jnp/cz/cestujeme/aktualni_doporuceni_a_varovani/x2020_04_25_rozcestnik_informaci_k_cestovani.html

## Usage

Get the state of latest updates of each country, this will generate `status.csv`:
```
python3 scraper.py
```

Check for recent updates (in the past 24 hours or in the past week), this will send an email to recepients defined in `mail_list.csv` in case of updates: 
```
python3 reporter.py -d # check for daily updates
python3 reporter.py -w # check for weekly updates
```

The `scraper.py` is intended to be run every 24 hours.
The `reporter.py` is intended to be run every 24 hours and every week.
