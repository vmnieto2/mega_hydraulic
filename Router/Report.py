from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.Reports import Report
from Schemas.report import Report as ReportSchema
from Middleware.jwt_bearer import JWTBearer

tools = Tools()
report_router = APIRouter()

@report_router.post('/reports/create_report', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def create_report(request: Request, report: ReportSchema):
    data = getattr(request.state, "json_data", {})
    response = Report().create_report(data)
    return response

@report_router.post('/reports/generate_report', tags=["Reports"], response_model=dict)
@http_decorator
def generate_report(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().generate_report(data)
    return response
