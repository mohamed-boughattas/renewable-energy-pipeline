import duckdb
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_tracker.config import get_settings


def overview_ui() -> ui.TagList:
    return ui.layout_columns(
        ui.card(
            ui.card_header("Total Renewable %"),
            ui.output_text("kpi_renewable_pct"),
        ),
        ui.card(
            ui.card_header("Total Renewable (GWh)"),
            ui.output_text("kpi_total_renewable"),
        ),
        ui.card(
            ui.card_header("Total Fossil (GWh)"),
            ui.output_text("kpi_total_fossil"),
        ),
        ui.card(
            ui.card_header("Total Nuclear (GWh)"),
            ui.output_text("kpi_total_nuclear"),
        ),
        col_widths=[3, 3, 3, 3],
    )


def overview_server(input: Inputs, output: Outputs, session: Session) -> None:
    @calc
    def kpi_data() -> dict[str, float]:
        path = get_settings().duckdb_path
        con = duckdb.connect(path, read_only=True)
        try:
            q = """
                SELECT * FROM mart_monthly_production_summary
                WHERE year_month = (SELECT MAX(year_month) FROM mart_monthly_production_summary)
            """
            df = con.sql(q).pl()
        finally:
            con.close()
        if df.is_empty():
            return {"renewable_pct": 0, "total_renewable": 0, "total_fossil": 0, "total_nuclear": 0}
        return {
            "renewable_pct": df["renewable_share_pct"].mean(),
            "total_renewable": df["total_renewable_gwh"].sum(),
            "total_fossil": df["total_fossil_gwh"].sum(),
            "total_nuclear": df["total_nuclear_gwh"].sum(),
        }

    @render.text
    def kpi_renewable_pct() -> str:
        data = kpi_data()
        return f"{data['renewable_pct']:.1f}%"

    @render.text
    def kpi_total_renewable() -> str:
        data = kpi_data()
        return f"{data['total_renewable']:,.0f}"

    @render.text
    def kpi_total_fossil() -> str:
        data = kpi_data()
        return f"{data['total_fossil']:,.0f}"

    @render.text
    def kpi_total_nuclear() -> str:
        data = kpi_data()
        return f"{data['total_nuclear']:,.0f}"