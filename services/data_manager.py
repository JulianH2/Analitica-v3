# services/data_manager.py
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from flask import session

from dashboard_core.query_builder import SmartQueryBuilder
from dashboard_core.db_helper import execute_dynamic_query
from services.real_data_service import RealDataService

Json = Dict[str, Any]
Path = List[Union[str, int]]


@dataclass
class CacheEntry:
    data: Json
    ts: float  # epoch seconds


class DataManager:
    """
    - Primer paint: devuelve estructura base (RealDataService.get_full_dashboard_data) recortada por pantalla.
    - Refresh (async): consulta BD solo KPIs definidos en SCREEN_MAP y los inyecta por path.
    - Cache: por (db_config + screen_id) con TTL.
    - Wiring Dash: helpers para generar dcc.Interval + dcc.Store y registrar callbacks estándar.
    """

    _instance: Optional["DataManager"] = None
    base_service: RealDataService
    qb: SmartQueryBuilder
    cache: Dict[str, CacheEntry]
    DEFAULT_TTL_SECONDS: int
    SCREEN_MAP: Dict[str, Dict[str, Any]]

    def __new__(cls) -> "DataManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.base_service = RealDataService()
            cls._instance.qb = SmartQueryBuilder()

            # cache_key -> CacheEntry
            cls._instance.cache = {}

            # TTL por defecto (segundos). Puedes sobreescribir por pantalla si quieres.
            cls._instance.DEFAULT_TTL_SECONDS = 30

            # Configuración de pantallas:
            # screen_id: {
            #   "section_key": "operaciones" | "administracion" | ...
            #   "ttl_seconds": int (opcional)
            #   "kpi_roadmap": ui_key -> kpi_id (SQL)
            #   "inject_paths": ui_key -> ["operaciones","dashboard","indicadores","viajes","valor"]
            # }
            cls._instance.SCREEN_MAP = {
                "admin-banks": {
                    "section_key": "administracion",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "admin-collection": {
                    "section_key": "administracion",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},     # luego lo llenas
                    "inject_paths": {},    # luego lo llenas
                },
                "admin-payables": {
                    "section_key": "administracion",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},     # luego lo llenas
                    "inject_paths": {},    # luego lo llenas
                },
                "home": {
                    "section_keys": ["operaciones", "mantenimiento", "administracion"],
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-costs": {
                    "section_key": "operaciones",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-dashboard": {
                    "section_keys": ["operaciones","mantenimiento","administracion"],
                    "ttl_seconds": 30,
                    "kpi_roadmap": {
                        "ingreso_viaje": "kpi_ingresos_brutos",
                        "viajes": "kpi_viajes_totales",
                        "kilometros": "kpi_kms_recorridos",
                    },
                    "inject_paths": {
                        "ingreso_viaje": [
                            "operaciones",
                            "dashboard",
                            "indicadores",
                            "ingreso_viaje",
                            "valor",
                        ],
                        "viajes": [
                            "operaciones",
                            "dashboard",
                            "indicadores",
                            "viajes",
                            "valor",
                        ],
                        "kilometros": [
                            "operaciones",
                            "dashboard",
                            "indicadores",
                            "kilometros",
                            "valor",
                        ],
                    },
                },
                "ops-performance": {
                    "section_key": "operaciones",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-routes": {
                    "section_key": "operaciones",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-availability": {
                    "section_key": "mantenimiento",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-dashboard": {
                    "section_key": "mantenimiento",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-inventory": {
                "section_key": "mantenimiento",
                "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-purchases": {
                    "section_key": "mantenimiento",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
            }
        return cls._instance

    # ---------------------------------------------------------------------
    # Cache keys / TTL
    # ---------------------------------------------------------------------

    def _db_fingerprint(self) -> str:
        """
        Deriva una huella estable desde session["current_db"].
        Si no existe, devuelve 'no-db' (para que el cache no reviente).
        """
        db_config = session.get("current_db")
        if not db_config:
            return "no-db"

        try:
            raw = json.dumps(db_config, sort_keys=True, default=str).encode("utf-8")
        except Exception:
            raw = str(db_config).encode("utf-8")

        return hashlib.sha256(raw).hexdigest()[:16]

    def _cache_key(self, screen_id: str) -> str:
        return f"{self._db_fingerprint()}::{screen_id}"

    def _ttl_for_screen(self, screen_id: str) -> int:
        cfg = self.SCREEN_MAP.get(screen_id, {})
        return int(cfg.get("ttl_seconds") or self.DEFAULT_TTL_SECONDS)

    def _is_fresh(self, entry: CacheEntry, ttl_seconds: int) -> bool:
        return (time.time() - entry.ts) <= ttl_seconds

    # ---------------------------------------------------------------------
    # Public API (sync) – para layout/callbacks normales
    # ---------------------------------------------------------------------

    def get_screen(
        self,
        screen_id: str,
        *,
        use_cache: bool = True,
        allow_stale: bool = True,
        force_base: bool = False,
    ) -> Json:
        """
        Devuelve SOLO el slice {"<section_key>": {...}} para screen_id.

        - use_cache=True: intenta devolver cache.
        - allow_stale=True: si está expirado, devuelve stale (y tú refrescas con Interval).
        - force_base=True: ignora cache y devuelve base recortada.
        """
        cfg = self.SCREEN_MAP.get(screen_id)
        if not cfg:
            return {}

        ttl = self._ttl_for_screen(screen_id)
        key = self._cache_key(screen_id)

        if not force_base and use_cache and key in self.cache:
            entry = self.cache[key]
            if self._is_fresh(entry, ttl):
                return entry.data
            if allow_stale:
                return entry.data

        # Base (mock/estructura rápida)
        base = self.base_service.get_full_dashboard_data()

        section_key = cfg.get("section_key")
        section_keys = cfg.get("section_keys")

        if section_keys:
            sliced = {k: base.get(k, {}) for k in section_keys}
        elif section_key:
            sliced = {section_key: base.get(section_key, {})}
        else:
            sliced = {}  # config inválida

        if use_cache:
            self.cache[key] = CacheEntry(data=sliced, ts=time.time())

        return sliced

    def clear_cache(self, screen_id: Optional[str] = None) -> None:
        """
        - screen_id=None: limpia todo el cache.
        - screen_id="ops-dashboard": limpia todas las entradas de ese screen para cualquier db_fingerprint.
        """
        if screen_id is None:
            self.cache = {}
            return

        suffix = f"::{screen_id}"
        self.cache = {k: v for k, v in self.cache.items() if not k.endswith(suffix)}

    # ---------------------------------------------------------------------
    # Refresh (async) – consulta BD / cache real por pantalla
    # ---------------------------------------------------------------------

    async def refresh_screen(self, screen_id: str, *, use_cache: bool = True) -> Json:
        """
        - Construye base slice.
        - Si hay session["current_db"], ejecuta SOLO KPIs definidos en kpi_roadmap.
        - Inyecta por inject_paths.
        - Actualiza cache (por db_fingerprint + screen_id).
        """
        cfg = self.SCREEN_MAP.get(screen_id)
        if not cfg:
            return {}

        kpi_roadmap: Dict[str, str] = cfg.get("kpi_roadmap", {})
        inject_paths: Dict[str, Path] = cfg.get("inject_paths", {})

        base = self.base_service.get_full_dashboard_data()
        section_key = cfg.get("section_key")
        section_keys = cfg.get("section_keys")

        if section_keys:
            data = {k: base.get(k, {}) for k in section_keys}
        elif section_key:
            data = {section_key: base.get(section_key, {})}
        else:
            return {}

        db_config = session.get("current_db")
        if not db_config:
            if use_cache:
                self.cache[self._cache_key(screen_id)] = CacheEntry(data=data, ts=time.time())
            return data

        for ui_key, kpi_id in kpi_roadmap.items():
            path = inject_paths.get(ui_key)
            if not path:
                continue

            build = self.qb.build_kpi_query(kpi_id)
            if not build or "query" not in build:
                continue

            rows = await execute_dynamic_query(db_config, build["query"])
            if not rows:
                continue

            value = list(rows[0].values())[0]
            self._set_path(data, path, value)

        if use_cache:
            self.cache[self._cache_key(screen_id)] = CacheEntry(data=data, ts=time.time())

        return data

    # ---------------------------------------------------------------------
    # Utilidad: set_path
    # ---------------------------------------------------------------------

    def _set_path(self, data: Json, path: Path, value: Any) -> None:
        """
        Inyecta `value` en `data` siguiendo `path`.
        Nota: soporta solo dict-paths (keys str). Si luego quieres índices int, se agrega.
        """
        cur: Any = data
        for key in path[:-1]:
            if not isinstance(key, str):
                raise ValueError("Paths con índices numéricos (int) no soportados aún")
            if key not in cur or not isinstance(cur[key], dict):
                cur[key] = {}
            cur = cur[key]

        last = path[-1]
        if not isinstance(last, str):
            raise ValueError("Last key numérica no soportada")
        cur[last] = value

    # ---------------------------------------------------------------------
    # Dash wiring helpers (para evitar duplicar Interval/Store/Callbacks)
    # ---------------------------------------------------------------------

    def dash_ids(self, screen_id: str, *, prefix: Optional[str] = None) -> Dict[str, str]:
        """
        IDs estandarizados por pantalla.
        `prefix` útil si quieres aislar IDs por page module.
        """
        base = f"{prefix}__{screen_id}" if prefix else screen_id
        return {
            "token_store": f"{base}__refresh_token",
            "auto_interval": f"{base}__auto_refresh",
            "status_text": f"{base}__refresh_status",
        }

    def dash_refresh_components(
        self,
        screen_id: str,
        *,
        interval_ms: int = 800,
        max_intervals: int = 1,
        prefix: Optional[str] = None,
        initial_token: int = 0,
    ) -> Tuple[List[Any], Dict[str, str]]:
        """
        Retorna ([dcc.Store, dcc.Interval], ids) listo para insertar en layout.
        Importa dcc de forma lazy para no acoplar demasiado el service.
        """
        from dash import dcc  # lazy import

        ids = self.dash_ids(screen_id, prefix=prefix)
        components = [
            dcc.Store(id=ids["token_store"], data=initial_token),
            dcc.Interval(
                id=ids["auto_interval"],
                interval=interval_ms,
                n_intervals=0,
                max_intervals=max_intervals,
            ),
        ]
        return components, ids

    def register_dash_refresh_callbacks(
        self,
        *,
        screen_id: str,
        body_output_id: str,
        render_body: Callable[[Json], Any],
        prefix: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Registra 2 callbacks:
        1) Interval -> (await refresh_screen) -> incrementa token
        2) token -> get_screen(use_cache=True) -> render_body(ctx)

        Uso típico en una page:
            refresh_bits, ids = data_manager.dash_refresh_components("ops-dashboard")
            data_manager.register_dash_refresh_callbacks(
                screen_id="ops-dashboard",
                body_output_id="ops-body",
                render_body=_render_ops_body
            )

        Requiere que en layout existan:
        - html.Div(id=body_output_id, ...)
        - los components devueltos por dash_refresh_components
        """
        import dash
        from dash import callback, Input, Output

        ids = self.dash_ids(screen_id, prefix=prefix)

        @callback(
            Output(ids["token_store"], "data"),
            Input(ids["auto_interval"], "n_intervals"),
            prevent_initial_call=False,
        )
        async def _auto_refresh(n_intervals: int) -> int:
            # refresca 1 vez al entrar (o según max_intervals)
            await self.refresh_screen(screen_id, use_cache=True)
            return int(n_intervals or 0)

        @callback(
            Output(body_output_id, "children"),
            Input(ids["token_store"], "data"),
        )
        def _rerender(_token: Any):
            ctx = self.get_screen(screen_id, use_cache=True, allow_stale=True)
            return render_body(ctx)

        return ids


data_manager = DataManager()
