import numpy as np
import pandas as pd
import pyEX as p
import streamlit as st
token = 'sk_17ccaec85d7943a78c9269f9e17f664e'
st.set_page_config(layout="wide")

def display_subscription_message():
    st.write(
        "This is for premium users only, please login or subscribe to access our premium stock screener")

    st.write("There's a 7 day free trial!")

    url = 'https://buy.stripe.com/6oEaHAaZG6s0a4g4gg'

    st.markdown(
        f'''
            <a href={url}>
            <button style="background-color: LightGrey; color: black; border: none; 
                            padding: 10px 20px; border-radius: 4px; font-weight: bold;
                            text-decoration: none; cursor: pointer; 
                            box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);">
                Subscribe Now!
            </button>
        </a>
        ''',
        unsafe_allow_html=True
    )

st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.row-widget.stRadio > div{display: flex; flex-direction: row; align-items: left;}</style>',
         unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def set_dataframe_styles():
    styles = """
    <style>
    /* Apply background color to alternate rows */
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    </style>
    """
    return styles


if "username" not in st.session_state:

    display_subscription_message()

else:

    # Function to calculate indicators
    def calculate_indicators(ticker):
        periods = [5, 10, 14, 50, 100, 200]

        # Calculate Moving Average
        for period in periods:
            ticker[f'MA ({period})'] = ticker['close'].rolling(period).mean().round(2)

        # Calculate RSI
        for period in periods:
            delta = ticker['close'].diff(period)
            up = delta.clip(lower=0)
            down = -delta.clip(upper=0)
            avg_gain = up.rolling(period).mean()
            avg_loss = down.rolling(period).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            ticker[f'RSI ({period})'] = rsi.round(2)

        # Calculate Variance
        ticker['Variance'] = ticker['close'].rolling(window=periods[-1]).var().round(2)

        # Calculate Covariance
        for period in periods:
            ticker[f'Covariance ({period})'] = ticker['close'].rolling(period).cov(ticker['close']).round(2)

        # Calculate Value at Risk (VaR)
        confidence_level = 0.95
        ticker['VaR'] = (ticker['close'].rolling(window=periods[-1]).std() * np.sqrt(periods[-1]) * -1.645).round(
            2)  # Assuming normal distribution, 1.645 corresponds to 95% confidence level

        # Calculate Geometric Brownian Motion
        drift = ticker['close'].pct_change().rolling(periods[-1]).mean().round(2)
        volatility = ticker['close'].pct_change().rolling(periods[-1]).std().round(2)
        ticker['Geometric Brownian Motion'] = (ticker['close'].iloc[-1] * np.exp(
            (drift - 0.5 * volatility ** 2) * periods[-1] + volatility * np.sqrt(periods[-1]) * np.random.normal(
                size=len(ticker))).round(2))

        # Calculate Standard Deviation
        for period in periods:
            ticker[f'Standard Deviation ({period})'] = ticker['close'].rolling(period).std().round(2)

        # Calculate MACD
        short_ema = ticker['close'].ewm(span=12, adjust=False).mean().round(2)
        long_ema = ticker['close'].ewm(span=26, adjust=False).mean().round(2)
        ticker['MACD'] = short_ema - long_ema

        return ticker


    # Define a function to fetch the stock data
    def get_stock_data(symbol, timeframe):
        client = p.Client(api_token=token, version='stable')
        # Fetch the stock data
        stock_data = client.chartDF(symbol=symbol, timeframe=timeframe)[['open', 'high', 'low', 'close', 'volume']]
        stock_data = stock_data.sort_values(by="date", ascending=True)
        stock_data.insert(0, 'Symbol', symbol)  # Insert stock symbol column
        return stock_data


    # Streamlit App
    def run_stock_screener():
        st.title("MyQ Stock Screener")

        # Radio button option to choose between view and filter
        view_option = st.radio("Enable Filters?", ["Yes", "No"])
        with st.spinner("Fetching stock data..."):

            # Fetch stock data
            symbols = symbols = ["AAPL",
                                 "MSFT",
                                 "AMZN",
                                 "NVDA",
                                 "GOOGL",
                                 "BRK.B",
                                 "GOOG",
                                 "META",
                                 "UNH",
                                 "XOM",
                                 "TSLA",
                                 "JNJ",
                                 "JPM",
                                 "PG",
                                 "V",
                                 "LLY",
                                 "MA",
                                 "MRK",
                                 "HD",
                                 "CVX",
                                 "PEP",
                                 "ABBV",
                                 "AVGO",
                                 "KO",
                                 "COST",
                                 "MCD",
                                 "PFE",
                                 "TMO",
                                 "WMT",
                                 "ABT",
                                 "CRM",
                                 "BAC",
                                 "CSCO",
                                 "DIS",
                                 "LIN",
                                 "CMCSA",
                                 "ACN",
                                 "DHR",
                                 "VZ",
                                 "NKE",
                                 "ADBE",
                                 "NEE",
                                 "TXN",
                                 "PM",
                                 "ORCL",
                                 "NFLX",
                                 "BMY",
                                 "RTX",
                                 "WFC",
                                 "AMD",
                                 "HON",
                                 "INTC",
                                 "UPS",
                                 "AMGN",
                                 "LOW",
                                 "UNP",
                                 "T",
                                 "SBUX",
                                 "COP",
                                 "INTU",
                                 "QCOM",
                                 "MDT",
                                 "PLD",
                                 "SPGI",
                                 "IBM",
                                 "BA",
                                 "CAT",
                                 "ELV",
                                 "GS",
                                 "GE",
                                 "MS",
                                 "ISRG",
                                 "MDLZ",
                                 "LMT",
                                 "DE",
                                 "BKNG",
                                 "GILD",
                                 "SYK",
                                 "AMAT",
                                 "BLK",
                                 "ADI",
                                 "AMT",
                                 "VRTX",
                                 "TJX",
                                 "AXP",
                                 "ADP",
                                 "CVS",
                                 "MMC",
                                 "NOW",
                                 "C",
                                 "TMUS",
                                 "ZTS",
                                 "MO",
                                 "PYPL",
                                 "REGN",
                                 "CB",
                                 "SO",
                                 "DUK",
                                 "FISV"]

            stock_data_frames = {}

            for symbol in symbols:
                stock_data = get_stock_data(symbol, "2y")  # Specify the timeframe directly
                stock_data = calculate_indicators(stock_data)
                stock_data_frames[symbol] = stock_data.reset_index(
                    drop=True)  # Reset the index to remove the default index column
                stock_data = stock_data.drop(columns=stock_data.columns[0])

            # Append most recent data to a separate data frame
            appended_data = pd.DataFrame()

            for symbol in symbols:
                last_row = stock_data_frames[symbol].iloc[[-1]]
                appended_data = appended_data.append(last_row)

            if view_option == "Yes":
                # Create columns for filters
                col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

                # Filter appended data based on the selected range for RSI 5
                with col1:
                    # Filter for RSI 5 range
                    rsi_range_5 = st.selectbox("RSI 5", ["", "0-30", "30-50", "50-70", "70-100"])

                    if rsi_range_5:
                        min_rsi_5, max_rsi_5 = map(int, rsi_range_5.split('-'))
                        appended_data = appended_data[
                            (appended_data["RSI (5)"] >= min_rsi_5) & (appended_data["RSI (5)"] <= max_rsi_5)]

                # Filter appended data based on the selected range for RSI 10
                with col2:
                    # Filter for RSI 10 range
                    rsi_range_10 = st.selectbox("RSI 10", ["", "0-30", "30-50", "50-70", "70-100"])

                    if rsi_range_10:
                        min_rsi_10, max_rsi_10 = map(int, rsi_range_10.split('-'))
                        appended_data = appended_data[
                            (appended_data["RSI (10)"] >= min_rsi_10) & (appended_data["RSI (10)"] <= max_rsi_10)]

                # Filter appended data based on the selected range for RSI 14
                with col3:
                    # Filter for RSI 14 range
                    rsi_range_14 = st.selectbox("RSI 14", ["", "0-30", "30-50", "50-70", "70-100"])

                    if rsi_range_14:
                        min_rsi_14, max_rsi_14 = map(int, rsi_range_14.split('-'))
                        appended_data = appended_data[
                            (appended_data["RSI (14)"] >= min_rsi_14) & (appended_data["RSI (14)"] <= max_rsi_14)]

                with col4:
                    # Filter for RSI 50 range
                    rsi_range_50 = st.selectbox("RSI 50", ["", "0-30", "30-50", "50-70", "70-100"])

                    if rsi_range_50:
                        min_rsi_50, max_rsi_50 = map(int, rsi_range_50.split('-'))
                        appended_data = appended_data[
                            (appended_data["RSI (50)"] >= min_rsi_50) & (appended_data["RSI (50)"] <= max_rsi_50)]

                with col5:
                    # Filter for RSI 100 range
                    rsi_range_100 = st.selectbox("RSI 100", ["", "0-30", "30-50", "50-70", "70-100"])

                    if rsi_range_100:
                        min_rsi_100, max_rsi_100 = map(int, rsi_range_100.split('-'))
                        appended_data = appended_data[
                            (appended_data["RSI (100)"] >= min_rsi_100) & (appended_data["RSI (100)"] <= max_rsi_100)]

                with col6:
                    # Filter for RSI 200 range
                    rsi_range_200 = st.selectbox("RSI 200", ["", "0-30", "30-50", "50-70", "70-100"])

                    if rsi_range_200:
                        min_rsi_200, max_rsi_200 = map(int, rsi_range_200.split('-'))
                        appended_data = appended_data[
                            (appended_data["RSI (200)"] >= min_rsi_200) & (appended_data["RSI (200)"] <= max_rsi_200)]

                # Display filtered data or full dataset
                # Display filtered data or full dataset
                st.subheader("Stock Screener Results")
                if view_option == "View":
                    st.dataframe(appended_data)
                else:
                    st.markdown(set_dataframe_styles(), unsafe_allow_html=True)
                    st.dataframe(appended_data)

                # Additional features
                show_additional_features = st.radio("Show full dataset", ["No", "Yes"])

            if show_additional_features == "Yes":

                # Show the stock data for the selected symbol
                selected_symbol = st.text_input("Input stock")
                selected_symbol = selected_symbol.upper()
                if selected_symbol:
                    st.subheader(f"Detailed Stock Data for {selected_symbol}")
                    st.dataframe(stock_data_frames[selected_symbol])


