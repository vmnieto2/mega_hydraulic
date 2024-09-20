from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, Text
from datetime import datetime

class ReportModel(BASE):

    __tablename__= "reports"
    
    id = Column(BigInteger, primary_key=True)
    intervened_item = Column(Text)
    activity_date = Column(DateTime, nullable=False)
    client = Column(String, nullable=False)
    service_order = Column(String, nullable=False)
    solped = Column(String, nullable=False)
    person_receives = Column(String, nullable=False)
    buy_order = Column(String, nullable=False)
    description = Column(Text)
    user_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.intervened_item = data['intervened_item']
        self.activity_date = data['activity_date']
        self.client = data['client']
        self.service_order = data['service_order']
        self.solped = data['solped']
        self.person_receives = data['person_receives']
        self.buy_order = data['buy_order']
        self.description = data['description']
        self.user_id = data['user_id']
