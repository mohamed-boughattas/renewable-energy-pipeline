from shiny import App, Inputs, Outputs, Session, ui

from renewable_energy_pipeline.app.components.co2_savings import (
    co2_savings_server,
    co2_savings_ui,
)
from renewable_energy_pipeline.app.components.comparison import (
    comparison_server,
    comparison_ui,
)
from renewable_energy_pipeline.app.components.overview import (
    overview_server,
    overview_ui,
)
from renewable_energy_pipeline.app.components.timeseries import (
    timeseries_server,
    timeseries_ui,
)

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Renewable Energy Pipeline"),
        ui.p("Global energy production monitoring"),
        ui.hr(),
        ui.p("Data source: Ember Climate API"),
    ),
    ui.navset_card_underline(
        ui.nav_panel("Overview", overview_ui()),
        ui.nav_panel("Time Series", timeseries_ui()),
        ui.nav_panel("Country Comparison", comparison_ui()),
        ui.nav_panel("CO2 Savings", co2_savings_ui()),
    ),
    title="Renewable Energy Pipeline",
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    overview_server(input, output, session)
    timeseries_server(input, output, session)
    comparison_server(input, output, session)
    co2_savings_server(input, output, session)


app = App(app_ui, server)
