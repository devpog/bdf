from core.commodity import *
from core.database import *

commodity = 'gold'

comm01 = Commodity(name=commodity)
db01 = Database(name='bdf')
# db01.populate_records(comm01.data)

print(len(db01.add_records(comm01.data, commodity)))



