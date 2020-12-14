import glassdoor_scraper as gs
import pandas as pd

driver_path = "/usr/bin/chromedriver"

df = gs.get_jobs('data scientist', 15, True, driver_path, 5)

print(df)
