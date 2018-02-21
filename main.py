from core.commodity import *
from core.database import *

comm01 = Commodity(name='gold')
db01 = Database(name='bdf')

db01.add_records(comm01.data)
