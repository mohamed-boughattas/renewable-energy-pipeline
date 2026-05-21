import duckdb
import polars as pl
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_tracker.config import get_settings


def comparison_ui() -> ui.TagList:
    return ui.layout_columns(
        ui.card(
            ui.card_header("Country Renewable Energy Ranking"),
            ui.output_data_frame("ranking_table"),
        ),
        col_widths=[12],
    )


def comparison_server(input: Inputs, output: Outputs, session: Session) -> None:
    @calc
    def ranking_data() -> pl.DataFrame:
        path = get_settings().duckdb_path
        con = duckdb.connect(path, read_only=True)
        try:
            q = """
                SELECT country_code, country_name, avg_renewable_share_pct,
                       total_production_gwh, total_renewable_gwh,
                       rank_renewable_share, rank_total_renewable
                FROM mart_country_renewable_ranking
                ORDER BY rank_renewable_share
            """
            return con.sql(q).pl()
        finally:
            con.close()

    @render.data_frame
    def ranking_table() -> render.DataGrid:
        df = ranking_data()
        return render.DataGrid(df.to_pandas(), filters=True)
