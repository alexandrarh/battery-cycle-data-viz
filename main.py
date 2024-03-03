import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import streamlit as st
from pathlib import Path

# Config for page
menu_items_page = {"Report a bug":"mailto:alexavndrarh@gmail.com","About":"This is version **1.0**"}
st.set_page_config(page_title="Battery Cycle Data Visualizer", page_icon="🔋",menu_items=menu_items_page)

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
- The file you give is either a .csv, .xls, or .xlsx file

**NOTE**: Only works for battery data generated from Neware (as of right now)!
"""
)

# User configurations
st.header("Your configurations here")
battery_file = st.file_uploader(label="Upload your CSV here", type=["csv", "xls", "xlsx"])
if battery_file is None:
    st.error("Please upload a CSV, XLS, or XLSX file")
    st.stop()

cycles_to_generate = st.text_input(label="Type cycles to generate; leave empty to generate all", placeholder="Type in this format: 1,5,10")

plot_title = st.text_input(label="Type plot title here", placeholder="Example: Battery cycles", value="Battery cycles")

battery_df_file_name_input = st.text_input(label="Type what to name visualization here", placeholder="Example: battery-cycles", value="battery-viz")
battery_df_file_name = battery_df_file_name_input + ".png"

generate_button = st.button(label="Generate visualization", type="primary")

'''

'''
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

def convert_df(df):
    return df.to_csv().encode('utf-8')

def standardize_df(battery_df):
    battery_df.columns = [
        "Data serial number", "Cycle ID", "Step ID", "Step number", "Step Type", "Time(hh:mm:ss)", "Total time(hh:mm:ss)",
        "Current(mA)", "Voltage(V)", "Capacity(mAh)", "Specific Capacity(mAh/g)", "Charge Cap.(mAh)", "Charging capacity(mAh/g)",
        "DChg cap.(mAh)", "Discharge specific capacity(mAh/g)", "Energy(Wh)", "Specific energy(mWh/g)", "Chg Eng.(Wh)",
        "Charge ratio energy(mWh/g)", "Discharge energy(Wh)",
        "Discharge specific energy(mWh/g)", "Real time","Power(W)"
        ]
    battery_df = battery_df.iloc[1:]
    battery_df.reindex()
    for column in battery_df.columns.to_list():
        if column == "Cycle ID":
            battery_df[column] = battery_df[column].astype(int)
        elif column == "Voltage(V)" or column == "Current(mA)" or column == "Specific Capacity(mAh/g)":
            battery_df[column] = battery_df[column].astype(float)
    return battery_df
        
# Plot generation here
if generate_button and battery_file:
    # Setup pre-plot
    # Create if-statement to evaluate what the file is (excel or csv)
    # If .xls, then run a function that converts it and standardizes it
    if battery_file.name.endswith(".csv"):
        battery_df = pd.read_csv(battery_file)
    elif battery_file.name.endswith(".xls") or battery_file.name.endswith(".xlsx"):
        battery_df = pd.read_excel(battery_file,sheet_name="Record")

    # When you need to standardize the columns
    if battery_df.columns.values[0] != "Data serial number":
        battery_df = standardize_df(battery_df)
    
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
    # img = plt.savefig(battery_df_file_name)
    st.pyplot(battery_cycle_viz)
    st.download_button(label="Download generated cycle data", data=convert_df(battery_df), file_name="generated-battery-df.csv")
    # st.download_button(label="Download generated visualization", data=img,file_name=battery_df_file_name)
