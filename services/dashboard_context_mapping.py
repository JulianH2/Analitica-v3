"""
Mapeo pathname -> screen_id y token_store_id para alimentar dashboard-context-store.
Cada pantalla que usa data_manager.dash_refresh_components(screen_id) sin prefix
tiene un token store con id f"{screen_id}__tok". Este módulo centraliza el mapeo
para el callback que actualiza el contexto del copilot.
"""
# pathname, screen_id, token_store_id (orden usado para State en el callback)
PATH_SCREEN_TOKEN = [
    ("/", "home", "home__tok"),
    ("/operational-dashboard", "operational-dashboard", "operational-dashboard__tok"),
    ("/administration-banks", "administration-banks", "administration-banks__tok"),
    ("/operational-costs", "operational-costs", "operational-costs__tok"),
    ("/workshop-purchases", "workshop-purchases", "workshop-purchases__tok"),
    ("/administration-receivables", "administration-receivables", "administration-receivables__tok"),
    ("/operational-performance", "operational-performance", "operational-performance__tok"),
    ("/administration-payables", "administration-payables", "administration-payables__tok"),
    ("/workshop-dashboard", "workshop-dashboard", "workshop-dashboard__tok"),
    ("/workshop-inventory", "workshop-inventory", "workshop-inventory__tok"),
    ("/operational-routes", "operational-routes", "operational-routes__tok"),
    ("/workshop-availability", "workshop-availability", "workshop-availability__tok"),
]

DEFAULT_TIMEZONE = "America/Mexico_City"
