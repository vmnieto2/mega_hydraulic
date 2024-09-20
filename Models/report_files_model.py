from Config.db import BASE
from sqlalchemy import Column, BigInteger, Text, Integer, DateTime
from datetime import datetime

class ReportFilesModel(BASE):

    __tablename__= "report_files"
    
    id = Column(BigInteger, primary_key=True)
    id_report = Column(BigInteger, nullable=False)
    path = Column(Text)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.id_report = data['id_report']
        self.path = data['path']
