from pydantic import BaseModel

class Report(BaseModel):
    intervened_item: str
    activity_date: str
    client: str
    service_order: str
    solped: str
    person_receives: str
    buy_order: str
    description: str
    maintenance_types: list
    files: list
    user_id: int
