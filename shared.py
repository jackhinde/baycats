import numpy as np
import pandas as pd
import re

def convert_google_sheet_url(url):
    # regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
    # replace function to construct the new URL for CSV export
    # if gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
    # replace using regex
    new_url = re.sub(pattern, replacement, url)
    return new_url

game_data_2024_url = 'https://docs.google.com/spreadsheets/d/1F8GBPtLhugdO0pqrJe3O9fMPOYv3AqVRq8ouUZWZxIY/edit#gid=0'
new_game_data_2024_url = convert_google_sheet_url(game_data_2024_url)
game_data_2024 = pd.read_csv(new_game_data_2024_url)

game_data_2023_url = 'https://docs.google.com/spreadsheets/d/1F8GBPtLhugdO0pqrJe3O9fMPOYv3AqVRq8ouUZWZxIY/edit#gid=256452955'
new_game_data_2023_url = convert_google_sheet_url(game_data_2023_url)
game_data_2023 = pd.read_csv(new_game_data_2023_url)