from datetime import date

import duckdb
import polars as pl
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_pipeline.config import get_settings

EMPTY_COLS = [
    "country_code", "country_name", "year_month",
    "renewable_share_pct", "total_production_gwh",
    "total_renewable_gwh", "total_fossil_gwh",
]


def timeseries_ui() -> ui.TagList:
    today = date.today()
    year_start = date(today.year - 1, 1, 1)
    year_end = date(today.year + 1, 12, 31)
    return ui.layout_columns(
        ui.card(
            ui.card_header("Filters"),
            ui.input_select(
                "ts_countries",
                "Countries",
                choices={
                    "DE": "Germany",
                    "FR": "France",
                    "ES": "Spain",
                    "DK": "Denmark",
                    "NO": "Norway",
                    "NL": "Netherlands",
                },
                selected=["DE", "FR"],
                multiple=True,
            ),
            ui.input_date_range(
                "ts_date_range",
                "Date Range",
                start=year_start.isoformat(),
                end=year_end.isoformat(),
            ),
        ),
        ui.card(
            ui.card_header("Monthly Renewable Share (%)"),
            ui.output_data_frame("ts_renewable_share_table"),
        ),
        col_widths=[4, 8],
    )


def timeseries_server(input: Inputs, output: Outputs, session: Session) -> None:
    @calc
    def timeseries_data() -> pl.DataFrame:
        countries = input.ts_countries()
        if not countries:
            return pl.DataFrame({col: [] for col in EMPTY_COLS})

        path = get_settings().duckdb_path
        con = duckdb.connect(path, read_only=True)
        try:
            country_list = ", ".join(f"'{c}'" for c in countries)
            q = f"""
                SELECT country_code, country_name, year_month,
                       renewable_share_pct, total_production_gwh,
                       total_renewable_gwh, total_fossil_gwh
                FROM mart_monthly_production_summary
                WHERE country_code IN ({country_list})
                ORDER BY year_month, country_code
            """
            return con.sql(q).pl()
        finally:
            con.close()

    @render.data_frame
    def ts_renewable_share_table() -> render.DataGrid:
        df = timeseries_data()
        return render.DataGrid(df.to_pandas(), filters=True)
