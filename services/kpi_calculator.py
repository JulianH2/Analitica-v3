from utils.helpers import format_value
from design_system import SemanticColors
import datetime
from services.time_service import TimeService

class KPICalculator:
    @staticmethod
    def calculate_kpi(
        title,
        current_value,
        previous_value=None,
        target_value=None,
        current_ytd_value=None,
        previous_ytd_value=None,
        kpi_type="currency", 
        unit="MXN",
        category="generic",
        description="",
        last_updated=None,
        inverse=False,
        metadata=None
    ):
        fmt_type = kpi_type
        ts = TimeService()
        
        if current_value is not None:
            value_formatted = format_value(current_value, "$" if unit == "MXN" else "", format_type=fmt_type)
        else:
            value_formatted = "---"
            current_value = 0
            
        if metadata is None:
            metadata = {}

        vs_prev_fmt = "---"
        vs_prev_delta = None
        vs_prev_delta_fmt = None
        trend = "neutral"
        label_prev_year = ""

        if previous_value is not None:
            label_prev_year = f"Vs {ts.previous_year}"
            if previous_value != 0:
                vs_prev_fmt = format_value(previous_value, "$" if unit == "MXN" else "", format_type=fmt_type)
                try:
                    delta = (current_value - previous_value) / previous_value
                    vs_prev_delta = delta
                    vs_prev_delta_fmt = f"{delta:+.1%}"
                    
                    if delta > 0.001: trend = "up"
                    elif delta < -0.001: trend = "down"
                except: pass

        target_fmt = "---"
        target_delta_fmt = None
        status = "neutral"
        status_color = SemanticColors.TEXT_MUTED 

        if target_value is not None and target_value != 0:
            target_fmt = format_value(target_value, "$" if unit == "MXN" else "", format_type=fmt_type)
            try:
                t_delta = (current_value - target_value) / target_value
                target_delta_fmt = f"{t_delta:+.1%}"

                diff = t_delta if not inverse else -t_delta
                
                if diff >= 0: 
                    status = "positive"
                    status_color = SemanticColors.SUCCESS
                elif diff >= -0.10: 
                    status = "warning"
                    status_color = SemanticColors.WARNING
                else:
                    status = "negative"
                    status_color = SemanticColors.DANGER
            except: pass

        ytd_fmt = "---"
        ytd_delta = None
        ytd_delta_fmt = None

        if current_ytd_value is not None:
             ytd_fmt = format_value(current_ytd_value, "$" if unit == "MXN" else "", format_type=fmt_type)
             
             if previous_ytd_value is not None and previous_ytd_value != 0:
                 try:
                     d_ytd = (current_ytd_value - previous_ytd_value) / previous_ytd_value
                     ytd_delta = d_ytd
                     ytd_delta_fmt = f"{d_ytd:+.1%}"
                 except: pass

        return {
            "title": title,
            "value": current_value,
            "value_formatted": value_formatted,
            "unit": unit,
            "vs_last_year_value": previous_value,
            "vs_last_year_formatted": vs_prev_fmt,
            "vs_last_year_delta": vs_prev_delta,
            "vs_last_year_delta_formatted": vs_prev_delta_fmt,
            "label_prev_year": label_prev_year,
            "target": target_value,
            "target_formatted": target_fmt,
            "target_delta_formatted": target_delta_fmt,
            
            "ytd_value": current_ytd_value,
            "ytd_formatted": ytd_fmt,
            "ytd_delta": ytd_delta,
            "ytd_delta_formatted": ytd_delta_fmt,
            
            "status": status,
            "status_color": status_color,
            "trend_direction": trend,
            "category": category,
            "type": kpi_type,
            "description": description,
            "last_updated": last_updated or datetime.datetime.now().isoformat(),
            "metadata": metadata
        }