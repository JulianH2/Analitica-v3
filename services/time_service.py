from datetime import date, timedelta
import calendar
import datetime
from typing import Optional
from core.models.filters import DateFilter

class TimeService:

    @staticmethod
    def get_current_date() -> date:
        return date.today()
    
    @property
    def current_year(self):
        return datetime.date.today().year

    @property
    def previous_year(self):
        return datetime.date.today().year - 1

    @property
    def current_month_name(self):
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return meses[datetime.date.today().month - 1]

    @classmethod
    def resolve_filter(cls, date_filter: DateFilter) -> DateFilter:
        if date_filter.period == "custom":
            return date_filter

        today = cls.get_current_date()
        
        year = date_filter.year if date_filter.year else today.year
        month = date_filter.month if date_filter.month else today.month

        start_date: Optional[date] = None
        end_date: Optional[date] = None

        if date_filter.period == "ytd":
            start_date = date(year, 1, 1)
            if year == today.year:
                end_date = today
            else:
                end_date = date(year, 12, 31)

        elif date_filter.period == "mtd":
            start_date = date(year, month, 1)
            if year == today.year and month == today.month:
                end_date = today
            else:
                last_day = calendar.monthrange(year, month)[1]
                end_date = date(year, month, last_day)

        elif date_filter.period == "previous_year":
            prev_year = year - 1
            start_date = date(prev_year, 1, 1)
            end_date = date(prev_year, 12, 31)

        elif date_filter.period == "rolling_12":
            end_date = today
            start_date = today - timedelta(days=365)

        elif date_filter.period == "today":
            start_date = today
            end_date = today

        if start_date:
            date_filter.start_date = start_date
        if end_date:
            date_filter.end_date = end_date

        return date_filter