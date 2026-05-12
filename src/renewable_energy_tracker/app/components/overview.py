import pandas as pd
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_tracker.app.query import get_conn


def overview_ui() -> ui.TagList:
    """Build the Overview tab UI with KPI cards.

    Returns:
        ui.TagList: A row of four KPI card elements.
    """
    return ui.layout_columns(
        ui.card(
            ui.card_header("Total Renewable %"),
            ui.output_text("kpi_renewable_pct"),
        ),
        ui.card(
            ui.card_header("Total Renewable (MWh)"),
            ui.output_text("kpi_total_renewable"),
        ),
        ui.card(
            ui.card_header("Total Fossil (MWh)"),
            ui.output_text("kpi_total_fossil"),
        ),
        ui.card(
            ui.card_header("Total Nuclear (MWh)"),
            ui.output_text("kpi_total_nuclear"),
        ),
        col_widths=[3, 3, 3, 3],
    )


def overview_server(input: Inputs, output: Outputs, session: Session) -> None:
    """Register reactive outputs for the Overview tab.

    Args:
        input: Shiny input values.
        output: Shiny output bindings.
        session: Shiny session object.
    """
    @calc
    def kpi_data() -> dict[str, float]:
        """Query the latest monthly summary from the gold layer.

        Returns:
            dict[str, float]: Aggregated KPI values with keys
                renewable_pct, total_renewable, total_fossil, total_nuclear.
        """
        conn = get_conn()
        try:
            df = pd.read_sql_query(
                "SELECT * FROM gld_monthly_production_summary "
                "WHERE year_month = (SELECT MAX(year_month) FROM gld_monthly_production_summary)",
                conn,
            )
        finally:
            conn.close()
        if df.empty:
            return {"renewable_pct": 0, "total_renewable": 0, "total_fossil": 0, "total_nuclear": 0}
        return {
            "renewable_pct": df["renewable_share_pct"].mean(),
            "total_renewable": df["total_renewable_mwh"].sum(),
            "total_fossil": df["total_fossil_mwh"].sum(),
            "total_nuclear": df["total_nuclear_mwh"].sum(),
        }

    @render.text
    def kpi_renewable_pct() -> str:
        """Render the renewable percentage KPI.

        Returns:
            str: Formatted percentage string.
        """
        data = kpi_data()
        return f"{data['renewable_pct']:.1f}%"

    @render.text
    def kpi_total_renewable() -> str:
        """Render the total renewable MWh KPI.

        Returns:
            str: Formatted number string.
        """
        data = kpi_data()
        return f"{data['total_renewable']:,.0f}"

    @render.text
    def kpi_total_fossil() -> str:
        """Render the total fossil MWh KPI.

        Returns:
            str: Formatted number string.
        """
        data = kpi_data()
        return f"{data['total_fossil']:,.0f}"

    @render.text
    def kpi_total_nuclear() -> str:
        """Render the total nuclear MWh KPI.

        Returns:
            str: Formatted number string.
        """
        data = kpi_data()
        return f"{data['total_nuclear']:,.0f}"
