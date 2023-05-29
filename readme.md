# Spikiest U.S. Baby Names by Decade

This Python script analyzes U.S. baby names data from the Social Security Administration and visualizes the "spikiest" names (those that show a significant increase followed by a decrease) by decade.

## Getting Started

### Prerequisites

To run this script, you need the following Python libraries:

- pandas
- plotly
- numpy
- PIL
- os
- time
- requests
- zipfile

You can install these using pip:

```bash
pip install pandas plotly numpy Pillow os time requests zipfile
```

### Downloading the Data

The script automatically downloads and extracts the required dataset from the Social Security Administration's website. The data is saved in a "data" folder at the same level as the script.

## Running the Script

You can run the script by simply executing the Python file:

```bash
python baby_names.py
```

By default, the script generates the "spikiest" names for each decade from 1960 to 2020. You can change these years by adjusting the values in the `main(1960, 2020)` line at the end of the script.

## Output

The script generates a series of plots, one for each decade, showing the names with the most significant "spikes" in popularity. These plots are saved as PNG files.

At the end of the script, all the generated images are combined into one large image called "combined.png".

## Acknowledgments

- The dataset used in this script is provided by the Social Security Administration.
