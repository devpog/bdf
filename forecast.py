import pandas as pd
import numpy as np


from core.database import *
from core.forecast import *


# define db
db = Database(name='bdf')

# define commodity
commodity = 'gold'

# pull gold and silver
data = db.get_commodity(commodity)
data.set_index('date', inplace=True)

forecast = Forecast(data['price'], 'rnn')


forecast.rnn()
forecast.fit()
print(forecast.predict())

forecast.horizon = 10
forecast.hidden = 10
forecast.fit()
print(forecast.fit_predict())

