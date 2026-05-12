import pandas as pd
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_tracker.app.query import get_conn


def co2_savings_ui() -> ui.TagList:
    """Build the CO2 Savings tab UI.

    Returns:
        ui.TagList: Layout containing the CO2 savings data table.
    """
    return ui.layout_columns(
        ui.card(
            ui.card_header("CO2 Savings by Country"),
            ui.output_data_frame("co2_table"),
        ),
        col_widths=[12],
    )


def co2_savings_server(input: Inputs, output: Outputs, session: Session) -> None:
    """Register reactive outputs for the CO2 Savings tab.

    Args:
        input: Shiny input values.
        output: Shiny output bindings.
        session: Shiny session object.
    """
    @calc
    def co2_data() -> pd.DataFrame:
        """Query CO2 savings data for all countries.

        Returns:
            pd.DataFrame: CO2 savings data with columns country_code,
                country_name, year_month, total_renewable_mwh, co2_avoided_tons,
                equivalent_cars_removed, equivalent_trees_planted.
        """
        conn = get_conn()
        try:
            return pd.read_sql_query(
                "SELECT country_code, country_name, year_month, "
                "total_renewable_mwh, co2_avoided_tons, "
                "equivalent_cars_removed, equivalent_trees_planted "
                "FROM gld_co2_savings_by_country "
                "ORDER BY year_month DESC, country_code",
                conn,
            )
        finally:
            conn.close()

    @render.data_frame
    def co2_table() -> render.DataGrid:
        """Render the CO2 savings data table.

        Returns:
            render.DataGrid: An interactive filtered data grid.
        """
        df = co2_data()
        return render.DataGrid(df, filters=True)
