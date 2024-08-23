import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import streamlit as st

# Config for page
menu_items_page = {"Report a bug":"mailto:alexavndrarh@gmail.com"}
st.set_page_config(page_title="Battery Cycle Data Visualizer", page_icon="🔋",menu_items=menu_items_page)

# Header stuff
st.title("Battery cycle visualizer")
st.write("""
Welcome to the Battery cycle data generator web app! Generate your battery cycles easily here.
**Compatible with Neware and Agitrbin-generated data files!**

Created by [Alexandra Hernandez](https://alexandrarh.com) at UC San Diego.
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
    - Please make sure that if your file is a **Neware** file, there are 23 columns; do not alter column order and/or amount before using
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

length = st.slider("Adjust the length of your visualization", 0, 50, 15)
width = st.slider("Adjust the width of your visualization", 0, 50, 10)

generate_button = st.button(label="Generate visualization", type="primary")

# Functions to help generate the visualization + creating the specific battery cycle range .csv
# Drops unwanted cycles (based on what theuser wants to generate)
def drop_unwanted_cycles(battery_df, cycles_to_generate):
    if cycles_to_generate:
        cycles_str_vals = cycles_to_generate.split(",")
        cycles = [int(val) for val in cycles_str_vals]
        return battery_df[battery_df["Cycle ID"].isin(cycles)]
    return battery_df

# Plots NDA battery cycle onto a line graph
def plotting_battery_cycle_nda(charge, discharge, min_val, max_val, cycle_legend, color_range, plot_title):
    battery_cycle_viz = plt.figure(figsize=(length,width), facecolor="white")
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

# Plots Arbin battery cycle onto a line graph
def plotting_battery_cycle_arbin(charge, discharge, min_val, max_val, cycle_legend, color_range, plot_title):
    battery_cycle_viz = plt.figure(figsize=(length,width), facecolor="white")
    i = 0

    for cycle_id, group in charge.groupby('Cycle ID'):
        plt.plot(group['Charge_Capacity(Ah)'], group['Voltage(V)'], color = color_range[i], linewidth="1.5")
        i += 1
    
    i = 0

    for cycle_id, group in discharge.groupby('Cycle ID'):
        plt.plot(group['Discharge_Capacity(Ah)'], group['Voltage(V)'], color = color_range[i], linewidth="1.5")
        i += 1

    plt.title(plot_title)
    plt.xlabel("Specific Capacity(Ah)")
    plt.ylabel("Voltage(V)") 
    plt.ylim(min_val, max_val)
    plt.legend(cycle_legend,loc="lower right")
    plt.grid(visible=True)

    return battery_cycle_viz

# Converts the battery_df into a .csv (important for when the user wants to pull a file only containing their cycles)
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Standardizes the dataframe to have these column names (just needs to have the same amount of columns)
def standardize_df(battery_df):
    cycle_id = "Cycle ID"
    voltage = "Voltage(V)"
    current_name = "Current(mA)"
    specific_capacity = "Specific Capacity(mAh/g)"
    
    cycle_id_loc = battery_df.columns[battery_df.isin([cycle_id]).any(axis=0)][0]
    voltage_loc = battery_df.columns[battery_df.isin([voltage]).any(axis=0)][0]
    current_loc = battery_df.columns[battery_df.isin([current_name]).any(axis=0)][0]
    specific_capacity_loc = battery_df.columns[battery_df.isin([specific_capacity]).any(axis=0)][0]
    
    rename_locs = {cycle_id_loc:cycle_id, voltage_loc:voltage, current_loc:current_name,
                specific_capacity_loc:specific_capacity}
    
    battery_df.rename(columns=rename_locs,inplace=True)
    battery_df = battery_df.iloc[1:]
    battery_df.reindex()
    
    battery_df[cycle_id] = battery_df[cycle_id].astype(int)
    battery_df[voltage] = battery_df[voltage].astype(float)
    battery_df[current_name] = battery_df[current_name].astype(float)
    battery_df[specific_capacity] = battery_df[specific_capacity].astype(float)
    
    return battery_df

# Standardizes Arbin dataframe
def standardize_arbin(battery_df):
    if battery_df.columns.values[0] == "Data_Point":
        battery_df.rename(columns={"Cycle_Index": "Cycle ID"}, inplace=True)
        battery_df["Specific Capacity(Ah)"] = battery_df["Charge_Capacity(Ah)"] + battery_df["Discharge_Capacity(Ah)"]
    elif battery_df.columns.values[0] == "DataPoint":
        battery_df.rename(columns={"Cycle Index": "Cycle ID", "Chg. Cap.(Ah)":"Charge_Capacity(Ah)", "DChg. Cap.(Ah)":"Discharge_Capacity(Ah)"}, inplace=True)
    
    return battery_df

# Overall app run here
if generate_button and battery_file:
    # Setup pre-plot
    # Create if-statement to evaluate what the file is (excel or csv)
    # If .xls, then run a function that converts it and standardizes it
    if battery_file.name.endswith(".csv"):
        battery_df = pd.read_csv(battery_file)
    elif battery_file.name.endswith(".xls") or battery_file.name.endswith(".xlsx"): # This might be bugged
        battery_reader_file = pd.ExcelFile(battery_file)
        for sheet in battery_reader_file.sheet_names:
            if sheet == "Record":
                battery_df = pd.read_excel(battery_file, sheet_name="Record") # NDA
            elif "Channel" in sheet:
                battery_df = pd.read_excel(battery_file, sheet_name=sheet)  # Arbin

    # When you need to standardize the columns
    if battery_df.columns.values[0] != "Data serial number":
        if battery_df.columns.values[0] == "Data_Point" or battery_df.columns.values[0] == "DataPoint":
            battery_df = standardize_arbin(battery_df)
        else:
            battery_df = standardize_df(battery_df)
    
    # When there are args in cycles_to_generate 
    battery_df = drop_unwanted_cycles(battery_df, cycles_to_generate)

    number_of_colors = battery_df["Cycle ID"].nunique()
    color_range = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]

    cycle_numbers = battery_df["Cycle ID"].unique().tolist()
    cycle_legend = [] 

    for i in range(len(cycle_numbers)):
        cycle_legend.append("Cycle " + str(cycle_numbers[i]))

    # Plotting (First is NDA, second is Arbin)
    if 'Specific Capacity(mAh/g)' in battery_df.columns:
        charge = battery_df[battery_df["Current(mA)"] >= 0]
        discharge = battery_df[battery_df["Current(mA)"] < 0]
        min_val = battery_df["Voltage(V)"].min()
        max_val = battery_df["Voltage(V)"].max()
        battery_cycle_viz = plotting_battery_cycle_nda(charge, discharge, min_val, max_val, cycle_legend, color_range, plot_title)
    elif 'Specific Capacity(Ah)' in battery_df.columns or 'Specific_Capacity(Ah)' in battery_df.columns or 'Spec. Cap.(mAh/g)' in battery_df.columns:
        charge = battery_df[battery_df["Current(A)"] >= 0]
        discharge = battery_df[battery_df["Current(A)"] < 0]
        min_val = battery_df["Voltage(V)"].min()
        max_val = battery_df["Voltage(V)"].max()
        battery_cycle_viz = plotting_battery_cycle_arbin(charge, discharge, min_val, max_val, cycle_legend, color_range, plot_title)

    st.pyplot(battery_cycle_viz)
    st.download_button(label="Download generated cycle data", data=convert_df(battery_df), file_name="generated-battery-df.csv")
