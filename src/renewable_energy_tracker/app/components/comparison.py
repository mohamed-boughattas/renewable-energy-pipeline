import pandas as pd
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_tracker.app.query import get_conn


def comparison_ui() -> ui.TagList:
    """Build the Country Comparison tab UI.

    Returns:
        ui.TagList: Layout containing the ranking data table.
    """
    return ui.layout_columns(
        ui.card(
            ui.card_header("Country Renewable Energy Ranking"),
            ui.output_data_frame("ranking_table"),
        ),
        col_widths=[12],
    )


def comparison_server(input: Inputs, output: Outputs, session: Session) -> None:
    """Register reactive outputs for the Country Comparison tab.

    Args:
        input: Shiny input values.
        output: Shiny output bindings.
        session: Shiny session object.
    """
    @calc
    def ranking_data() -> pd.DataFrame:
        """Query country renewable energy rankings.

        Returns:
            pd.DataFrame: Ranking data with columns country_code, country_name,
                avg_renewable_share_pct, total_production_mwh, total_renewable_mwh,
                rank_renewable_share, rank_total_renewable.
        """
        conn = get_conn()
        try:
            return pd.read_sql_query(
                "SELECT country_code, country_name, avg_renewable_share_pct, "
                "total_production_mwh, total_renewable_mwh, "
                "rank_renewable_share, rank_total_renewable "
                "FROM gld_country_renewable_ranking "
                "ORDER BY rank_renewable_share",
                conn,
            )
        finally:
            conn.close()

    @render.data_frame
    def ranking_table() -> render.DataGrid:
        """Render the country ranking data table.

        Returns:
            render.DataGrid: An interactive filtered data grid.
        """
        df = ranking_data()
        return render.DataGrid(df, filters=True)
