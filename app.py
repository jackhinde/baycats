import numpy as np
import pandas as pd

from shared import game_data_2024, game_data_2023
from shiny import App, reactive, req, ui
from shinywidgets import output_widget, render_plotly

# Define the app UI

game_data = game_data_2024

game_data['pitcher_team'] = game_data['home_team']
game_data.loc[game_data['inning_topbot'] == 'Bot', 'pitcher_team'] = game_data['away_team']
game_data['batter_team'] = game_data['away_team']
game_data.loc[game_data['inning_topbot'] == 'Bot', 'batter_team'] = game_data['home_team']

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize(
            'date_range',
            "Game Date",
            choices=game_data_2024['game_date'].values.tolist(),
            selected=game_data_2024['game_date'].values.tolist(),
            multiple=True
        ),
        ui.input_selectize(
            'pitcher_team',
            "Pitcher Team",
            choices=game_data_2024['pitcher_team'].values.tolist(),
            selected=game_data_2024['pitcher_team'].values.tolist(),
            multiple=True
        ),
        ui.input_selectize(
            'pitcher_name',
            "Pitcher Name",
            choices=game_data_2024['pitcher'].values.tolist(),
            selected=game_data_2024['pitcher'].values.tolist(),
            multiple=True
        ),
        ui.input_checkbox_group(
            'pitcher_throws',
            "Pitcher Throws",
            choices=['L', 'R'],
            selected=['L', 'R'],
            inline=True
        ),
        ui.input_selectize(
            'batter_team',
            "Batter Team",
            choices=game_data_2024['batter_team'].values.tolist(),
            selected=game_data_2024['batter_team'].values.tolist(),
            multiple=True
        ),
        ui.input_selectize(
            'batter_name',
            "Batter Name",
            choices=game_data_2024['batter'].values.tolist(),
            selected=game_data_2024['batter'].values.tolist(),
            multiple=True
        ),
        ui.input_checkbox_group(
            'batter_swings',
            "Batter Swings",
            choices=['L', 'R'],
            selected=['L', 'R'],
            inline=True
        )
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Strike Zone"),
            output_widget('strike_zone_plot'),
            ui.card_footer("Select the visible plot."),
            full_screen=True
        ),
        ui.card(
            ui.card_header("Field"),
            output_widget('field_plot'),
            ui.card_footer("Select the visible plot."),
            full_screen=True
        ),
        col_widths=(6, 6)
    )
)

def server(input, output, session):
    pass

app = App(app_ui, server)