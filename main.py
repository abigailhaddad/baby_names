"""
Created on Sun May 28 21:25:15 2023

@author: abiga
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import time
import requests
import zipfile


def download_and_extract_data(url, folder_path):
    # Define paths
    zip_file_path = os.path.join(folder_path, 'names.zip')
    data_folder_path = os.path.join(folder_path, 'data')

    # Create data folder if it does not exist
    os.makedirs(data_folder_path, exist_ok=True)

    # Download the file
    r = requests.get(url)
    with open(zip_file_path, 'wb') as f:
        f.write(r.content)

    # Extract the file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(data_folder_path)

    # Remove the zip file
    os.remove(zip_file_path)



def read_and_combine_files(start_year, end_year):
    dataframes = []  # to store dataframes for each year
    # loop through each year
    for year in range(start_year, end_year + 1):
        file_name = f'../data/yob{year}.txt'  # construct the file name
        # read the file into a dataframe
        df = pd.read_csv(file_name, header=None, names=['Name', 'Sex', 'Count'])
        # add a column for the year
        df['Year'] = year
        # append the dataframe to the list
        dataframes.append(df)
    # concatenate all the dataframes together
    final_df = pd.concat(dataframes, ignore_index=True)
    return final_df


def get_full_for_spikes(spike_df, df):
    spike_names = spike_df[['Name', 'Sex']].drop_duplicates()
    filtered_df = pd.merge(df, spike_names, how='inner', on=['Name', 'Sex'])
    pivot_df = filtered_df.pivot_table(index=['Name', 'Sex'], columns='Year', values='Count')
    pivot_df.reset_index(inplace=True)
    return pivot_df


def plotly_line(pivot_df):
    colors = ['blue', 'green', 'purple', 'orange', 'red', 'pink', 'yellow', 'brown', 'cyan', 'magenta']
    traces = []
    for i in range(len(pivot_df)):
        traces.append(go.Scatter(
            x=pivot_df.columns[2:],  # years
            y=pivot_df.iloc[i, 2:],  # counts
            mode='lines+markers',  # add markers
            name=f"{pivot_df.iloc[i, 0]} ({pivot_df.iloc[i, 1]})",  # name (sex)
            line=dict(color=colors[i%len(colors)], shape='spline', width=2.5),  # smooth lines, and thicker width
        ))
    return traces


def find_spike(df):
    df = df.sort_values(by='Year')
    df['Prev_Year_Count'] = df.groupby(['Name', 'Sex'])['Count'].shift(1)
    df['Next_Year_Count'] = df.groupby(['Name', 'Sex'])['Count'].shift(-1)
    df['Increase'] = df['Count'] / df['Prev_Year_Count'] - 1
    df['Decrease'] = 1 - df['Next_Year_Count'] / df['Count']
    df['Abs_Increase'] = df['Count'] - df['Prev_Year_Count']
    df = df.replace([np.inf, -np.inf], np.nan)
    increase_threshold = .8 
    decrease_threshold = 0.3
    abs_increase_threshold = 500
    spike_df = df[(df['Increase'] > increase_threshold) 
                  & (df['Decrease'] > decrease_threshold)
                  & (df['Abs_Increase'] > abs_increase_threshold)]
    spike_df = spike_df.sort_values(by='Abs_Increase', ascending=False).head(3)
    return spike_df


def plot_decade(start_decade_year, end_decade_year, df):
    start_plot_year = start_decade_year - 1
    end_plot_year = min(start_decade_year + 10, df['Year'].max())  # adjust end year to account for missing data
    df_decade = df[(df['Year'] >= start_plot_year) & (df['Year'] <= end_plot_year)]
    spike_df = find_spike(df_decade)
    pivot_df = get_full_for_spikes(spike_df, df)
    year_cols = [col for col in pivot_df.columns[2:] if str(col).isdigit()]
    pivot_df = pivot_df.loc[:, ['Name', 'Sex'] + [col for col in year_cols if start_plot_year <= int(col) <= end_plot_year]]
    traces = plotly_line(pivot_df)
    fig = go.Figure()
    for trace in traces:
        fig.add_trace(trace)
    fig.update_layout(title=f"The {start_decade_year}s", xaxis_range=[start_plot_year, end_plot_year])
    fig_name = f"fig_{start_decade_year}.png"
    fig.update_layout(
        title=f"The {start_decade_year}s",
        xaxis_range=[start_plot_year, end_plot_year],
        font=dict(family="Arial"),
        margin=dict(t=40),
        height=300,
        yaxis=dict(tickprefix="\xa0\xa0\xa0\xa0\xa0"),  # Add space before y-axis labels
        title_x=.113,  # Align the title with the beginning of the y-axis
    )
    time.sleep(1)  # wait for the file to be written
    fig.write_image(fig_name)

    # Trim the image
    # Trim the image
    img = Image.open(fig_name)
    trimmed_img = trim_top_bottom(img, 0.00, 0.1)  # Adjust the percentages as desired
    trimmed_fig_name = f"trimmed_{fig_name}"
    trimmed_img.save(trimmed_fig_name)
    # Remove the original image
    os.remove(fig_name)
    return trimmed_fig_name

def trim_top_bottom(image, top_percentage, bottom_percentage):
    width, height = image.size
    new_height = height * (1 - top_percentage - bottom_percentage)
    top = int(height * top_percentage)
    image = image.crop((0, top, width, top + new_height))
    return image

def create_title_image(width, height, title_text, bg_color=(255, 255, 255), text_color=(0, 0, 0), font_path="arial.ttf"):
    img = Image.new('RGB', (width, height), color = bg_color)
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(font_path, 25)
    text_width, text_height = d.textsize(title_text, font=fnt)
    d.text(((width - text_width) // 2, (height - text_height) // 2), title_text, font=fnt, fill=text_color)
    return img

def combine_images(img_names):
    imgs = [Image.open(img_name) for img_name in img_names]
    min_img_width = min(img.width for img in imgs)
    # Create and add title image
    title_img = create_title_image(min_img_width, 50, "Spikiest U.S. Baby Names by Decade")
    imgs.insert(0, title_img)
    imgs = [img.resize((min_img_width, int(img.height * min_img_width / img.width)), Image.ANTIALIAS) for img in imgs]
    total_height = sum(img.height for img in imgs)
    combined_img = Image.new('RGB', (min_img_width, total_height))
    y_offset = 0
    for img in imgs:
        combined_img.paste(img, (0, y_offset))
        y_offset += img.height
    combined_img.save('combined.png')

def main(start_year, end_year):
    df = read_and_combine_files(start_year - 1, end_year + 1)  # Adjusted to include the year before and after the decades
    img_names = []
    for start_decade_year in range(start_year, end_year + 1, 10):
        if start_decade_year + 10 <= end_year:
            img_names.append(plot_decade(start_decade_year, start_decade_year + 10, df))
    combine_images(img_names)

if __name__ == '__main__':
    download_and_extract_data('https://www.ssa.gov/oact/babynames/names.zip', '..')
    main(1960, 2020)  # Change the years here


