import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import streamlit as st

# Random header stuff
st.title("Battery cycle data generator")
st.write("""
Welcome to the Battery cycle data generator web app! Generate your battery cycles easily here.

Created by [Alexandra Hernandez](https://alexavndra.github.io) at UC San Diego.
""")
st.subheader("How to use the app")
st.write("""
1. Upload battery cycle file by clicking the **Upload** button
2. Customize the configurations below (if you'd like)
3. Click the **Generate Visualization** button
4. Let the magic happen!
"""
)
st.subheader("Requirements from you")
st.write("""
- Make sure all columns are formatted properly
- You're uploading a .csv file (Can use Excel to do this or any online converter)

**NOTE**: Only works for battery data generated from Neware (as of right now)!
"""
)

# User configurations
st.header("Your configurations here")
battery_file = st.file_uploader(label="Upload your CSV here", type="csv")
if battery_file is None:
    st.error("Please upload a CSV file")
    st.stop()

cycles_to_generate = st.text_input(label="Type cycles to generate; leave empty to generate all", placeholder="Type in this format: 1,5,10")

plot_title = st.text_input(label="Type plot title here", placeholder="Example: Battery cycles", value="Battery cycles")

battery_df_file_name_input = st.text_input(label="Type what to name visualization here", placeholder="Example: battery-cycles", value="battery-viz")
battery_df_file_name = battery_df_file_name_input + ".png"

generate_button = st.button(label="Generate visualization", type="primary")

# Functions to reduce clutter
def drop_unwanted_cycles(battery_df, cycles_to_generate):
    if cycles_to_generate:
        cycles_str_vals = cycles_to_generate.split(",")
        cycles = [int(val) for val in cycles_str_vals]
        return battery_df[battery_df["Cycle ID"].isin(cycles)]
    return battery_df

def plotting_battery_cycle(charge, discharge, min_val, max_val, cycle_legend, color_range, plot_title):
    battery_cycle_viz = plt.figure(figsize=(15, 10), facecolor="white")
    i = 0

    for cycle_id, group in charge.groupby('Cycle ID'):
        plt.plot(group['Specific Capacity(mAh/g)'], group['Voltage(V)'], color = color_range[i], linewidth="1.5")
        i += 1
    
    i = 0

    for cycle_id, group in discharge.groupby('Cycle ID'):
        plt.plot(group['Specific Capacity(mAh/g)'], group['Voltage(V)'], color = color_range[i], linewidth="1.5")
        i += 1

    plt.title(plot_title)
    plt.xlabel("Specific Capacity(mAh/g)")
    plt.ylabel("Voltage(V)") 
    plt.ylim(min_val, max_val)
    plt.legend(cycle_legend,loc="lower right")
    plt.grid(visible=True)

    return battery_cycle_viz

# Plot generation here
if generate_button and battery_file:
    # Setup pre-plot
    battery_df = pd.read_csv(battery_file)

    # When there are args in cycles_to_generate   
    battery_df = drop_unwanted_cycles(battery_df, cycles_to_generate)

    number_of_colors = battery_df["Cycle ID"].nunique()
    color_range = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]

    cycle_numbers = battery_df["Cycle ID"].unique().tolist()
    cycle_legend = [] 

    for i in range(len(cycle_numbers)):
        cycle_legend.append("Cycle " + str(cycle_numbers[i]))

    # Plotting 
    charge = battery_df[battery_df["Current(mA)"] >= 0]
    discharge = battery_df[battery_df["Current(mA)"] < 0]
    min_val = battery_df["Voltage(V)"].min()
    max_val = battery_df["Voltage(V)"].max()

    battery_cycle_viz = plotting_battery_cycle(charge, discharge, min_val, max_val, cycle_legend, color_range, plot_title)
    st.pyplot(battery_cycle_viz)
