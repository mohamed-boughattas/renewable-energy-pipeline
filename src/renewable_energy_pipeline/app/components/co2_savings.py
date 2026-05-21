import duckdb
import polars as pl
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_pipeline.config import get_settings


def co2_savings_ui() -> ui.TagList:
    return ui.layout_columns(
        ui.card(
            ui.card_header("CO2 Savings by Country"),
            ui.output_data_frame("co2_table"),
        ),
        col_widths=[12],
    )


def co2_savings_server(input: Inputs, output: Outputs, session: Session) -> None:
    @calc
    def co2_data() -> pl.DataFrame:
        path = get_settings().duckdb_path
        con = duckdb.connect(path, read_only=True)
        try:
            q = """
                SELECT country_code, country_name, year_month,
                       total_renewable_gwh, co2_avoided_tons,
                       equivalent_cars_removed, equivalent_trees_planted
                FROM mart_co2_savings_by_country
                ORDER BY year_month DESC, country_code
            """
            return con.sql(q).pl()
        finally:
            con.close()

    @render.data_frame
    def co2_table() -> render.DataGrid:
        df = co2_data()
        return render.DataGrid(df.to_pandas(), filters=True)
