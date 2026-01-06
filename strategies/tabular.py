import dash_mantine_components as dmc
from services.data_manager import DataManager

data_manager = DataManager()

class MainTableStrategy:
    def get_table_data(self):
        df = data_manager.service.get_main_dashboard_table()
        return df

    def render(self):
        df = self.get_table_data()
        header = dmc.TableThead(dmc.TableTr([
            dmc.TableTh("Indicator"), dmc.TableTh("Current Value"), dmc.TableTh("Target"), dmc.TableTh("vs 2024"), dmc.TableTh("Var %")
        ]))
        rows = []
        for _, row in df.iterrows():
            rows.append(dmc.TableTr([
                dmc.TableTd(row["Indicador"], fw="normal"),
                dmc.TableTd(str(row["Valor Actual"]), fw="bold", c="blue"),
                dmc.TableTd(str(row["Meta"])),
                dmc.TableTd(str(row["vs. 2024"])),
                dmc.TableTd(str(row["YTD/Variación"]))
            ]))
        return dmc.Table([header, dmc.TableTbody(rows)], striped="odd", highlightOnHover=True, withTableBorder=True)

class OpsUnitTableStrategy:
    def render(self):
        ops_data = data_manager.service.get_ops_income_data()
        unidades = ops_data.get("tablas", {}).get("unidades", [])

        header = dmc.TableThead(
            dmc.TableTr([
                dmc.TableTh("Eco Unit"),
                dmc.TableTh("Loaded Kms"),
                dmc.TableTh("Empty Kms"),
                dmc.TableTh("Total Kms"),
                dmc.TableTh("Status")
            ])
        )

        rows = []
        for u in unidades:
            loaded = u.get("kms_cargados", 0)
            empty = u.get("kms_vacios", 0)
            total = u.get("kms_totales", 0)
            
            is_efficient = empty == 0 or (loaded / (loaded + empty) > 0.8)
            
            rows.append(dmc.TableTr([
                dmc.TableTd(dmc.Badge(u.get("unidad", "N/A"), variant="outline", color="gray")),
                dmc.TableTd(f"{loaded:,.0f}", c="blue", fw="normal"),
                dmc.TableTd(
                    f"{empty:,.0f}", 
                    style={"color": "var(--mantine-color-orange-filled)" if empty > 0 else "var(--mantine-color-dimmed)"}
                ),
                dmc.TableTd(f"{total:,.0f}", fw="bold"),
                dmc.TableTd(
                    dmc.Badge("Optimal", color="green") if is_efficient else dmc.Badge("Review", color="red")
                )
            ]))

        return dmc.Table(
            [header, dmc.TableTbody(rows)],
            striped="odd", 
            highlightOnHover=True, 
            withTableBorder=True,
            verticalSpacing="sm"
        )