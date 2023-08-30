import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

st.title("Stock Support and Resistance Calculator")

# Take stock names as input
stock_names = st.text_input("Enter stock symbols separated by commas (e.g., AAPL, GOOGL)", value="reliance.ns, hdfcbank.ns, tcs.ns, icicibank.ns, sbin.ns")

# Split the input symbols
symbols = [symbol.strip() for symbol in stock_names.split(',')]

# Fetch historical data from Yahoo Finance for each symbol
stock_data = {}
for symbol in symbols:
    stock_data[symbol] = yf.download(symbol, period="18mo")

# Check if the stock data is available for all symbols
data_available = all(not data.empty for data in stock_data.values())
if not data_available:
    st.error("Stock data not found for one or more symbols. Please enter valid stock symbols.")
else:
    st.success("Stock data found for all symbols")

    # Calculate support and resistance levels
    def calculate_support_resistance(data):
        # Get the closing prices
        close_prices = data['Close']

        # Find local peaks and valleys
        peaks = argrelextrema(close_prices.values, np.greater, order=3)[0]
        valleys = argrelextrema(close_prices.values, np.less, order=3)[0]

        # Calculate support and resistance levels
        support_levels = []
        for i in range(len(valleys) - 2):
            if close_prices.iloc[valleys[i]] <= close_prices.iloc[valleys[i+1]] and \
               close_prices.iloc[valleys[i+1]] <= close_prices.iloc[valleys[i+2]]:
                support_levels.append(close_prices.iloc[valleys[i]])

        support_levels = pd.Series(support_levels[-3:]).round(2)

        resistance_levels = []
        for i in range(len(peaks) - 2):
            if close_prices.iloc[peaks[i]] >= close_prices.iloc[peaks[i+1]] and \
               close_prices.iloc[peaks[i+1]] >= close_prices.iloc[peaks[i+2]]:
                resistance_levels.append(close_prices.iloc[peaks[i]])

        resistance_levels = pd.Series(resistance_levels[-3:]).round(2)

        return support_levels, resistance_levels

    # Display a table with the 3 most recent support levels for all symbols
    st.header("Recent Support Levels")
    support_table = pd.DataFrame(columns=symbols)

    for symbol in symbols:
        support_levels, _ = calculate_support_resistance(stock_data[symbol])
        if not support_levels.empty:
            support_table[symbol] = support_levels

    st.dataframe(support_table)

    # Display a table with the 3 most recent resistance levels for all symbols
    st.header("Recent Resistance Levels")
    resistance_table = pd.DataFrame(columns=symbols)

    for symbol in symbols:
        _, resistance_levels = calculate_support_resistance(stock_data[symbol])
        if not resistance_levels.empty:
            resistance_table[symbol] = resistance_levels

    st.dataframe(resistance_table)
