import datetime
import webbrowser
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyEX as p
import pytz
import streamlit as st
from scipy.stats import norm
from ta import add_all_ta_features
import openpyxl


def display_subscription_message():
    st.write(
        "This is for premium users only, please login or subscribe to access our premium market dashboard")

    st.write("There's a 7 day free trial!")

    url = 'https://buy.stripe.com/7sIdRK4ti85E2paeUU'

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
import pyEX as p
token = 'sk_d29084f79c0c4135809f6c58a552d1e7'

st.set_page_config(layout="wide")
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)

st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Check if the user is logged in
if "username" not in st.session_state:
    # If the user is not logged in, show the login form

    try:
        # This creates the two text boxes side by side for stock input and time input

        c1, c2 = st.columns([3, 5])

        with c1:

            # Load the Excel file
            excel_file = 'MyQ_v1_dash/pages/Stock_List.xlsx'

            df = pd.read_excel(excel_file)

            options = df['symbol'].tolist()  # Replace 'Column_Name' with the actual column name from your Excel sheet

            tickerSymbol = st.selectbox('Select a stock:', options)

            # Perform VLOOKUP to get the corresponding value
            value = df.loc[df['symbol'] == tickerSymbol, 'name'].values[
                0]  # Replace 'Value_Column' with the actual column name containing the values

            st.write(value)
            
        with c2:
            tickerTime = st.radio(
                'Select time period for analysis',
                options=['6m', '1y', '2y', 'max'])

            # Call the API from IEX Cloud based on user input from 'stock_option' variable

            c = p.Client(api_token=token, version='stable')

            # Assign the API call to a pandas dataframe called ticker
            ticker = c.chartDF(symbol=tickerSymbol, timeframe=tickerTime)[
                ['open', 'high', 'low', 'close', 'volume']]

            ticker = ticker.sort_values(by="date", ascending=True)

            ticker['Increase_Decrease'] = np.where(ticker['volume'].shift(-1) > ticker['volume'], 'Increase',
                                                   'Decrease')
            ticker['Buy_Sell_on_Open'] = np.where(ticker['open'].shift(-1) > ticker['open'], 1, 0)
            ticker['Buy_Sell'] = np.where(ticker['close'].shift(-1) > ticker['close'], 1, 0)
            ticker['Returns'] = ticker['close'].pct_change()
            dataset = ticker.dropna()
            ticker['Increase_Decrease'].value_counts()
            ticker['VolumePositive'] = ticker['open'] < ticker['close']

            delta = ticker['close'].diff(5)
            ticker['Close_to_Close_5'] = delta

            # 5 RSI + Percentile Calculations
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=4, adjust=False).mean()
            ema_down = down.ewm(com=4, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (5)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 14 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (14)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 50 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=49, adjust=False).mean()
            ema_down = down.ewm(com=49, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (50)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 100 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=99, adjust=False).mean()
            ema_down = down.ewm(com=99, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (100)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 200 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=199, adjust=False).mean()
            ema_down = down.ewm(com=199, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (200)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # Moving Averages
            ticker['Moving Average (5)'] = ticker['close'].rolling(5).mean().round(2)
            ticker['Moving Average (14)'] = ticker['close'].rolling(14).mean().round(2)
            ticker['Moving Average (50)'] = ticker['close'].rolling(50).mean().round(2)
            ticker['Moving Average (100)'] = ticker['close'].rolling(100).mean().round(2)
            ticker['Moving Average (200)'] = ticker['close'].rolling(200).mean().round(2)

            # Moving Average Trend Analysis
            # Values for Moving Averages (today)
            today_ma_5 = ticker['Moving Average (5)'].tail(1)
            today_ma_14 = ticker['Moving Average (14)'].tail(1)
            today_ma_50 = ticker['Moving Average (50)'].tail(1)
            today_ma_100 = ticker['Moving Average (100)'].tail(1)
            today_ma_200 = ticker['Moving Average (200)'].tail(1)

            # RSI Analysis
            # Values for Moving Averages (today)
            today_rsi_5 = ticker['RSI (5)'].tail(1)
            today_rsi_14 = ticker['RSI (14)'].tail(1)
            today_rsi_50 = ticker['RSI (50)'].tail(1)
            today_rsi_100 = ticker['RSI (100)'].tail(1)
            today_rsi_200 = ticker['RSI (200)'].tail(1)

            # Values for Moving Averages (yesterday)

            diff_5_rsi = ticker['RSI (5)'].iloc[-1] - ticker['RSI (5)'].iloc[-2]
            percentage_change_5 = (diff_5_rsi / ticker['RSI (5)'].iloc[-2]) * 100
            rounded_percentage_change_5 = percentage_change_5.round(2)
            rsi_formatted_percentage_change_5 = f"{rounded_percentage_change_5}%"

            diff_14 = ticker['RSI (14)'].iloc[-1] - ticker['RSI (14)'].iloc[-2]
            percentage_change_14 = (diff_14 / ticker['RSI (14)'].iloc[-2]) * 100
            rounded_percentage_change_14 = percentage_change_14.round(2)
            rsi_formatted_percentage_change_14 = f"{rounded_percentage_change_14}%"

            diff_50 = ticker['RSI (50)'].iloc[-1] - ticker['RSI (50)'].iloc[-2]
            percentage_change_50 = (diff_50 / ticker['RSI (50)'].iloc[-2]) * 100
            rounded_percentage_change_50 = percentage_change_50.round(2)
            rsi_formatted_percentage_change_50 = f"{rounded_percentage_change_50}%"

            diff_100 = ticker['RSI (100)'].iloc[-1] - ticker['RSI (100)'].iloc[-2]
            percentage_change_100 = (diff_100 / ticker['RSI (100)'].iloc[-2]) * 100
            rounded_percentage_change_100 = percentage_change_100.round(2)
            rsi_formatted_percentage_change_100 = f"{rounded_percentage_change_100}%"

            diff_200 = ticker['RSI (200)'].iloc[-1] - ticker['RSI (200)'].iloc[-2]
            percentage_change_200 = (diff_200 / ticker['RSI (200)'].iloc[-2]) * 100
            rounded_percentage_change_200 = percentage_change_200.round(2)
            rsi_formatted_percentage_change_200 = f"{rounded_percentage_change_200}%"

            ticker['MF Multiplier'] = (2 * ticker['close'] - ticker['low'] - ticker['high']) / (
                    ticker['high'] - ticker['low'])
            ticker['MF Volume'] = ticker['MF Multiplier'] * ticker['volume']
            ticker['ADL'] = ticker['MF Volume'].cumsum()

            n = 14  # number of periods
            ticker['sum'] = ticker['close'].rolling(n).sum()

            returns = ticker['close'].pct_change()[1:].dropna()

            n = 14
            ticker['HL'] = ticker['high'] - ticker['low']
            ticker['HC'] = abs(ticker['high'] - ticker['close'].shift())
            ticker['LC'] = abs(ticker['low'] - ticker['close'].shift())
            ticker['TR'] = ticker[['HL', 'HC', 'LC']].max(axis=1)
            ticker['ATR'] = ticker['TR'].rolling(n).mean()
            ticker = ticker.drop(['HL', 'HC', 'LC', 'TR'], axis=1)
            daily_returns = ticker['close'].pct_change()

        # Creating the tabs for the relevant areas on the dashboard

        Returns, Technical, Quantitative, Risk, Maths, Physics = st.tabs(
            ["Returns", "Technical", "Quantitative", "Risk", "Mathematics", "Physics"])

        with Returns:
            Candlestick, Line, OHLC, Histogram, Increase_Decrease, Increase_Decrease_Count, Scatter, Volume = st.tabs(
                ["Candlestick", "Line", "OHLC", "Histogram", "Increase/Decrease", "Increase/Decrease Count",
                 "Scatter Plot",
                 "Volume"])

            with Candlestick:
                col1, col2 = st.columns([10, 2])

                with col1:
                    title = f"{tickerSymbol} Stock Chart ({tickerTime} timeframe)"

                    trace = go.Candlestick(x=ticker.index,
                                           open=ticker['open'],
                                           high=ticker['high'],
                                           low=ticker['low'],
                                           close=ticker['close'])

                    layout = go.Layout(title=title, yaxis=dict(title='Price ($)'))

                    fig = go.Figure(data=[trace], layout=layout)

                    st.write(fig)

                with col2:
                    today_price = ticker['close'].tail(1).item()
                    previous_close = ticker['close'].iloc[-2]
                    percent_change = ((today_price - previous_close) / previous_close) * 100
                    formatted_price_changes = {'1 Day Change': f"{percent_change:.2f}%"}

                    price_changes = {
                        '5 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-5],
                        '10 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    }

                    for period, price_change in price_changes.items():
                        percent_change = (price_change / ticker['close'].iloc[-2]) * 100
                        formatted_price_change = f"{percent_change:.2f}%"
                        formatted_price_changes[period] = formatted_price_change

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a candlestick chart?": "A candlestick chart is a popular type of financial chart used to represent the price movement of an asset, such as stocks or currencies, over a specific time period. It provides visual insights into the opening, closing, high, and low prices of the asset within each time interval.",
                    "How do I interpret a candlestick chart?": "Each candlestick on the chart represents a specific time period (e.g., a day, an hour) and consists of a rectangular body and thin lines called wicks or shadows. The body represents the price range between the opening and closing prices, while the wicks indicate the high and low prices reached during the time period. A filled (colored) body typically represents a bearish (downward) movement, while an empty (uncolored) or filled body with a different color represents a bullish (upward) movement.",
                    "What does a long/short body indicate?": "A long body suggests a significant price movement during the time period, indicating strong buying or selling pressure. Conversely, a short body implies a relatively small price movement and potentially indecisive market conditions.",
                    "What do the upper and lower wicks indicate?": "The upper wick represents the highest price reached during the time period, while the lower wick represents the lowest price reached. Longer wicks suggest greater price volatility, while shorter wicks indicate more stability within the time period.",
                    "Can candlestick patterns help in predicting price movements?": "Yes, candlestick patterns are widely used by traders and analysts to identify potential trend reversals, continuations, or patterns that may suggest future price movements. Common candlestick patterns include doji, hammer, engulfing patterns, and more. However, it's important to note that candlestick patterns should be used in conjunction with other technical analysis tools and indicators for more accurate predictions.",
                    "How can I customize the candlestick chart?": "Most charting platforms and tools allow you to customize the appearance of candlestick charts. You can adjust the time period displayed, add technical indicators (such as moving averages or Bollinger Bands), change the colors and styles of the candlesticks, and more. These customization options can help you analyze the chart according to your preferred trading strategy or analysis approach."
                }
                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Line:
                col1, col2 = st.columns([10, 2])
                with col1:
                    fig = go.Figure(data=go.Scatter(x=dataset.index, y=dataset['close']))
                    fig.update_layout(
                        title="Close Prices - Line chart",
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )
                    st.plotly_chart(fig)

                with col2:

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                            [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a line chart?": "A line chart is a type of chart that displays data as a series of data points connected by straight line segments. It is commonly used to visualize the trend or pattern of data over time or across different categories.",
                    "How do I interpret a line chart?": "In a line chart, the x-axis represents the independent variable (e.g., time, categories) and the y-axis represents the dependent variable (e.g., numerical values). The data points on the chart are plotted and connected by lines, allowing you to see the overall trend, fluctuations, or changes in the data over the given time period or categories.",
                    "What does an upward/downward trend indicate?": "An upward trend in a line chart shows an increasing or positive relationship between the variables being plotted. It indicates that the dependent variable is generally increasing as the independent variable increases. Conversely, a downward trend shows a decreasing or negative relationship.",
                    "What can I infer from a flat or horizontal line?": "A flat or horizontal line in a line chart indicates no significant change or trend in the data. It suggests that the dependent variable remains relatively constant or does not show any clear relationship with the independent variable.",
                    "Can I compare multiple data series in a line chart?": "Yes, a line chart allows you to compare multiple data series on the same chart by plotting each series as a separate line with different colors or styles. This enables you to visualize and analyze the relationship or patterns among different variables or categories.",
                    "How can I customize the line chart?": "Most charting tools and libraries offer customization options for line charts. You can modify the appearance, such as changing line colors, styles, thickness, adding data markers, and adjusting the axes labels and scales. Additionally, you can include annotations, legends, and other interactive features to enhance the chart's readability and interactivity."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with OHLC:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['open'], name='Open'))
                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['low'], name='Low'))
                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['high'], name='High'))
                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['close'], name='Close'))

                    fig.update_layout(
                        title="OHLC Prices",
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )

                    st.write(fig)

                with col2:

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is an OHLC chart?": "An OHLC chart, also known as a bar chart, is a type of financial chart that represents the price movement of an asset, such as stocks or currencies, over a specific time period. It displays the opening, high, low, and closing prices of the asset for each time interval.",
                    "How do I interpret an OHLC chart?": "Each bar on the chart represents a specific time period (e.g., a day, an hour) and consists of four points: the opening price (represented by a horizontal line on the left), the highest price reached (top of the bar), the lowest price reached (bottom of the bar), and the closing price (represented by a horizontal line on the right). The length of the vertical line (bar) provides insights into the price range and volatility during the time period.",
                    "What does a long/short bar indicate?": "A long bar indicates a significant price movement during the time period, reflecting strong buying or selling pressure. On the other hand, a short bar suggests a relatively small price movement and potentially indecisive market conditions.",
                    "How can I identify bullish or bearish bars?": "In an OHLC chart, a bullish bar is usually represented by a green or white bar. It indicates that the closing price is higher than the opening price, suggesting a positive price movement. Conversely, a bearish bar is typically represented by a red or black bar, indicating that the closing price is lower than the opening price, suggesting a negative price movement.",
                    "Can I customize the appearance of an OHLC chart?": "Yes, many charting platforms and tools allow you to customize the appearance of OHLC charts. You can adjust the colors, styles, and widths of the bars, as well as add additional technical indicators or overlays to enhance your analysis, such as moving averages, volume bars, or trendlines.",
                    "How can I use OHLC data for analysis?": "OHLC data is commonly used for technical analysis to identify patterns, trends, and potential trading opportunities. Traders often look for patterns like doji, hammer, engulfing, or harami to make decisions. Additionally, OHLC data can be used in conjunction with other indicators, such as moving averages or oscillators, to further analyze market dynamics."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Histogram:
                col1, col2 = st.columns([10, 2])

                with col1:
                    # Create trace for histogram of daily returns
                    trace = go.Histogram(x=daily_returns, nbinsx=50, histnorm='probability', opacity=0.5,
                                         name='Daily Returns')

                    # Create layout
                    layout = go.Layout(title='Histogram of Stock Daily Returns', xaxis=dict(title='Daily Returns'),
                                       yaxis=dict(title='Frequency'))

                    # Create figure object and add trace and layout
                    fig = go.Figure(data=[trace], layout=layout)

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a returns histogram?": "A returns histogram is a graphical representation that displays the distribution of returns for a given dataset. It provides insights into the frequency and magnitude of returns observed in the data, allowing you to analyze the volatility or risk associated with an asset or investment strategy.",
                    "How do I interpret a returns histogram?": "In a returns histogram, the x-axis represents the range of returns, divided into bins or intervals, while the y-axis represents the frequency or count of occurrences within each bin. The height of each bar represents the number of observations falling within a specific range of returns. A wider or more spread-out histogram suggests a higher variability or dispersion of returns, while a narrower histogram indicates a more concentrated or less volatile distribution.",
                    "What can I infer from a skewness in the histogram?": "Skewness in a returns histogram refers to the asymmetry of the distribution. A positive skewness indicates a longer tail on the right side of the histogram, suggesting a higher frequency of positive returns or a potential for large positive outliers. Conversely, a negative skewness indicates a longer tail on the left side, indicating a higher frequency of negative returns or potential for large negative outliers.",
                    "How can I identify the shape of the distribution?": "The shape of a returns histogram can provide insights into the underlying distribution. Common shapes include symmetric bell-shaped (normal or Gaussian), skewed, bimodal, or fat-tailed distributions. These shapes can help you understand the characteristics and behavior of the returns data, such as whether it follows a known statistical distribution or exhibits specific patterns or anomalies.",
                    "How can I use a returns histogram in analysis?": "Returns histograms are commonly used in finance and investment analysis to assess risk, evaluate investment strategies, and identify abnormal return patterns. They can help you understand the potential range and likelihood of returns, evaluate the performance of investments relative to a benchmark, and support decision-making in portfolio management or risk assessment."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Increase_Decrease:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = px.line(dataset, x=dataset.index, y="close", color="Increase_Decrease")

                    fig.update_layout(
                        title="Close Prices - Increase/Decrease",
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is an Increase Decrease chart?": "An Increase Decrease chart, also known as an Up Down chart or a Step chart, is a type of chart that visually represents the increase and decrease in values over a given time period or category. It focuses on showcasing the direction and magnitude of changes rather than the specific values.",
                    "How do I interpret an Increase Decrease chart?": "In an Increase Decrease chart, the x-axis represents the time period or categories, while the y-axis typically represents the magnitude or scale of the values being plotted. Instead of using continuous lines or bars, this chart uses vertical steps or connected blocks to represent changes. The upward steps indicate an increase in values, while the downward steps represent a decrease.",
                    "What does a larger step indicate?": "A larger step in an Increase Decrease chart indicates a greater change in values over the given time period or category. It signifies a more significant increase or decrease in the corresponding data compared to smaller steps.",
                    "Can I compare multiple data series in an Increase Decrease chart?": "Yes, an Increase Decrease chart allows you to compare multiple data series by plotting them on the same chart using different colors or styles. This enables you to visually compare the changes in values across different categories or time periods and identify trends or patterns.",
                    "How can I customize the appearance of an Increase Decrease chart?": "Most charting libraries and tools provide options to customize the appearance of Increase Decrease charts. You can adjust the colors, thickness, or styles of the steps or blocks, modify the axes labels and scales, and add additional annotations or visual elements to enhance the clarity and readability of the chart.",
                    "What types of data are suitable for an Increase Decrease chart?": "Increase Decrease charts are particularly useful for representing categorical data or discrete values that exhibit clear increase and decrease patterns. They are commonly used in various domains, including finance, stock market analysis, project management, and other areas where changes in values or progress tracking are important."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Increase_Decrease_Count:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = px.histogram(ticker, x="Increase_Decrease")

                    fig.update_layout(
                        title="Increase/Decrease Count",
                        xaxis_title="Increase/Decrease",
                        yaxis_title="Count"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))
                faq = {
                    "What is an Increase Decrease Count chart?": "An Increase Decrease Count chart is a type of chart that visually represents the count or frequency of increase and decrease events over a given time period or category. It provides insights into the number of occurrences of upward and downward movements rather than the specific values associated with them.",
                    "How do I interpret an Increase Decrease Count chart?": "In an Increase Decrease Count chart, the x-axis represents the time period or categories, while the y-axis represents the count or frequency of increase and decrease events. The chart displays vertical bars or steps, where the upward bars indicate the count of increase events, and the downward bars represent the count of decrease events.",
                    "What does a taller bar indicate?": "A taller bar in an Increase Decrease Count chart indicates a higher count or frequency of increase or decrease events over the given time period or category. It represents a greater number of occurrences of upward or downward movements compared to shorter bars.",
                    "Can I compare multiple data series in an Increase Decrease Count chart?": "Yes, an Increase Decrease Count chart allows you to compare multiple data series by plotting them on the same chart using different colors or styles. This enables you to visually compare the count of increase and decrease events across different categories or time periods and identify patterns or trends.",
                    "How can I customize the appearance of an Increase Decrease Count chart?": "Most charting libraries and tools provide options to customize the appearance of Increase Decrease Count charts. You can adjust the colors, thickness, or styles of the bars or steps, modify the axes labels and scales, and add additional annotations or visual elements to enhance the clarity and readability of the chart.",
                    "What types of data are suitable for an Increase Decrease Count chart?": "Increase Decrease Count charts are useful for analyzing datasets that involve counting events of increase and decrease. They are commonly used in various fields such as finance, stock market analysis, sales analysis, and other areas where the frequency of upward and downward movements is of interest."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Scatter:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=ticker['open'], y=ticker['close'], mode='markers'))

                    fig.update_layout(
                        title="Open vs. Close Scatter Plot",
                        xaxis_title="Open Price",
                        yaxis_title="Close Price"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a scatter plot chart?": "A scatter plot chart is a type of chart that displays individual data points as markers on a two-dimensional plane. It is used to visualize the relationship or correlation between two variables. Each data point is represented by a marker, and the position of the marker on the chart corresponds to the values of the two variables being plotted.",
                    "How do I interpret a scatter plot chart?": "In a scatter plot chart, the x-axis represents one variable, while the y-axis represents the other variable. The position of each data point on the chart indicates the values of the two variables for that specific data point. By analyzing the distribution, clustering, or pattern of the data points, you can infer the relationship between the variables, such as positive or negative correlation, clusters, outliers, or trends.",
                    "What does the density of data points indicate?": "The density of data points in a scatter plot chart provides insights into the concentration or frequency of observations within specific regions of the chart. Higher density indicates a larger number of data points in that area, while lower density suggests sparser observations. The density of data points can reveal patterns, clusters, or trends in the relationship between the variables.",
                    "Can I customize the appearance of a scatter plot chart?": "Yes, most charting libraries and tools provide options to customize the appearance of scatter plot charts. You can modify the marker style, size, color, or transparency, adjust the axes labels and scales, add annotations, or include additional visual elements such as trend lines or regression lines to enhance the chart's interpretability and aesthetics.",
                    "How can I identify correlation or patterns in a scatter plot chart?": "In a scatter plot chart, you can visually assess the correlation between variables by observing the general trend or pattern of the data points. If the points tend to form a positive slope or curve, it indicates a positive correlation. Conversely, a negative slope or scattered distribution suggests a negative correlation. You can also use statistical measures or techniques, such as calculating correlation coefficients or fitting regression models, to quantify and validate the observed relationships.",
                    "What types of data are suitable for a scatter plot chart?": "Scatter plot charts are commonly used when working with continuous or numeric data. They are useful for visualizing and exploring relationships, correlations, clusters, or outliers in various domains, including scientific research, finance, marketing, and social sciences, among others."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Volume:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = go.Figure()

                    fig.add_trace(
                        go.Bar(
                            x=ticker.index,
                            y=ticker['volume'],
                            name='Volume',
                            marker_color=ticker['VolumePositive'].map({True: 'green', False: 'red'}),
                            opacity=0.4
                        )
                    )

                    fig.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Daily Volume',
                        title=f"{tickerSymbol} Volume"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a volume chart?": "A volume chart is a type of financial chart that represents the trading volume or the number of shares or contracts traded over a specific time period. It provides insights into the liquidity, market activity, and buying or selling pressure for a particular asset or financial instrument.",
                    "How do I interpret a volume chart?": "In a volume chart, the x-axis represents the time period, while the y-axis represents the trading volume. Each bar or column on the chart represents the volume of shares or contracts traded during a specific time interval. By analyzing the height or length of the bars, you can identify periods of high or low trading activity and gauge the market sentiment.",
                    "What does a taller bar indicate?": "A taller bar in a volume chart indicates a higher trading volume for the corresponding time interval. It suggests increased market activity, higher liquidity, and potentially greater interest or participation from traders or investors.",
                    "Can I compare volume with price movements?": "Yes, volume charts are often used in conjunction with other types of financial charts, such as candlestick charts or line charts, to analyze the relationship between trading volume and price movements. By comparing the volume bars with the corresponding price movements, you can identify potential correlations, divergences, or patterns that may provide insights into market trends or reversals.",
                    "How can I customize the appearance of a volume chart?": "Most charting platforms and tools provide options to customize the appearance of volume charts. You can adjust the color, thickness, or style of the volume bars, modify the axes labels and scales, and add additional technical indicators or overlays, such as moving averages or volume-based oscillators, to enhance your analysis.",
                    "What types of data are suitable for a volume chart?": "Volume charts are primarily used in the analysis of financial markets, such as stocks, futures, or currencies, where trading volume is readily available. They are particularly useful for understanding market dynamics, identifying potential trends, reversals, or price support/resistance levels, and confirming or questioning the validity of price movements."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

        with Technical:

            Moving_Average, RSI, Accumulation_Distribution, Moving_Summation, Bollinger_Bands, Acceleration_Bands = st.tabs(
                ["Moving Average", "RSI", "Accumulation Distribution", "Moving Summation", "Bollinger Bands",
                 "Acceleration_Bands"])

            with Moving_Average:
                display_subscription_message()

            with RSI:
                display_subscription_message()

            with Accumulation_Distribution:
                display_subscription_message()

            with Moving_Summation:
                display_subscription_message()

            with Bollinger_Bands:
                display_subscription_message()

            with Acceleration_Bands:
                display_subscription_message()

        with Quantitative:

            Standard_Deviation, Variance, Residual_Risk, Geometric_Mean, HistoGram_Returns, Log_Returns = st.tabs(
                ["Standard Deviation", "Variance", "Residual Risk", "Geometric Mean", "Histogram Returns",
                 "Log Returns"])

            with Standard_Deviation:
                display_subscription_message()

            with Variance:
                display_subscription_message()

            with Residual_Risk:
                display_subscription_message()

            with HistoGram_Returns:
                display_subscription_message()

            with Log_Returns:
                display_subscription_message()

            with Geometric_Mean:
                display_subscription_message()

        with Risk:
            ATR, Returns, Realised_Volatility, Relative_Volatility = st.tabs(
                ["ATR", "Returns", "Realised Volatility", "Relative Volatility"])

            with ATR:
                display_subscription_message()

            with Returns:
                display_subscription_message()

            with Realised_Volatility:
                display_subscription_message()

            with Relative_Volatility:
                display_subscription_message()

        with Maths:
            Standard, Kurtosis = st.tabs(
                ["Standard Deviation", "Kurtosis"])

            with Standard:
                display_subscription_message()

            with Kurtosis:
                display_subscription_message()

        with Physics:

            Momentum, Chaos_Theory = st.tabs(
                ["Momentum", "Chaos Theory"])

            with Momentum:
                display_subscription_message()

            with Chaos_Theory:
                display_subscription_message()


    except:
        # Prevent the error from propagating into your Streamlit app.
        pass


else:

    try:
        # This creates the two text boxes side by side for stock input and time input

        c1, c2 = st.columns([3, 5])

        with c1:

            # Load the Excel file
            excel_file = 'MyQ_v1_dash/pages/Stock_List.xlsx'
            df = pd.read_excel(excel_file)

            options = df['symbol'].tolist()  # Replace 'Column_Name' with the actual column name from your Excel sheet

            tickerSymbol = st.selectbox('Select a stock:', options)

            # Perform VLOOKUP to get the corresponding value
            value = df.loc[df['symbol'] == tickerSymbol, 'name'].values[
                0]  # Replace 'Value_Column' with the actual column name containing the values

            st.write(value)

        with c2:
            tickerTime = st.radio(
                'Select time period for analysis',
                options=['6m', '1y', '2y', 'max'])

            # Call the API from IEX Cloud based on user input from 'stock_option' variable
            c = p.Client(api_token=token, version='stable')

            # Assign the API call to a pandas dataframe called ticker
            ticker = c.chartDF(symbol=tickerSymbol, timeframe=tickerTime)[
                ['open', 'high', 'low', 'close', 'volume']]

            ticker = ticker.sort_values(by="date", ascending=True)

            ticker['Increase_Decrease'] = np.where(ticker['volume'].shift(-1) > ticker['volume'], 'Increase',
                                                   'Decrease')
            ticker['Buy_Sell_on_Open'] = np.where(ticker['open'].shift(-1) > ticker['open'], 1, 0)
            ticker['Buy_Sell'] = np.where(ticker['close'].shift(-1) > ticker['close'], 1, 0)
            ticker['Returns'] = ticker['close'].pct_change()
            dataset = ticker.dropna()
            ticker['Increase_Decrease'].value_counts()
            ticker['VolumePositive'] = ticker['open'] < ticker['close']

            delta = ticker['close'].diff(5)
            ticker['Close_to_Close_5'] = delta

            # 5 RSI + Percentile Calculations
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=4, adjust=False).mean()
            ema_down = down.ewm(com=4, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (5)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 14 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (14)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 50 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=49, adjust=False).mean()
            ema_down = down.ewm(com=49, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (50)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 100 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=99, adjust=False).mean()
            ema_down = down.ewm(com=99, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (100)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # 200 RSI Calc
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=199, adjust=False).mean()
            ema_down = down.ewm(com=199, adjust=False).mean()
            rs = ema_up / ema_down
            ticker['RSI (200)'] = 100 - (100 / (1 + rs))
            # Skip first 14 days to have real values
            ticker = ticker.iloc[14:].round(2)

            # Moving Averages
            ticker['Moving Average (5)'] = ticker['close'].rolling(5).mean().round(2)
            ticker['Moving Average (14)'] = ticker['close'].rolling(14).mean().round(2)
            ticker['Moving Average (50)'] = ticker['close'].rolling(50).mean().round(2)
            ticker['Moving Average (100)'] = ticker['close'].rolling(100).mean().round(2)
            ticker['Moving Average (200)'] = ticker['close'].rolling(200).mean().round(2)

            # Moving Average Trend Analysis
            # Values for Moving Averages (today)
            today_ma_5 = ticker['Moving Average (5)'].tail(1)
            today_ma_14 = ticker['Moving Average (14)'].tail(1)
            today_ma_50 = ticker['Moving Average (50)'].tail(1)
            today_ma_100 = ticker['Moving Average (100)'].tail(1)
            today_ma_200 = ticker['Moving Average (200)'].tail(1)

            # RSI Analysis
            # Values for Moving Averages (today)
            today_rsi_5 = ticker['RSI (5)'].tail(1)
            today_rsi_14 = ticker['RSI (14)'].tail(1)
            today_rsi_50 = ticker['RSI (50)'].tail(1)
            today_rsi_100 = ticker['RSI (100)'].tail(1)
            today_rsi_200 = ticker['RSI (200)'].tail(1)

            # Values for Moving Averages (yesterday)

            diff_5_rsi = ticker['RSI (5)'].iloc[-1] - ticker['RSI (5)'].iloc[-2]
            percentage_change_5 = (diff_5_rsi / ticker['RSI (5)'].iloc[-2]) * 100
            rounded_percentage_change_5 = percentage_change_5.round(2)
            rsi_formatted_percentage_change_5 = f"{rounded_percentage_change_5}%"

            diff_14 = ticker['RSI (14)'].iloc[-1] - ticker['RSI (14)'].iloc[-2]
            percentage_change_14 = (diff_14 / ticker['RSI (14)'].iloc[-2]) * 100
            rounded_percentage_change_14 = percentage_change_14.round(2)
            rsi_formatted_percentage_change_14 = f"{rounded_percentage_change_14}%"

            diff_50 = ticker['RSI (50)'].iloc[-1] - ticker['RSI (50)'].iloc[-2]
            percentage_change_50 = (diff_50 / ticker['RSI (50)'].iloc[-2]) * 100
            rounded_percentage_change_50 = percentage_change_50.round(2)
            rsi_formatted_percentage_change_50 = f"{rounded_percentage_change_50}%"

            diff_100 = ticker['RSI (100)'].iloc[-1] - ticker['RSI (100)'].iloc[-2]
            percentage_change_100 = (diff_100 / ticker['RSI (100)'].iloc[-2]) * 100
            rounded_percentage_change_100 = percentage_change_100.round(2)
            rsi_formatted_percentage_change_100 = f"{rounded_percentage_change_100}%"

            diff_200 = ticker['RSI (200)'].iloc[-1] - ticker['RSI (200)'].iloc[-2]
            percentage_change_200 = (diff_200 / ticker['RSI (200)'].iloc[-2]) * 100
            rounded_percentage_change_200 = percentage_change_200.round(2)
            rsi_formatted_percentage_change_200 = f"{rounded_percentage_change_200}%"

            ticker['MF Multiplier'] = (2 * ticker['close'] - ticker['low'] - ticker['high']) / (
                    ticker['high'] - ticker['low'])
            ticker['MF Volume'] = ticker['MF Multiplier'] * ticker['volume']
            ticker['ADL'] = ticker['MF Volume'].cumsum()

            n = 14  # number of periods
            ticker['sum'] = ticker['close'].rolling(n).sum()

            returns = ticker['close'].pct_change()[1:].dropna()

            n = 14
            ticker['HL'] = ticker['high'] - ticker['low']
            ticker['HC'] = abs(ticker['high'] - ticker['close'].shift())
            ticker['LC'] = abs(ticker['low'] - ticker['close'].shift())
            ticker['TR'] = ticker[['HL', 'HC', 'LC']].max(axis=1)
            ticker['ATR'] = ticker['TR'].rolling(n).mean()
            ticker = ticker.drop(['HL', 'HC', 'LC', 'TR'], axis=1)
            daily_returns = ticker['close'].pct_change()



        # Creating the tabs for the relevant areas on the dashboard

        Returns, Technical, Quantitative, Risk, Maths, Physics = st.tabs(
            ["Returns", "Technical", "Quantitative", "Risk", "Mathematics", "Physics"])

        with Returns:
            Candlestick, Line, OHLC, Histogram, Increase_Decrease, Increase_Decrease_Count, Scatter, Volume = st.tabs(
                ["Candlestick", "Line", "OHLC", "Histogram", "Increase/Decrease", "Increase/Decrease Count",
                 "Scatter Plot",
                 "Volume"])

            with Candlestick:
                col1, col2 = st.columns([10, 2])

                with col1:
                    title = f"{tickerSymbol} Stock Chart ({tickerTime} timeframe)"

                    trace = go.Candlestick(x=ticker.index,
                                           open=ticker['open'],
                                           high=ticker['high'],
                                           low=ticker['low'],
                                           close=ticker['close'])

                    layout = go.Layout(title=title, yaxis=dict(title='Price ($)'))

                    fig = go.Figure(data=[trace], layout=layout)

                    st.write(fig)

                with col2:
                    today_price = ticker['close'].tail(1).item()
                    previous_close = ticker['close'].iloc[-2]
                    percent_change = ((today_price - previous_close) / previous_close) * 100
                    formatted_price_changes = {'1 Day Change': f"{percent_change:.2f}%"}

                    price_changes = {
                        '5 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-5],
                        '10 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    }

                    for period, price_change in price_changes.items():
                        percent_change = (price_change / ticker['close'].iloc[-2]) * 100
                        formatted_price_change = f"{percent_change:.2f}%"
                        formatted_price_changes[period] = formatted_price_change

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a candlestick chart?": "A candlestick chart is a popular type of financial chart used to represent the price movement of an asset, such as stocks or currencies, over a specific time period. It provides visual insights into the opening, closing, high, and low prices of the asset within each time interval.",
                    "How do I interpret a candlestick chart?": "Each candlestick on the chart represents a specific time period (e.g., a day, an hour) and consists of a rectangular body and thin lines called wicks or shadows. The body represents the price range between the opening and closing prices, while the wicks indicate the high and low prices reached during the time period. A filled (colored) body typically represents a bearish (downward) movement, while an empty (uncolored) or filled body with a different color represents a bullish (upward) movement.",
                    "What does a long/short body indicate?": "A long body suggests a significant price movement during the time period, indicating strong buying or selling pressure. Conversely, a short body implies a relatively small price movement and potentially indecisive market conditions.",
                    "What do the upper and lower wicks indicate?": "The upper wick represents the highest price reached during the time period, while the lower wick represents the lowest price reached. Longer wicks suggest greater price volatility, while shorter wicks indicate more stability within the time period.",
                    "Can candlestick patterns help in predicting price movements?": "Yes, candlestick patterns are widely used by traders and analysts to identify potential trend reversals, continuations, or patterns that may suggest future price movements. Common candlestick patterns include doji, hammer, engulfing patterns, and more. However, it's important to note that candlestick patterns should be used in conjunction with other technical analysis tools and indicators for more accurate predictions.",
                    "How can I customize the candlestick chart?": "Most charting platforms and tools allow you to customize the appearance of candlestick charts. You can adjust the time period displayed, add technical indicators (such as moving averages or Bollinger Bands), change the colors and styles of the candlesticks, and more. These customization options can help you analyze the chart according to your preferred trading strategy or analysis approach."
                }
                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Line:
                col1, col2 = st.columns([10, 2])
                with col1:
                    fig = go.Figure(data=go.Scatter(x=dataset.index, y=dataset['close']))
                    fig.update_layout(
                        title="Close Prices - Line chart",
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )
                    st.plotly_chart(fig)

                with col2:

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                            [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a line chart?": "A line chart is a type of chart that displays data as a series of data points connected by straight line segments. It is commonly used to visualize the trend or pattern of data over time or across different categories.",
                    "How do I interpret a line chart?": "In a line chart, the x-axis represents the independent variable (e.g., time, categories) and the y-axis represents the dependent variable (e.g., numerical values). The data points on the chart are plotted and connected by lines, allowing you to see the overall trend, fluctuations, or changes in the data over the given time period or categories.",
                    "What does an upward/downward trend indicate?": "An upward trend in a line chart shows an increasing or positive relationship between the variables being plotted. It indicates that the dependent variable is generally increasing as the independent variable increases. Conversely, a downward trend shows a decreasing or negative relationship.",
                    "What can I infer from a flat or horizontal line?": "A flat or horizontal line in a line chart indicates no significant change or trend in the data. It suggests that the dependent variable remains relatively constant or does not show any clear relationship with the independent variable.",
                    "Can I compare multiple data series in a line chart?": "Yes, a line chart allows you to compare multiple data series on the same chart by plotting each series as a separate line with different colors or styles. This enables you to visualize and analyze the relationship or patterns among different variables or categories.",
                    "How can I customize the line chart?": "Most charting tools and libraries offer customization options for line charts. You can modify the appearance, such as changing line colors, styles, thickness, adding data markers, and adjusting the axes labels and scales. Additionally, you can include annotations, legends, and other interactive features to enhance the chart's readability and interactivity."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with OHLC:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['open'], name='Open'))
                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['low'], name='Low'))
                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['high'], name='High'))
                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['close'], name='Close'))

                    fig.update_layout(
                        title="OHLC Prices",
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )

                    st.write(fig)

                with col2:

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is an OHLC chart?": "An OHLC chart, also known as a bar chart, is a type of financial chart that represents the price movement of an asset, such as stocks or currencies, over a specific time period. It displays the opening, high, low, and closing prices of the asset for each time interval.",
                    "How do I interpret an OHLC chart?": "Each bar on the chart represents a specific time period (e.g., a day, an hour) and consists of four points: the opening price (represented by a horizontal line on the left), the highest price reached (top of the bar), the lowest price reached (bottom of the bar), and the closing price (represented by a horizontal line on the right). The length of the vertical line (bar) provides insights into the price range and volatility during the time period.",
                    "What does a long/short bar indicate?": "A long bar indicates a significant price movement during the time period, reflecting strong buying or selling pressure. On the other hand, a short bar suggests a relatively small price movement and potentially indecisive market conditions.",
                    "How can I identify bullish or bearish bars?": "In an OHLC chart, a bullish bar is usually represented by a green or white bar. It indicates that the closing price is higher than the opening price, suggesting a positive price movement. Conversely, a bearish bar is typically represented by a red or black bar, indicating that the closing price is lower than the opening price, suggesting a negative price movement.",
                    "Can I customize the appearance of an OHLC chart?": "Yes, many charting platforms and tools allow you to customize the appearance of OHLC charts. You can adjust the colors, styles, and widths of the bars, as well as add additional technical indicators or overlays to enhance your analysis, such as moving averages, volume bars, or trendlines.",
                    "How can I use OHLC data for analysis?": "OHLC data is commonly used for technical analysis to identify patterns, trends, and potential trading opportunities. Traders often look for patterns like doji, hammer, engulfing, or harami to make decisions. Additionally, OHLC data can be used in conjunction with other indicators, such as moving averages or oscillators, to further analyze market dynamics."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Histogram:
                col1, col2 = st.columns([10, 2])

                with col1:
                    # Create trace for histogram of daily returns
                    trace = go.Histogram(x=daily_returns, nbinsx=50, histnorm='probability', opacity=0.5,
                                         name='Daily Returns')

                    # Create layout
                    layout = go.Layout(title='Histogram of Stock Daily Returns', xaxis=dict(title='Daily Returns'),
                                       yaxis=dict(title='Frequency'))

                    # Create figure object and add trace and layout
                    fig = go.Figure(data=[trace], layout=layout)

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a returns histogram?": "A returns histogram is a graphical representation that displays the distribution of returns for a given dataset. It provides insights into the frequency and magnitude of returns observed in the data, allowing you to analyze the volatility or risk associated with an asset or investment strategy.",
                    "How do I interpret a returns histogram?": "In a returns histogram, the x-axis represents the range of returns, divided into bins or intervals, while the y-axis represents the frequency or count of occurrences within each bin. The height of each bar represents the number of observations falling within a specific range of returns. A wider or more spread-out histogram suggests a higher variability or dispersion of returns, while a narrower histogram indicates a more concentrated or less volatile distribution.",
                    "What can I infer from a skewness in the histogram?": "Skewness in a returns histogram refers to the asymmetry of the distribution. A positive skewness indicates a longer tail on the right side of the histogram, suggesting a higher frequency of positive returns or a potential for large positive outliers. Conversely, a negative skewness indicates a longer tail on the left side, indicating a higher frequency of negative returns or potential for large negative outliers.",
                    "How can I identify the shape of the distribution?": "The shape of a returns histogram can provide insights into the underlying distribution. Common shapes include symmetric bell-shaped (normal or Gaussian), skewed, bimodal, or fat-tailed distributions. These shapes can help you understand the characteristics and behavior of the returns data, such as whether it follows a known statistical distribution or exhibits specific patterns or anomalies.",
                    "How can I use a returns histogram in analysis?": "Returns histograms are commonly used in finance and investment analysis to assess risk, evaluate investment strategies, and identify abnormal return patterns. They can help you understand the potential range and likelihood of returns, evaluate the performance of investments relative to a benchmark, and support decision-making in portfolio management or risk assessment."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Increase_Decrease:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = px.line(dataset, x=dataset.index, y="close", color="Increase_Decrease")

                    fig.update_layout(
                        title="Close Prices - Increase/Decrease",
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is an Increase Decrease chart?": "An Increase Decrease chart, also known as an Up Down chart or a Step chart, is a type of chart that visually represents the increase and decrease in values over a given time period or category. It focuses on showcasing the direction and magnitude of changes rather than the specific values.",
                    "How do I interpret an Increase Decrease chart?": "In an Increase Decrease chart, the x-axis represents the time period or categories, while the y-axis typically represents the magnitude or scale of the values being plotted. Instead of using continuous lines or bars, this chart uses vertical steps or connected blocks to represent changes. The upward steps indicate an increase in values, while the downward steps represent a decrease.",
                    "What does a larger step indicate?": "A larger step in an Increase Decrease chart indicates a greater change in values over the given time period or category. It signifies a more significant increase or decrease in the corresponding data compared to smaller steps.",
                    "Can I compare multiple data series in an Increase Decrease chart?": "Yes, an Increase Decrease chart allows you to compare multiple data series by plotting them on the same chart using different colors or styles. This enables you to visually compare the changes in values across different categories or time periods and identify trends or patterns.",
                    "How can I customize the appearance of an Increase Decrease chart?": "Most charting libraries and tools provide options to customize the appearance of Increase Decrease charts. You can adjust the colors, thickness, or styles of the steps or blocks, modify the axes labels and scales, and add additional annotations or visual elements to enhance the clarity and readability of the chart.",
                    "What types of data are suitable for an Increase Decrease chart?": "Increase Decrease charts are particularly useful for representing categorical data or discrete values that exhibit clear increase and decrease patterns. They are commonly used in various domains, including finance, stock market analysis, project management, and other areas where changes in values or progress tracking are important."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Increase_Decrease_Count:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = px.histogram(ticker, x="Increase_Decrease")

                    fig.update_layout(
                        title="Increase/Decrease Count",
                        xaxis_title="Increase/Decrease",
                        yaxis_title="Count"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))
                faq = {
                    "What is an Increase Decrease Count chart?": "An Increase Decrease Count chart is a type of chart that visually represents the count or frequency of increase and decrease events over a given time period or category. It provides insights into the number of occurrences of upward and downward movements rather than the specific values associated with them.",
                    "How do I interpret an Increase Decrease Count chart?": "In an Increase Decrease Count chart, the x-axis represents the time period or categories, while the y-axis represents the count or frequency of increase and decrease events. The chart displays vertical bars or steps, where the upward bars indicate the count of increase events, and the downward bars represent the count of decrease events.",
                    "What does a taller bar indicate?": "A taller bar in an Increase Decrease Count chart indicates a higher count or frequency of increase or decrease events over the given time period or category. It represents a greater number of occurrences of upward or downward movements compared to shorter bars.",
                    "Can I compare multiple data series in an Increase Decrease Count chart?": "Yes, an Increase Decrease Count chart allows you to compare multiple data series by plotting them on the same chart using different colors or styles. This enables you to visually compare the count of increase and decrease events across different categories or time periods and identify patterns or trends.",
                    "How can I customize the appearance of an Increase Decrease Count chart?": "Most charting libraries and tools provide options to customize the appearance of Increase Decrease Count charts. You can adjust the colors, thickness, or styles of the bars or steps, modify the axes labels and scales, and add additional annotations or visual elements to enhance the clarity and readability of the chart.",
                    "What types of data are suitable for an Increase Decrease Count chart?": "Increase Decrease Count charts are useful for analyzing datasets that involve counting events of increase and decrease. They are commonly used in various fields such as finance, stock market analysis, sales analysis, and other areas where the frequency of upward and downward movements is of interest."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Scatter:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=ticker['open'], y=ticker['close'], mode='markers'))

                    fig.update_layout(
                        title="Open vs. Close Scatter Plot",
                        xaxis_title="Open Price",
                        yaxis_title="Close Price"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a scatter plot chart?": "A scatter plot chart is a type of chart that displays individual data points as markers on a two-dimensional plane. It is used to visualize the relationship or correlation between two variables. Each data point is represented by a marker, and the position of the marker on the chart corresponds to the values of the two variables being plotted.",
                    "How do I interpret a scatter plot chart?": "In a scatter plot chart, the x-axis represents one variable, while the y-axis represents the other variable. The position of each data point on the chart indicates the values of the two variables for that specific data point. By analyzing the distribution, clustering, or pattern of the data points, you can infer the relationship between the variables, such as positive or negative correlation, clusters, outliers, or trends.",
                    "What does the density of data points indicate?": "The density of data points in a scatter plot chart provides insights into the concentration or frequency of observations within specific regions of the chart. Higher density indicates a larger number of data points in that area, while lower density suggests sparser observations. The density of data points can reveal patterns, clusters, or trends in the relationship between the variables.",
                    "Can I customize the appearance of a scatter plot chart?": "Yes, most charting libraries and tools provide options to customize the appearance of scatter plot charts. You can modify the marker style, size, color, or transparency, adjust the axes labels and scales, add annotations, or include additional visual elements such as trend lines or regression lines to enhance the chart's interpretability and aesthetics.",
                    "How can I identify correlation or patterns in a scatter plot chart?": "In a scatter plot chart, you can visually assess the correlation between variables by observing the general trend or pattern of the data points. If the points tend to form a positive slope or curve, it indicates a positive correlation. Conversely, a negative slope or scattered distribution suggests a negative correlation. You can also use statistical measures or techniques, such as calculating correlation coefficients or fitting regression models, to quantify and validate the observed relationships.",
                    "What types of data are suitable for a scatter plot chart?": "Scatter plot charts are commonly used when working with continuous or numeric data. They are useful for visualizing and exploring relationships, correlations, clusters, or outliers in various domains, including scientific research, finance, marketing, and social sciences, among others."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

            with Volume:
                col1, col2 = st.columns([10, 2])

                with col1:
                    fig = go.Figure()

                    fig.add_trace(
                        go.Bar(
                            x=ticker.index,
                            y=ticker['volume'],
                            name='Volume',
                            marker_color=ticker['VolumePositive'].map({True: 'green', False: 'red'}),
                            opacity=0.4
                        )
                    )

                    fig.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Daily Volume',
                        title=f"{tickerSymbol} Volume"
                    )

                    st.write(fig)

                with col2:
                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq = {
                    "What is a volume chart?": "A volume chart is a type of financial chart that represents the trading volume or the number of shares or contracts traded over a specific time period. It provides insights into the liquidity, market activity, and buying or selling pressure for a particular asset or financial instrument.",
                    "How do I interpret a volume chart?": "In a volume chart, the x-axis represents the time period, while the y-axis represents the trading volume. Each bar or column on the chart represents the volume of shares or contracts traded during a specific time interval. By analyzing the height or length of the bars, you can identify periods of high or low trading activity and gauge the market sentiment.",
                    "What does a taller bar indicate?": "A taller bar in a volume chart indicates a higher trading volume for the corresponding time interval. It suggests increased market activity, higher liquidity, and potentially greater interest or participation from traders or investors.",
                    "Can I compare volume with price movements?": "Yes, volume charts are often used in conjunction with other types of financial charts, such as candlestick charts or line charts, to analyze the relationship between trading volume and price movements. By comparing the volume bars with the corresponding price movements, you can identify potential correlations, divergences, or patterns that may provide insights into market trends or reversals.",
                    "How can I customize the appearance of a volume chart?": "Most charting platforms and tools provide options to customize the appearance of volume charts. You can adjust the color, thickness, or style of the volume bars, modify the axes labels and scales, and add additional technical indicators or overlays, such as moving averages or volume-based oscillators, to enhance your analysis.",
                    "What types of data are suitable for a volume chart?": "Volume charts are primarily used in the analysis of financial markets, such as stocks, futures, or currencies, where trading volume is readily available. They are particularly useful for understanding market dynamics, identifying potential trends, reversals, or price support/resistance levels, and confirming or questioning the validity of price movements."
                }

                for question, answer in faq.items():
                    with st.expander(question):
                        st.write(answer)

        with Technical:

            Moving_Average, RSI, Accumulation_Distribution, Moving_Summation, Bollinger_Bands, Acceleration_Bands = st.tabs(
                ["Moving Average", "RSI", "Accumulation Distribution", "Moving Summation", "Bollinger Bands",
                 "Acceleration_Bands"])

            with Moving_Average:

                col1, col2 = st.columns([10, 2])
                with col1:

                    # Create the chart
                    selected_ma_indices = st.multiselect(
                        "Select Moving Averages to display",
                        options=["5 MA", "14 MA", "50 MA", "100 MA", "200 MA"],
                        default=["5 MA", "14 MA", "50 MA", "100 MA", "200 MA"]
                    )

                    fig_2 = go.Figure()

                    if "5 MA" in selected_ma_indices:
                        fig_2.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["Moving Average (5)"], name="5 MA",
                                       line=dict(color="blue")))

                    if "14 MA" in selected_ma_indices:
                        fig_2.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["Moving Average (14)"], name="14 MA",
                                       line=dict(color="red")))

                    if "50 MA" in selected_ma_indices:
                        fig_2.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["Moving Average (50)"], name="50 MA",
                                       line=dict(color="green")))

                    if "100 MA" in selected_ma_indices:
                        fig_2.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["Moving Average (100)"], name="100 MA",
                                       line=dict(color="yellow")))

                    if "200 MA" in selected_ma_indices:
                        fig_2.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["Moving Average (200)"], name="200 MA",
                                       line=dict(color="pink")))

                    # Customize the chart
                    fig_2.update_layout(
                        title="Exponetial Moving Average (MA)",
                        xaxis_title="Date",
                        yaxis_title="MA",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )

                    # Show the chart
                    st.write(fig_2)

                with col2:

                    # Create the chart
                    selected_ma_indices = st.select_slider(
                        'Select MA time period',
                        options=['5', '14', '50', '100', '200'])

                    if "5" in selected_ma_indices:
                        today_price = ticker['Moving Average (5)'].tail(1)
                        price_5 = ticker['Moving Average (5)'].iloc[-5]
                        price_10 = ticker['Moving Average (5)'].iloc[-10]

                        diff = ticker['Moving Average (5)'].iloc[-1] - ticker['Moving Average (5)'].iloc[-2]
                        price_change = (diff / ticker['Moving Average (5)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['Moving Average (5)'].iloc[-1] - ticker['Moving Average (5)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['Moving Average (5)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['Moving Average (5)'].iloc[-1] - ticker['Moving Average (5)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['Moving Average (5)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "14" in selected_ma_indices:
                        today_price = ticker['Moving Average (14)'].tail(1)
                        price_5 = ticker['Moving Average (14)'].iloc[-5]
                        price_10 = ticker['Moving Average (14)'].iloc[-10]

                        diff = ticker['Moving Average (14)'].iloc[-1] - ticker['Moving Average (14)'].iloc[-2]
                        price_change = (diff / ticker['Moving Average (14)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['Moving Average (14)'].iloc[-1] - ticker['Moving Average (14)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['Moving Average (14)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['Moving Average (14)'].iloc[-1] - ticker['Moving Average (14)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['Moving Average (14)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "50" in selected_ma_indices:
                        today_price = ticker['Moving Average (50)'].tail(1)
                        price_5 = ticker['Moving Average (50)'].iloc[-5]
                        price_10 = ticker['Moving Average (50)'].iloc[-10]

                        diff = ticker['Moving Average (50)'].iloc[-1] - ticker['Moving Average (50)'].iloc[-2]
                        price_change = (diff / ticker['Moving Average (50)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['Moving Average (50)'].iloc[-1] - ticker['Moving Average (50)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['Moving Average (50)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['Moving Average (50)'].iloc[-1] - ticker['Moving Average (50)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['Moving Average (50)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "100" in selected_ma_indices:
                        today_price = ticker['Moving Average (100)'].tail(1)
                        price_5 = ticker['Moving Average (100)'].iloc[-5]
                        price_10 = ticker['Moving Average (100)'].iloc[-10]

                        diff = ticker['Moving Average (100)'].iloc[-1] - ticker['Moving Average (100)'].iloc[-2]
                        price_change = (diff / ticker['Moving Average (100)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['Moving Average (100)'].iloc[-1] - ticker['Moving Average (100)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['Moving Average (100)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['Moving Average (100)'].iloc[-1] - ticker['Moving Average (100)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['Moving Average (100)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "200" in selected_ma_indices:
                        today_price = ticker['Moving Average (200)'].tail(1)
                        price_5 = ticker['Moving Average (200)'].iloc[-5]
                        price_10 = ticker['Moving Average (200)'].iloc[-10]

                        diff = ticker['Moving Average (200)'].iloc[-1] - ticker['Moving Average (200)'].iloc[-2]
                        price_change = (diff / ticker['Moving Average (200)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['Moving Average (200)'].iloc[-1] - ticker['Moving Average (200)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['Moving Average (200)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['Moving Average (200)'].iloc[-1] - ticker['Moving Average (200)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['Moving Average (200)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_moving_average = {
                    "What is a moving average?": "A moving average is a commonly used technical indicator that smooths out price data over a specified time period. It calculates the average price over that period and is plotted as a line on a chart. Moving averages help identify trends, potential support and resistance levels, and generate buy/sell signals.",
                    "How do I interpret a moving average?": "When the price moves above the moving average, it may indicate an uptrend, while a price below the moving average may indicate a downtrend. Additionally, crossovers between different moving averages (e.g., a shorter-term crossing above a longer-term) can provide buy or sell signals. Traders often use moving averages in conjunction with other technical indicators to confirm trends and improve trading decisions.",
                    "What are the commonly used types of moving averages?": "Some commonly used moving averages include the simple moving average (SMA), which gives equal weight to each data point, and the exponential moving average (EMA), which places more weight on recent data points. Other types include weighted moving averages and displaced moving averages, each with their own calculation methods and characteristics.",
                    "Can I customize the parameters of a moving average?": "Yes, the parameters of a moving average can be customized based on your analysis requirements. This includes selecting the time period (number of data points) for the moving average, choosing the type of moving average (e.g., SMA or EMA), and adjusting the visualization settings such as line color, thickness, or style.",
                    "How can I use multiple moving averages together?": "Using multiple moving averages of different time periods can provide additional insights. For example, the crossing of shorter-term and longer-term moving averages (e.g., 50-day and 200-day) is often used to identify potential trend reversals or confirm the strength of a prevailing trend. Experimenting with different combinations can help determine the most effective moving averages for your analysis."
                }

                for question, answer in faq_moving_average.items():
                    with st.expander(question):
                        st.write(answer)

            with RSI:

                col1, col2 = st.columns([10, 2])

                with col1:
                    # Create the chart
                    selected_rs_indices = st.multiselect(
                        "Select RSI lines to display",
                        options=["5 RSI", "14 RSI", "50 RSI", "100 RSI", "200 RSI"],
                        default=["5 RSI", "14 RSI", "50 RSI", "100 RSI", "200 RSI"]
                    )

                    fig_1 = go.Figure()

                    if "5 RSI" in selected_rs_indices:
                        fig_1.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["RSI (5)"], name="5 RSI", line=dict(color="blue")))

                    if "14 RSI" in selected_rs_indices:
                        fig_1.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["RSI (14)"], name="14 RSI", line=dict(color="red")))

                    if "50 RSI" in selected_rs_indices:
                        fig_1.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["RSI (50)"], name="50 RSI", line=dict(color="green")))

                    if "100 RSI" in selected_rs_indices:
                        fig_1.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["RSI (100)"], name="100 RSI",
                                       line=dict(color="yellow")))

                    if "200 RSI" in selected_rs_indices:
                        fig_1.add_trace(
                            go.Scatter(x=ticker.index, y=ticker["RSI (200)"], name="200 RSI", line=dict(color="pink")))

                    # Add horizontal lines at 30 and 70 (common oversold and overbought levels)
                    fig_1.add_shape(type="line", x0=ticker.index[0], x1=ticker.index[-1], y0=30, y1=30, yref="y",
                                    xref="x",
                                    line=dict(color="gray", dash="dash"))
                    fig_1.add_shape(type="line", x0=ticker.index[0], x1=ticker.index[-1], y0=70, y1=70, yref="y",
                                    xref="x",
                                    line=dict(color="gray", dash="dash"))

                    # Customize the chart
                    fig_1.update_layout(
                        title="Relative Strength Index (RSI)",
                        xaxis_title="Date",
                        yaxis_title="RSI",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )

                    # Show the chart
                    st.write(fig_1)

                with col2:

                    # Create the chart
                    selected_ma_indices = st.select_slider(
                        'Select RSI time period',
                        options=['5', '14', '50', '100', '200'])

                    if "5" in selected_ma_indices:
                        today_price = ticker['RSI (5)'].tail(1)
                        price_5 = ticker['RSI (5)'].iloc[-5]
                        price_10 = ticker['RSI (5)'].iloc[-10]

                        diff = ticker['RSI (5)'].iloc[-1] - ticker['RSI (5)'].iloc[-2]
                        price_change = (diff / ticker['RSI (5)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['RSI (5)'].iloc[-1] - ticker['RSI (5)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['RSI (5)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['RSI (5)'].iloc[-1] - ticker['RSI (5)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['RSI (5)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "14" in selected_ma_indices:
                        today_price = ticker['RSI (14)'].tail(1)
                        price_5 = ticker['RSI (14)'].iloc[-5]
                        price_10 = ticker['RSI (14)'].iloc[-10]

                        diff = ticker['RSI (14)'].iloc[-1] - ticker['RSI (14)'].iloc[-2]
                        price_change = (diff / ticker['RSI (14)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['RSI (14)'].iloc[-1] - ticker['RSI (14)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['RSI (14)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['RSI (14)'].iloc[-1] - ticker['RSI (14)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['RSI (14)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "50" in selected_ma_indices:
                        today_price = ticker['RSI (50)'].tail(1)
                        price_5 = ticker['RSI (50)'].iloc[-5]
                        price_10 = ticker['RSI (50)'].iloc[-10]

                        diff = ticker['RSI (50)'].iloc[-1] - ticker['RSI (50)'].iloc[-2]
                        price_change = (diff / ticker['RSI (50)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['RSI (50)'].iloc[-1] - ticker['RSI (50)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['RSI (50)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['RSI (50)'].iloc[-1] - ticker['RSI (50)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['RSI (50)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "100" in selected_ma_indices:
                        today_price = ticker['RSI (100)'].tail(1)
                        price_5 = ticker['RSI (100)'].iloc[-5]
                        price_10 = ticker['RSI (100)'].iloc[-10]

                        diff = ticker['RSI (100)'].iloc[-1] - ticker['RSI (100)'].iloc[-2]
                        price_change = (diff / ticker['RSI (100)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['RSI (100)'].iloc[-1] - ticker['RSI (100)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['RSI (100)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['RSI (100)'].iloc[-1] - ticker['RSI (100)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['RSI (100)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                    if "200" in selected_ma_indices:
                        today_price = ticker['RSI (200)'].tail(1)
                        price_5 = ticker['RSI (200)'].iloc[-5]
                        price_10 = ticker['RSI (200)'].iloc[-10]

                        diff = ticker['RSI (200)'].iloc[-1] - ticker['RSI (200)'].iloc[-2]
                        price_change = (diff / ticker['RSI (200)'].iloc[-2]) * 100
                        round_price_change = price_change.round(2)
                        formatted_price_change = f"{round_price_change}%"

                        diff_5 = ticker['RSI (200)'].iloc[-1] - ticker['RSI (200)'].iloc[-5]
                        price_change_5 = (diff_5 / ticker['RSI (200)'].iloc[-2]) * 100
                        round_price_change_5 = price_change_5.round(2)
                        formatted_price_change_5 = f"{round_price_change_5}%"

                        diff_10 = ticker['RSI (200)'].iloc[-1] - ticker['RSI (200)'].iloc[-10]
                        price_change_10 = (diff_10 / ticker['RSI (200)'].iloc[-2]) * 100
                        round_price_change_10 = price_change_10.round(2)
                        formatted_price_change_10 = f"{round_price_change_10}%"

                        col2.metric("1 Day Change", today_price, formatted_price_change)
                        col2.metric("5 Day Change", price_5, formatted_price_change_5)
                        col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_rsi = {
                    "What is the Relative Strength Index (RSI)?": "The Relative Strength Index (RSI) is a popular momentum oscillator used in technical analysis to measure the speed and change of price movements. It oscillates between 0 and 100 and is typically displayed as a line chart. RSI is used to identify overbought and oversold levels, as well as potential trend reversals.",
                    "How do I interpret the RSI values?": "RSI values above 70 are generally considered overbought, indicating a potentially overextended rally and a higher probability of a price correction or reversal. Conversely, RSI values below 30 are typically considered oversold, suggesting a potentially oversold condition and a higher probability of a price bounce or reversal. Traders often use these levels, along with chart patterns or other indicators, to generate buy/sell signals.",
                    "What is the calculation formula for RSI?": "The RSI calculation involves comparing the average gains and average losses over a specified time period. The formula calculates the Relative Strength (RS), which is the ratio of average gains to average losses. RSI is then derived from RS and expressed as a value between 0 and 100 using the formula RSI = 100 - (100 / (1 + RS)). The time period for RSI calculation is often set to 14 periods, but it can be adjusted to suit different analysis needs.",
                    "Can I customize the RSI parameters?": "Yes, you can customize the RSI parameters based on your analysis preferences. This includes adjusting the time period for RSI calculation, selecting different overbought and oversold levels (such as 70 and 30, or different levels depending on market conditions), and modifying the visualization settings of the RSI line chart, such as color or thickness.",
                    "What other indicators can I use in conjunction with RSI?": "RSI is often used in combination with other indicators to confirm signals and improve analysis. Some common approaches include using RSI in conjunction with trendlines, chart patterns (e.g., head and shoulders), moving averages, or volume indicators. The combination of multiple indicators can provide a more comprehensive analysis of price trends and potential reversals."
                }

                for question, answer in faq_rsi.items():
                    with st.expander(question):
                        st.write(answer)

            with Accumulation_Distribution:

                col1, col2 = st.columns([9, 3])
                with col1:
                    # Create figure with subplots
                    fig = go.Figure()

                    # Add trace for Accumulation Distribution Line
                    fig.add_trace(
                        go.Scatter(x=ticker.index, y=ticker['ADL'], name='Accumulation Distribution Line')
                    )

                    # Update layout
                    fig.update_layout(
                        title='Accumulation Distribution Line',
                        yaxis_title='Accumulation Distribution Line',
                        xaxis_title='Date',
                        height=500,
                        showlegend=True
                    )

                    st.write(fig)

                with col2:
                    today_price = ticker['ADL'].tail(1)
                    price_5 = ticker['ADL'].iloc[-5]
                    price_10 = ticker['ADL'].iloc[-10]

                    diff = ticker['ADL'].iloc[-1] - ticker['ADL'].iloc[-2]
                    price_change = (diff / ticker['ADL'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['ADL'].iloc[-1] - ticker['ADL'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['ADL'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['ADL'].iloc[-1] - ticker['ADL'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['ADL'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_accumulation_distribution = {
                    "What is Accumulation Distribution?": "Accumulation Distribution is a technical analysis indicator that combines volume and price data to assess the flow of money into or out of an asset. It aims to identify divergences between volume and price movements, which can signal potential trend reversals.",
                    "How is Accumulation Distribution calculated?": "The Accumulation Distribution Line is calculated by considering the relationship between the closing price and the trading range (high and low) for a given period. It incorporates volume to weigh the price movements and determine whether buying or selling pressure is dominant. The formula involves accumulating or distributing values based on the relationship between the close price and the range, adjusted by volume.",
                    "How do I interpret Accumulation Distribution?": "Increasing values of Accumulation Distribution indicate positive buying pressure, suggesting that the asset is being accumulated. Conversely, decreasing values indicate negative selling pressure, suggesting distribution or selling of the asset. Divergences between the Accumulation Distribution Line and the price trend can indicate potential trend reversals or changes in market sentiment.",
                    "Can I customize the parameters of Accumulation Distribution?": "The parameters of Accumulation Distribution can be customized based on your analysis needs. This includes adjusting the time period over which the indicator is calculated, modifying the visualization settings of the line chart, and combining Accumulation Distribution with other technical indicators to improve analysis and signal confirmation.",
                    "How can I use Accumulation Distribution in trading strategies?": "Accumulation Distribution can be used in various trading strategies. For example, traders may look for divergences between price and Accumulation Distribution, where the price is making higher highs or lower lows, while the indicator shows the opposite. This can signal potential trend reversals or changes in market sentiment. Additionally, combining Accumulation Distribution with other indicators, such as moving averages or trendlines, can enhance the effectiveness of trading strategies."
                }

                for question, answer in faq_accumulation_distribution.items():
                    with st.expander(question):
                        st.write(answer)

            with Moving_Summation:

                col1, col2 = st.columns([9, 3])
                with col1:
                    # Create trace for Moving Summation
                    trace = go.Scatter(x=ticker.index, y=ticker['sum'], name='Moving Summation')

                    # Create layout
                    layout = go.Layout(
                        title='Moving Summation',
                        yaxis_title='Moving Summation',
                        xaxis_title='Date',
                        height=500,
                        showlegend=True
                    )

                    # Create figure and add trace and layout
                    fig = go.Figure(data=[trace], layout=layout)

                    # Show the chart
                    st.write(fig)

                with col2:
                    today_price = ticker['sum'].tail(1)
                    price_5 = ticker['sum'].iloc[-5]
                    price_10 = ticker['sum'].iloc[-10]

                    diff = ticker['sum'].iloc[-1] - ticker['sum'].iloc[-2]
                    price_change = (diff / ticker['sum'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['sum'].iloc[-1] - ticker['sum'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['sum'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['sum'].iloc[-1] - ticker['sum'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['sum'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_moving_summation = {
                    "What is Moving Summation?": "Moving Summation is a technical analysis indicator that calculates the sum of a specific data series over a given time period. It provides insights into the cumulative total of the data points and helps identify trends or patterns within the series.",
                    "How is Moving Summation calculated?": "Moving Summation is calculated by summing the values of a specific data series over a defined number of periods. The sum is then plotted as a line on a chart, representing the cumulative total of the data points over time.",
                    "How do I interpret Moving Summation?": "An increasing Moving Summation indicates that the data series is generally trending upwards or accumulating over time. Conversely, a decreasing Moving Summation suggests a downtrend or depletion of the data series. Traders and analysts may use Moving Summation to identify potential trend reversals or confirm the strength of an existing trend.",
                    "Can I customize the parameters of Moving Summation?": "Yes, you can customize the parameters of Moving Summation based on your analysis requirements. This includes selecting the time period (number of data points) for the Moving Summation calculation, adjusting the visualization settings of the line chart (such as color or thickness), and combining Moving Summation with other technical indicators for more comprehensive analysis.",
                    "How can Moving Summation be used in trading strategies?": "Moving Summation can be used in various trading strategies. For example, traders may look for crossovers between Moving Summation and price to identify potential trend reversals or confirm the strength of a prevailing trend. Additionally, Moving Summation can be used in conjunction with other indicators, such as moving averages or oscillators, to enhance trading signals and improve decision-making."
                }

                for question, answer in faq_moving_summation.items():
                    with st.expander(question):
                        st.write(answer)

            with Bollinger_Bands:

                col1, col2 = st.columns([9, 3])
                with col1:
                    n = 20
                    MA = pd.Series(ticker['close'].rolling(n).mean())
                    STD = pd.Series(ticker['close'].rolling(n).std())
                    bb1 = MA + 2 * STD
                    ticker['Upper Bollinger Band'] = pd.Series(bb1)
                    bb2 = MA - 2 * STD
                    ticker['Lower Bollinger Band'] = pd.Series(bb2)

                    trace1 = go.Scatter(x=ticker.index, y=ticker['close'], name='Close')
                    trace2 = go.Scatter(x=ticker.index, y=ticker['Upper Bollinger Band'], name='Upper Bollinger Band')
                    trace3 = go.Scatter(x=ticker.index, y=ticker['Lower Bollinger Band'], name='Lower Bollinger Band')

                    data = [trace1, trace2, trace3]

                    layout = go.Layout(
                        title='Stock Closing Price of Bollinger Bands',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Price'),
                        legend=dict(x=0, y=1)
                    )

                    fig = go.Figure(data=data, layout=layout)

                    st.write(fig)

                with col2:
                    today_price = ticker['close'].tail(1)
                    price_5 = ticker['close'].iloc[-5]
                    price_10 = ticker['close'].iloc[-10]

                    diff = ticker['close'].iloc[-1] - ticker['close'].iloc[-2]
                    price_change = (diff / ticker['close'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['close'].iloc[-1] - ticker['close'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['close'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['close'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_bollinger_bands = {
                    "What are Bollinger Bands?": "Bollinger Bands are a popular technical analysis tool that consists of a central moving average line and two outer bands that represent the volatility of an asset's price. The outer bands are typically calculated as standard deviations away from the moving average, forming a dynamic range around the average.",
                    "How are Bollinger Bands calculated?": "Bollinger Bands are calculated by first establishing a central moving average, commonly the simple moving average (SMA), over a specified time period. The upper band is then calculated by adding a multiple of the standard deviation to the moving average, while the lower band is derived by subtracting the same multiple of the standard deviation. The most common multiple used is 2, resulting in bands that encompass approximately 95% of price data.",
                    "How do I interpret Bollinger Bands?": "When the price moves towards the upper band, it may indicate that the asset is overbought or overvalued, potentially signaling a reversal or price pullback. Conversely, when the price approaches the lower band, it may suggest that the asset is oversold or undervalued, potentially signaling a price bounce or reversal. Traders often look for price interactions with the bands, along with other indicators or chart patterns, to generate trading signals.",
                    "Can I customize the parameters of Bollinger Bands?": "Yes, Bollinger Bands can be customized based on your analysis preferences. This includes selecting the time period for the moving average calculation, adjusting the standard deviation multiplier for the outer bands, and modifying the visualization settings of the bands, such as line color, thickness, or style.",
                    "What other indicators can be used with Bollinger Bands?": "Bollinger Bands are often used in conjunction with other indicators to confirm signals and improve analysis. For example, traders may combine Bollinger Bands with oscillators like the Relative Strength Index (RSI) to identify overbought or oversold conditions within the bands. Additionally, chart patterns, candlestick patterns, or trendlines can provide additional insights when used alongside Bollinger Bands."
                }

                for question, answer in faq_bollinger_bands.items():
                    with st.expander(question):
                        st.write(answer)

            with Acceleration_Bands:

                col1, col2 = st.columns([9, 3])

                with col1:
                    n = 7
                    UBB = ticker['high'] * (1 + 4 * (ticker['high'] - ticker['low']) / (ticker['high'] + ticker['low']))
                    ticker['Upper_Band'] = UBB.rolling(n, center=False).mean()
                    ticker['Middle_Band'] = ticker['close'].rolling(n).mean()
                    LBB = ticker['low'] * (1 - 4 * (ticker['high'] - ticker['low']) / (ticker['high'] + ticker['low']))
                    ticker['Lower_Band'] = LBB.rolling(n, center=False).mean()

                    trace1 = go.Scatter(x=ticker.index, y=ticker['close'], name='Close')
                    trace2 = go.Scatter(x=ticker.index, y=ticker['Upper_Band'], name='Upper Band')
                    trace3 = go.Scatter(x=ticker.index, y=ticker['Middle_Band'], name='Middle Band')
                    trace4 = go.Scatter(x=ticker.index, y=ticker['Lower_Band'], name='Lower Band')

                    data = [trace1, trace2, trace3, trace4]

                    layout = go.Layout(
                        title=f"Stock Closing Price of {n}-Day Acceleration Bands",
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Price'),
                        legend=dict(x=0, y=1)
                    )

                    fig = go.Figure(data=data, layout=layout)

                    st.write(fig)

                with col2:
                    st.write("Price Change")

                    today_price = ticker['close'].tail(1)
                    price_5 = ticker['close'].iloc[-5]
                    price_10 = ticker['close'].iloc[-10]

                    diff = ticker['close'].iloc[-1] - ticker['close'].iloc[-2]
                    price_change = (diff / ticker['close'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['close'].iloc[-1] - ticker['close'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['close'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['close'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_acceleration_bands = {
                    "What are Acceleration Bands?": "Acceleration Bands are a technical analysis tool designed to capture price trends and volatility. They consist of three bands plotted around a moving average, including an upper band, a lower band, and a centerline. The width of the bands expands or contracts based on market volatility.",
                    "How are Acceleration Bands calculated?": "Acceleration Bands are calculated by adding and subtracting a fixed percentage (called the Acceleration Factor) from a moving average. The upper band is derived by multiplying the Acceleration Factor by the moving average and adding it to the average, while the lower band is obtained by subtracting the product of the Acceleration Factor and the moving average from the average. The centerline represents the moving average.",
                    "How do I interpret Acceleration Bands?": "When the price moves outside the outer bands, it suggests a potential acceleration or increase in volatility. Traders often interpret breakouts above the upper band as a signal of an upward trend continuation, while breakouts below the lower band may indicate a potential downward trend continuation. The width of the bands can provide insights into the current market volatility.",
                    "Can I customize the parameters of Acceleration Bands?": "Yes, you can customize the parameters of Acceleration Bands based on your analysis preferences. This includes selecting the time period for the moving average, adjusting the Acceleration Factor to control the width of the bands, and modifying the visualization settings of the bands, such as line color, thickness, or style.",
                    "How can Acceleration Bands be used in trading strategies?": "Acceleration Bands can be used in various trading strategies. Traders may look for breakouts above or below the bands as potential entry or exit points, depending on the direction of the trend. Additionally, combining Acceleration Bands with other indicators, such as oscillators or trendlines, can provide further confirmation and enhance trading signals."
                }

                for question, answer in faq_acceleration_bands.items():
                    with st.expander(question):
                        st.write(answer)

        with Quantitative:

            Standard_Deviation, Variance, Residual_Risk, Geometric_Mean, HistoGram_Returns, Log_Returns = st.tabs(
                ["Standard Deviation", "Variance", "Residual Risk", "Geometric Mean", "Histogram Returns",
                 "Log Returns"])

            with Standard_Deviation:
                col1, col2 = st.columns([10, 2])
                with col1:
                    def std(returns):
                        stock_std = returns.std()
                        return stock_std


                    # Compute the running Standard Deviation
                    running = [std(returns[i - 90:i]) for i in range(90, len(returns))]
                    # Create the scatter plot
                    scatter = go.Scatter(x=ticker.index[90:-100], y=running[:-100], name='Standard Deviation')
                    # Create the figure and add the trace
                    fig = go.Figure(data=[scatter])
                    # Set the figure title and axis labels
                    fig.update_layout(title='ticker' + ' Standard Deviation', xaxis_title='Date',
                                      yaxis_title='Standard Deviation')
                    # Display the plot using Streamlit
                    st.plotly_chart(fig)

                with col2:
                    st.write("Price Change")

                    today_price = ticker['close'].tail(1)
                    price_5 = ticker['close'].iloc[-5]
                    price_10 = ticker['close'].iloc[-10]

                    diff = ticker['close'].iloc[-1] - ticker['close'].iloc[-2]
                    price_change = (diff / ticker['close'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['close'].iloc[-1] - ticker['close'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['close'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['close'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_std_dev = {
                    "What is Standard Deviation in the stock market?": "Standard Deviation is a statistical measure that quantifies the dispersion or variability of returns for a stock or portfolio. It provides an indication of the stock's price volatility and risk. A higher standard deviation suggests a wider range of price fluctuations, indicating higher volatility and potentially higher risk.",
                    "How is Standard Deviation calculated for stock market returns?": "Standard Deviation for stock market returns is calculated as the square root of the variance. It involves calculating the difference between each individual return and the average return, squaring the differences, averaging the squared differences, and taking the square root of the result.",
                    "How do I interpret Standard Deviation in the stock market?": "A higher Standard Deviation suggests that the stock's returns have a wider dispersion, indicating greater price volatility and potentially higher risk. A lower Standard Deviation indicates more stable and less volatile returns. Investors often use Standard Deviation as a risk measure when assessing the suitability of an investment or comparing the risk levels of different stocks or portfolios.",
                    "Can I use Standard Deviation to compare stocks?": "Yes, Standard Deviation can be used to compare the risk levels of different stocks. By comparing the Standard Deviation of returns, investors can assess which stocks have higher or lower price volatility. However, it's important to consider other factors and perform a comprehensive analysis when comparing stocks, as Standard Deviation alone may not provide a complete picture of a stock's risk and suitability for investment."
                }

                for question, answer in faq_std_dev.items():
                    with st.expander(question):
                        st.write(answer)

            with Variance:
                col1, col2 = st.columns([10, 2])
                with col1:
                    def var(returns_1):
                        stock_var = returns_1.var()
                        return stock_var


                    running = [var(returns[i - 90:i]) for i in range(90, len(returns))]
                    # Create the scatter plot
                    scatter = go.Scatter(x=ticker.index[90:-100], y=running[:-100], name='Variance')
                    # Create the figure and add the trace
                    fig = go.Figure(data=[scatter])
                    # Set the figure title and axis labels
                    fig.update_layout(title='Chart' + ' Variance', xaxis_title='Date', yaxis_title='Variance')
                    # Display the plot using Streamlit
                    st.plotly_chart(fig)

                with col2:
                    st.write("Price Change")

                    today_price = ticker['close'].tail(1)
                    price_5 = ticker['close'].iloc[-5]
                    price_10 = ticker['close'].iloc[-10]

                    diff = ticker['close'].iloc[-1] - ticker['close'].iloc[-2]
                    price_change = (diff / ticker['close'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['close'].iloc[-1] - ticker['close'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['close'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['close'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_variance = {
                    "What is Variance in the stock market?": "Variance is a statistical measure that quantifies the average squared deviation of stock market returns from their mean. It provides insights into the dispersion or variability of returns and is commonly used as a risk measure. A higher variance suggests a wider range of price fluctuations and potentially higher risk.",
                    "How is Variance calculated for stock market returns?": "Variance for stock market returns is calculated by taking the average of the squared differences between each individual return and the mean return. It involves squaring the differences, summing the squared differences, and dividing the sum by the number of observations.",
                    "How do I interpret Variance in the stock market?": "A higher Variance indicates a greater dispersion of returns, suggesting higher price volatility and potentially higher risk. A lower Variance suggests more stable and less volatile returns. Investors often use Variance as a risk measure when assessing the suitability of an investment or comparing the risk levels of different stocks or portfolios.",
                    "Can I use Variance to compare stocks?": "Yes, Variance can be used to compare the risk levels of different stocks. By comparing the Variance of returns, investors can assess which stocks have higher or lower price volatility. However, it's important to consider other factors and perform a comprehensive analysis when comparing stocks, as Variance alone may not provide a complete picture of a stock's risk and suitability for investment."
                }

                for question, answer in faq_variance.items():
                    with st.expander(question):
                        st.write(answer)

            with Residual_Risk:
                col1, col2 = st.columns([10, 2])

                with col1:
                    def residual_risk(stock_returns, market_returns):
                        m = np.matrix([stock_returns, market_returns])
                        beta = np.cov(m)[0][1] / np.std(market_returns)
                        rr = stock_returns.std() - beta
                        return rr


                    # Create the scatter plot
                    scatter = go.Scatter(x=ticker.index, y=ticker['close'].pct_change(), name='Stock daily returns')
                    # Create the figure and add the trace
                    fig = go.Figure(data=[scatter])
                    # Set the figure title and axis labels
                    fig.update_layout(title='Stock Daily Returns', xaxis_title='Date', yaxis_title='Returns')
                    # Display the plot using Streamlit
                    st.plotly_chart(fig)

                with col2:
                    st.write("Price Change")
                    today_price = ticker['close'].tail(1)
                    price_5 = ticker['close'].iloc[-5]
                    price_10 = ticker['close'].iloc[-10]

                    diff = ticker['close'].iloc[-1] - ticker['close'].iloc[-2]
                    price_change = (diff / ticker['close'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['close'].iloc[-1] - ticker['close'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['close'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['close'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_residual_risk = {
                    "What is Residual Risk in the stock market?": "Residual Risk, also known as unsystematic risk or specific risk, refers to the risk that is specific to an individual stock or portfolio and cannot be diversified away. It represents the portion of risk that is unrelated to the overall market movements or systematic risk factors.",
                    "What factors contribute to Residual Risk?": "Residual Risk can arise from company-specific factors, such as management decisions, competitive landscape, regulatory changes, or unforeseen events. It is unique to each stock or portfolio and cannot be eliminated through diversification.",
                    "How is Residual Risk different from Systematic Risk?": "Residual Risk is different from Systematic Risk, which refers to the risk that affects the overall market or a specific market segment. Systematic Risk factors include macroeconomic conditions, interest rates, geopolitical events, and market sentiment. Residual Risk is specific to an individual stock or portfolio and can be managed through careful security selection and diversification.",
                    "How can I mitigate Residual Risk?": "While Residual Risk cannot be eliminated entirely, it can be mitigated through diversification. By holding a diversified portfolio of stocks across different sectors and industries, investors can reduce the impact of company-specific events on their overall investment performance. Additionally, conducting thorough fundamental analysis and staying informed about the companies in the portfolio can help manage Residual Risk."
                }

                for question, answer in faq_residual_risk.items():
                    with st.expander(question):
                        st.write(answer)

            with HistoGram_Returns:
                # Create Log Returns
                ticker['Log_Returns'] = np.log(ticker['close'].shift(-1)) - np.log(ticker['close'])

                # Compute the mean and standard deviation of the log returns
                mu = ticker['Log_Returns'].mean()
                sigma = ticker['Log_Returns'].std(ddof=1)

                # Create a dataframe to hold the density data
                density = pd.DataFrame()
                density['x'] = np.arange(ticker['Log_Returns'].min() - 0.01, ticker['Log_Returns'].max() + 0.01, 0.001)
                density['pdf'] = norm.pdf(density['x'], mu, sigma)

                # Create a histogram of the log returns
                histogram = go.Histogram(x=ticker['Log_Returns'], nbinsx=50, marker_color='blue')

                # Create a line chart of the density function
                density_chart = go.Scatter(x=density['x'], y=density['pdf'], mode='lines',
                                           line=dict(color='red', width=2))

                # Combine the histogram and density charts into a single plot
                layout = go.Layout(title='Log Returns Density', xaxis=dict(title='Log Returns'),
                                   yaxis=dict(title='Density'))
                fig = go.Figure(data=[histogram, density_chart], layout=layout)

                st.plotly_chart(fig)

            faq_histogram_returns = {
                "What are Histogram Returns in the stock market?": "Histogram Returns are a visual representation of the distribution of stock market returns. It provides insights into the frequency and magnitude of returns within specific intervals or bins.",
                "How are Histogram Returns calculated for stock market data?": "Histogram Returns are calculated by grouping the returns into intervals or bins and counting the number of occurrences within each interval. The resulting counts are then plotted as bars on a histogram chart.",
                "How do I interpret Histogram Returns in the stock market?": "Histogram Returns provide a visual representation of the distribution of returns. The shape of the histogram can reveal insights into the skewness, kurtosis, and potential outliers in the return distribution. It helps investors understand the range of potential returns and assess the risk associated with an investment.",
                "Can I use Histogram Returns to assess risk?": "Yes, Histogram Returns can be used to assess the risk associated with an investment. A wider or more spread-out histogram indicates a higher level of return variability or volatility, suggesting higher risk. Conversely, a narrower or more concentrated histogram suggests lower return variability and potentially lower risk. Investors can use Histogram Returns to gain insights into the potential range of returns and make informed risk assessments."
            }

            for question, answer in faq_histogram_returns.items():
                with st.expander(question):
                    st.write(answer)

            with Log_Returns:

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=ticker.index, y=ticker['Log_Returns'], mode='lines'))

                fig.update_layout(title='Stock Log Returns', xaxis_title='Date', yaxis_title='Log Returns')
                fig.add_shape(dict(type='line', x0=ticker.index.min(), y0=0, x1=ticker.index.max(), y1=0,
                                   line=dict(color='red', width=2, dash='dash')))

                st.write(fig)

            faq_log_returns = {
                "What are Log Returns in the stock market?": "Log Returns, also known as logarithmic returns or continuously compounded returns, measure the proportional change in the price or value of an asset over a specific period. They provide a standardized way to calculate and compare returns over different timeframes.",
                "How are Log Returns calculated for stock market data?": "Log Returns are calculated using the natural logarithm of the ratio between the final price (or value) and the initial price (or value) of the asset. The formula for Log Returns is log(final price / initial price).",
                "How do I interpret Log Returns in the stock market?": "Log Returns provide a measure of the relative change or growth rate of an asset's price or value over time. They allow for direct comparisons of returns across different timeframes and provide a more accurate representation of the actual percentage change. Log Returns are often used in financial models and analysis as they exhibit desirable mathematical properties.",
                "Can I use Log Returns for risk assessment?": "Yes, Log Returns can be used for risk assessment in the stock market. They are commonly used in quantitative finance and risk management models due to their desirable properties, such as their normality assumption and the ability to work with additive processes. Log Returns allow for a more accurate representation of the distribution of returns and can be used to estimate risk measures such as standard deviation or Value-at-Risk (VaR)."
            }

            for question, answer in faq_log_returns.items():
                with st.expander(question):
                    st.write(answer)

            with Geometric_Mean:
                col1, col2 = st.columns([8, 2])

                with col1:
                    from scipy.stats import gmean, norm, stats

                    n = 10
                    ticker['Geometric_Return'] = pd.Series(ticker['close']).rolling(n).apply(gmean)

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['Geometric_Return'],
                                             mode='lines', name='Geometric Return',
                                             line=dict(color='red')))

                    fig.update_layout(title='Geometric Return',
                                      xaxis_title='Date',
                                      yaxis_title='Geometric Return',
                                      legend=dict(x=0, y=1, traceorder='normal'))

                    st.plotly_chart(fig)

                with col2:
                    st.write("Geometric Return Change")
                    today_price = ticker['Geometric_Return'].tail(1).round(2)
                    price_5 = ticker['Geometric_Return'].iloc[-5].round(2)
                    price_10 = ticker['Geometric_Return'].iloc[-10].round(2)

                    diff = ticker['Geometric_Return'].iloc[-1] - ticker['Geometric_Return'].iloc[-2]
                    price_change = (diff / ticker['Geometric_Return'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['Geometric_Return'].iloc[-1] - ticker['Geometric_Return'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['Geometric_Return'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['Geometric_Return'].iloc[-1] - ticker['Geometric_Return'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['Geometric_Return'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_geometric_mean = {
                    "What is Geometric Mean in the stock market?": "Geometric Mean is a statistical measure used to calculate the average rate of return for an investment over multiple periods. It provides insights into the compounded growth rate of an investment and is often used to assess long-term performance.",
                    "How is Geometric Mean calculated for stock market returns?": "Geometric Mean is calculated by taking the nth root of the product of the individual period returns, where n is the number of periods. The individual period returns are usually expressed as 1 plus the periodic rate of return.",
                    "How do I interpret Geometric Mean in the stock market?": "Geometric Mean represents the average compounded growth rate of an investment over multiple periods. It provides a better measure of long-term performance compared to arithmetic mean, especially when dealing with returns that compound over time. Investors often use Geometric Mean to assess the historical performance of an investment or compare the average returns of different stocks or portfolios.",
                    "What are the limitations of using Geometric Mean?": "One limitation of Geometric Mean is that it assumes that the investment compounds at a constant rate over time, which may not always be the case in real-world scenarios. Additionally, Geometric Mean does not account for other factors such as risk or volatility. Therefore, it should be used in conjunction with other performance measures and factors when making investment decisions."
                }

                for question, answer in faq_geometric_mean.items():
                    with st.expander(question):
                        st.write(answer)

        with Risk:
            ATR, Returns, Realised_Volatility, Relative_Volatility, GBM = st.tabs(
                ["ATR", "Returns", "Realised Volatility", "Relative Volatility", "GBM"])

            with ATR:
                col1, col2 = st.columns([8, 2])

                with col1:
                    # Create figure with subplots
                    fig = go.Figure()

                    # Add trace for ATR
                    fig.add_trace(
                        go.Scatter(x=ticker.index, y=ticker['ATR'], name='ATR')
                    )

                    # Add horizontal line at y=1
                    fig.add_shape(
                        type='line',
                        x0=ticker.index[0],
                        y0=1,
                        x1=ticker.index[-1],
                        y1=1,
                        line=dict(color='blue', dash='dash')
                    )

                    # Update layout
                    fig.update_layout(
                        title='Average True Range',
                        yaxis_title='Average True Range',
                        xaxis_title='Date',
                        height=500,
                        showlegend=True
                    )

                    st.plotly_chart(fig)

                with col2:
                    st.write("ATR Change")
                    today_price = ticker['ATR'].tail(1).round(2)
                    price_5 = ticker['ATR'].iloc[-5].round(2)
                    price_10 = ticker['ATR'].iloc[-10].round(2)

                    diff = ticker['ATR'].iloc[-1] - ticker['ATR'].iloc[-2]
                    price_change = (diff / ticker['ATR'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['ATR'].iloc[-1] - ticker['ATR'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['ATR'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['ATR'].iloc[-1] - ticker['ATR'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['ATR'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_average_true_range = {
                    "What is Average True Range (ATR) in the stock market?": "Average True Range (ATR) is a technical analysis indicator that measures the volatility or price range of an asset over a specific period. It provides insights into the average size of price movements and can help identify potential trend reversals or changes in market volatility.",
                    "How is Average True Range calculated for stock market data?": "Average True Range is calculated using the True Range values, which represent the greatest of the following: the difference between the current high and low, the absolute value of the difference between the current high and the previous close, or the absolute value of the difference between the current low and the previous close. ATR is typically calculated as an average of the True Range values over a specified time period.",
                    "How do I interpret Average True Range in the stock market?": "Higher values of Average True Range indicate greater price volatility, suggesting larger price movements and potentially higher risk. Lower values suggest lower volatility and potentially calmer market conditions. Traders often use Average True Range to set stop-loss levels, determine position sizes, or identify potential breakouts.",
                    "Can I customize the parameters of Average True Range?": "Yes, the parameters of Average True Range can be customized based on your analysis needs. This includes selecting the time period over which the True Range values are calculated and adjusting the visualization settings of the Average True Range line, such as color or thickness."
                }

                for question, answer in faq_average_true_range.items():
                    with st.expander(question):
                        st.write(answer)

            with Returns:
                col1, col2 = st.columns([8, 2])

                with col1:
                    # Create trace for daily returns
                    trace = go.Scatter(x=daily_returns.index, y=daily_returns.values, mode='lines',
                                       name='Daily Returns')

                    # Create layout
                    layout = go.Layout(title='Stock Daily Returns', xaxis=dict(title='Date'),
                                       yaxis=dict(title='Daily Returns'))

                    # Create figure object and add trace and layout
                    fig = go.Figure(data=[trace], layout=layout)

                    st.write(fig)

                with col2:
                    # Stock Price Chart

                    today_price = ticker['close'].tail(1)
                    price_5 = ticker['close'].iloc[-5]
                    price_10 = ticker['close'].iloc[-10]

                    diff = ticker['close'].iloc[-1] - ticker['close'].iloc[-2]
                    price_change = (diff / ticker['close'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['close'].iloc[-1] - ticker['close'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['close'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['close'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)



            with Realised_Volatility:

                col1, col2 = st.columns([10, 2])

                with col1:
                    import math
                    n = 20
                    rets = ticker['close'].pct_change().dropna()
                    std = rets.rolling(n).std()

                    historical_vol_annually = std * math.sqrt(252)
                    ticker['RV'] = 100 * historical_vol_annually

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['RV'],
                                             mode='lines', name='Realised Volatility'))

                    fig.add_shape(type='line',
                                  x0=ticker.index[0], y0=ticker['RV'].mean(),
                                  x1=ticker.index[-1], y1=ticker['RV'].mean(),
                                  line=dict(color='red', width=1, dash='dash'))

                    fig.update_layout(title='Realised Volatility',
                                      xaxis_title='Date',
                                      yaxis_title='Realised Volatility',
                                      legend=dict(x=0, y=1, traceorder='normal'))

                    st.plotly_chart(fig)

                with col2:
                    st.write("Volatility Change")
                    today_price = ticker['RV'].tail(1).round(2)
                    price_5 = ticker['RV'].iloc[-5].round(2)
                    price_10 = ticker['RV'].iloc[-10].round(2)

                    diff = ticker['RV'].iloc[-1] - ticker['RV'].iloc[-2]
                    price_change = (diff / ticker['RV'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['RV'].iloc[-1] - ticker['RV'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['RV'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['RV'].iloc[-1] - ticker['RV'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['RV'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("1 Day Change", today_price, formatted_price_change)
                    col2.metric("5 Day Change", price_5, formatted_price_change_5)
                    col2.metric("10 Day Change", price_10, formatted_price_change_10)

                faq_realized_volatility = {
                    "What is Realized Volatility in the stock market?": "Realized Volatility is a measure of the actual volatility or price fluctuations experienced by a stock or market over a specific time period. It is based on historical price data and provides insights into the level of risk associated with the asset.",
                    "How is Realized Volatility calculated for stock market data?": "Realized Volatility is calculated by measuring the standard deviation of the stock's or market's returns over a specified time period. It quantifies the dispersion or variability of the returns, indicating the level of price volatility experienced during that period.",
                    "How do I interpret Realized Volatility in the stock market?": "Higher values of Realized Volatility indicate greater price volatility and potentially higher risk. Lower values suggest lower volatility and potentially calmer market conditions. Investors and traders use Realized Volatility to assess the level of risk associated with an investment, determine appropriate risk management strategies, and set expectations for potential price movements.",
                    "Can I use Realized Volatility to compare different stocks?": "Yes, Realized Volatility can be used to compare the volatility levels of different stocks. By comparing the Realized Volatility values, investors can assess which stocks have higher or lower price volatility. However, it's important to consider other factors and perform a comprehensive analysis when comparing stocks, as Realized Volatility alone may not provide a complete picture of a stock's risk and suitability for investment."
                }

                for question, answer in faq_realized_volatility.items():
                    with st.expander(question):
                        st.write(answer)

            with Relative_Volatility:
                col1, col2 = st.columns([10, 2])

                with col1:
                    n = 14  # Number of periods
                    change = ticker['close'].diff(1)
                    ticker['Gain'] = change.mask(change < 0, 0)
                    ticker['Loss'] = abs(change.mask(change > 0, 0))
                    ticker['AVG_Gain'] = ticker.Gain.rolling(n).std()
                    ticker['AVG_Loss'] = ticker.Loss.rolling(n).std()
                    ticker['RS'] = ticker['AVG_Gain'] / ticker['AVG_Loss']
                    ticker['RVI'] = 100 - (100 / (1 + ticker['RS']))

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['RVI'],
                                             mode='lines', name='Relative Volatility Index'))

                    fig.add_annotation(x=ticker.index[30], y=70, text='Overbought',
                                       showarrow=False, font=dict(size=14))
                    fig.add_annotation(x=ticker.index[30], y=30, text='Oversold',
                                       showarrow=False, font=dict(size=14))

                    fig.add_shape(type='line', x0=ticker.index[0], y0=70, x1=ticker.index[-1], y1=70,
                                  line=dict(color='red', width=1, dash='dash'))
                    fig.add_shape(type='line', x0=ticker.index[0], y0=30, x1=ticker.index[-1], y1=30,
                                  line=dict(color='red', width=1, dash='dash'))

                    fig.update_layout(title='Relative Volatility Index',
                                      xaxis_title='Date',
                                      yaxis_title='Volume',
                                      legend=dict(x=0, y=1, traceorder='normal'))

                    st.plotly_chart(fig)

                with col2:
                    st.write("Volatility Change")
                    today_price = ticker['RV'].tail(1).round(2)
                    price_5 = ticker['RV'].iloc[-5].round(2)
                    price_10 = ticker['RV'].iloc[-10].round(2)

                    diff = ticker['RV'].iloc[-1] - ticker['RV'].iloc[-2]
                    price_change = (diff / ticker['RV'].iloc[-2]) * 100
                    round_price_change = price_change.round(2)
                    formatted_price_change = f"{round_price_change}%"

                    diff_5 = ticker['RV'].iloc[-1] - ticker['RV'].iloc[-5]
                    price_change_5 = (diff_5 / ticker['RV'].iloc[-2]) * 100
                    round_price_change_5 = price_change_5.round(2)
                    formatted_price_change_5 = f"{round_price_change_5}%"

                    diff_10 = ticker['RV'].iloc[-1] - ticker['RV'].iloc[-10]
                    price_change_10 = (diff_10 / ticker['RV'].iloc[-2]) * 100
                    round_price_change_10 = price_change_10.round(2)
                    formatted_price_change_10 = f"{round_price_change_10}%"

                    col2.metric("Current Level", f"{today_price.item():.2f}", formatted_price_change)
                    col2.metric("5 Day Change", f"{diff_5.item():.2f}", formatted_price_change_5)
                    col2.metric("10 Day Change", f"{diff_10.item():.2f}", formatted_price_change_10)

                faq_relative_volatility = {
                    "What is Relative Volatility in the stock market?": "Relative Volatility is a measure used to compare the volatility of a stock or asset to the overall market or a benchmark index. It provides insights into whether the stock is more or less volatile than the market as a whole.",
                    "How is Relative Volatility calculated for stock market data?": "Relative Volatility is typically calculated as the ratio of the stock's volatility (such as standard deviation of returns) to the volatility of the overall market or benchmark index over a specific time period. It quantifies the stock's volatility relative to the broader market.",
                    "How do I interpret Relative Volatility in the stock market?": "A Relative Volatility value greater than 1 indicates that the stock is more volatile than the market, suggesting higher risk. A value less than 1 suggests that the stock is less volatile than the market, indicating potentially lower risk. Relative Volatility can help investors assess the risk level of a stock in comparison to the market or benchmark, aiding in portfolio diversification and risk management decisions.",
                    "Can I use Relative Volatility for stock selection?": "Yes, Relative Volatility can be used as a factor in stock selection. Investors may look for stocks with lower Relative Volatility as they may offer a more stable investment compared to stocks with higher Relative Volatility. However, it's important to consider other factors, such as fundamentals and market conditions, when selecting stocks for investment."
                }

                for question, answer in faq_relative_volatility.items():
                    with st.expander(question):
                        st.write(answer)

        with Maths:
            Standard, Kurtosis = st.tabs(
                ["Standard Deviation", "Kurtosis"])

            with Standard:

                col1, col2 = st.columns([10, 2])

                with col1:
                    title = f"{tickerSymbol} Standard Deviation ({tickerTime} timeframe)"

                    # Calculate Standard Deviation
                    price_std = ticker['close'].rolling(window=5).std()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=ticker.index, y=price_std, mode='lines', name='Standard Deviation'))
                    fig.update_layout(title=title, yaxis=dict(title='Standard Deviation'))

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    today_price = ticker['close'].tail(1).item()
                    previous_close = ticker['close'].iloc[-2]
                    percent_change = ((today_price - previous_close) / previous_close) * 100
                    formatted_price_changes = {'1 Day Change': f"{percent_change:.2f}%"}

                    price_changes = {
                        '5 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-5],
                        '10 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    }

                    for period, price_change in price_changes.items():
                        percent_change = (price_change / ticker['close'].iloc[-2]) * 100
                        formatted_price_change = f"{percent_change:.2f}%"
                        formatted_price_changes[period] = formatted_price_change

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq_std_dev = {
                    "What is Standard Deviation in the stock market?": "Standard Deviation is a statistical measure that quantifies the dispersion or variability of returns for a stock or portfolio. It provides an indication of the stock's price volatility and risk. A higher standard deviation suggests a wider range of price fluctuations, indicating higher volatility and potentially higher risk.",
                    "How is Standard Deviation calculated for stock market returns?": "Standard Deviation for stock market returns is calculated as the square root of the variance. It involves calculating the difference between each individual return and the average return, squaring the differences, averaging the squared differences, and taking the square root of the result.",
                    "How do I interpret Standard Deviation in the stock market?": "A higher Standard Deviation suggests that the stock's returns have a wider dispersion, indicating greater price volatility and potentially higher risk. A lower Standard Deviation indicates more stable and less volatile returns. Investors often use Standard Deviation as a risk measure when assessing the suitability of an investment or comparing the risk levels of different stocks or portfolios.",
                    "Can I use Standard Deviation to compare stocks?": "Yes, Standard Deviation can be used to compare the risk levels of different stocks. By comparing the Standard Deviation of returns, investors can assess which stocks have higher or lower price volatility. However, it's important to consider other factors and perform a comprehensive analysis when comparing stocks, as Standard Deviation alone may not provide a complete picture of a stock's risk and suitability for investment."
                }

                for question, answer in faq_std_dev.items():
                    with st.expander(question):
                        st.write(answer)

            with Kurtosis:

                import numpy as np

                col1, col2 = st.columns([10, 2])

                with col1:
                    title = f"{tickerSymbol} Kurtosis ({tickerTime} timeframe)"

                    # Calculate Kurtosis
                    price_kurtosis = ticker['close'].rolling(window=5).kurt()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=ticker.index, y=price_kurtosis, mode='lines', name='Kurtosis'))
                    fig.update_layout(title=title, yaxis=dict(title='Kurtosis'))

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    today_price = ticker['close'].tail(1).item()
                    previous_close = ticker['close'].iloc[-2]
                    percent_change = ((today_price - previous_close) / previous_close) * 100
                    formatted_price_changes = {'1 Day Change': f"{percent_change:.2f}%"}

                    price_changes = {
                        '5 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-5],
                        '10 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    }

                    for period, price_change in price_changes.items():
                        percent_change = (price_change / ticker['close'].iloc[-2]) * 100
                        formatted_price_change = f"{percent_change:.2f}%"
                        formatted_price_changes[period] = formatted_price_change

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq_kurtosis = {
                    "What is Kurtosis in the stock market?": "Kurtosis is a statistical measure that quantifies the shape of the distribution of stock market returns. It provides insights into the tails of the distribution, indicating the presence of outliers or extreme values.",
                    "How is Kurtosis calculated for stock market returns?": "Kurtosis is calculated by comparing the distribution of returns to the normal distribution. Positive kurtosis indicates a distribution with heavier tails and potentially more outliers than the normal distribution, while negative kurtosis suggests a distribution with lighter tails and fewer outliers.",
                    "How do I interpret Kurtosis in the stock market?": "Higher values of Kurtosis indicate a distribution with heavier tails and potentially more extreme returns, suggesting higher risk or volatility. Lower values suggest a distribution with lighter tails and potentially fewer extreme returns. Kurtosis helps investors understand the shape and characteristics of the return distribution, aiding in risk assessment and portfolio analysis.",
                    "Can I use Kurtosis to identify outliers in stock market returns?": "Yes, Kurtosis can be used to identify potential outliers or extreme returns in stock market data. Positive kurtosis values suggest the presence of outliers in the tails of the distribution. By identifying and analyzing these outliers, investors can gain insights into potential risk factors or unique events that may impact stock performance."
                }

                for question, answer in faq_kurtosis.items():
                    with st.expander(question):
                        st.write(answer)

        with Physics:

            Momentum, Chaos_Theory = st.tabs(
                ["Momentum", "Chaos Theory"])

            import plotly.graph_objects as go
            import streamlit as st

            with Momentum:

                col1, col2 = st.columns([10, 2])

                with col1:
                    title = f"{tickerSymbol} Momentum ({tickerTime} timeframe)"

                    # Calculate Momentum
                    momentum = (ticker['close'] - ticker['close'].shift(5)) / ticker['close'].shift(5) * 100

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=ticker.index, y=momentum, mode='lines', name='Momentum'))
                    fig.update_layout(title=title, yaxis=dict(title='Momentum (%)'))

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    today_price = ticker['close'].tail(1).item()
                    previous_close = ticker['close'].iloc[-2]
                    percent_change = ((today_price - previous_close) / previous_close) * 100
                    formatted_price_changes = {'1 Day Change': f"{percent_change:.2f}%"}

                    price_changes = {
                        '5 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-5],
                        '10 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    }

                    for period, price_change in price_changes.items():
                        percent_change = (price_change / ticker['close'].iloc[-2]) * 100
                        formatted_price_change = f"{percent_change:.2f}%"
                        formatted_price_changes[period] = formatted_price_change

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq_momentum = {
                    "What is Momentum in the stock market?": "Momentum is a technical analysis indicator that measures the rate of change in a stock's price over a specified time period. It provides insights into the strength and direction of the price trend.",
                    "How is Momentum calculated for stock market data?": "Momentum is calculated by subtracting the closing price of the stock a certain number of periods ago from the current closing price. The resulting value indicates the price change over that period.",
                    "How do I interpret Momentum in the stock market?": "Positive Momentum values indicate an upward price trend, suggesting buying pressure and potential opportunities for further price appreciation. Negative Momentum values indicate a downward price trend, suggesting selling pressure and potential opportunities for further price decline. Traders often use Momentum to identify potential trend reversals, confirm the strength of an existing trend, or generate buy/sell signals.",
                    "Can I use Momentum to assess the strength of a stock's price trend?": "Yes, Momentum can be used to assess the strength and direction of a stock's price trend. Higher positive Momentum values indicate a stronger upward trend, while lower negative Momentum values indicate a stronger downward trend. By analyzing the Momentum values, investors can gain insights into the stock's price dynamics and make more informed trading decisions."
                }

                for question, answer in faq_momentum.items():
                    with st.expander(question):
                        st.write(answer)

            with Chaos_Theory:

                def calculate_chaos_oscillator(high, low):
                    fractal_high = high.rolling(window=5, center=True).max()
                    fractal_low = low.rolling(window=5, center=True).min()
                    chaos_oscillator = fractal_high - fractal_low
                    return chaos_oscillator

                col1, col2 = st.columns([10, 2])

                with col1:
                    title = f"{tickerSymbol} Chaos Theory Chart ({tickerTime} timeframe)"

                    # Calculate Chaos Oscillator
                    chaos_oscillator = calculate_chaos_oscillator(ticker['high'], ticker['low'])

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=ticker.index, y=chaos_oscillator, mode='lines', name='Chaos Oscillator'))
                    fig.update_layout(title=title, yaxis=dict(title='Chaos Oscillator'))

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    today_price = ticker['close'].tail(1).item()
                    previous_close = ticker['close'].iloc[-2]
                    percent_change = ((today_price - previous_close) / previous_close) * 100
                    formatted_price_changes = {'1 Day Change': f"{percent_change:.2f}%"}

                    price_changes = {
                        '5 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-5],
                        '10 Day Change': ticker['close'].iloc[-1] - ticker['close'].iloc[-10]
                    }

                    for period, price_change in price_changes.items():
                        percent_change = (price_change / ticker['close'].iloc[-2]) * 100
                        formatted_price_change = f"{percent_change:.2f}%"
                        formatted_price_changes[period] = formatted_price_change

                    col2.metric("Current Price", f"{today_price:.2f}", formatted_price_changes.get('1 Day Change', 'N/A'))
                    for period, price in zip(price_changes.keys(),
                                             [price_changes['5 Day Change'], price_changes['10 Day Change']]):
                        col2.metric(period, f"{price:.2f}", formatted_price_changes.get(period, 'N/A'))

                faq_chaos_theory = {
                    "What is Chaos Theory in the stock market?": "Chaos Theory is a mathematical concept that studies complex and dynamic systems, including financial markets. It explores the idea that seemingly random and unpredictable behavior in the markets may have underlying patterns or structures.",
                    "How does Chaos Theory relate to the stock market?": "Chaos Theory suggests that even in highly complex and seemingly chaotic systems like the stock market, there may be hidden patterns, relationships, or feedback loops that contribute to the overall behavior. It challenges the notion of pure randomness and explores the concept of deterministic chaos, where small changes or events can have significant and unpredictable impacts on the system.",
                    "What are some applications of Chaos Theory in the stock market?": "Chaos Theory has been applied in various ways to the stock market, including the study of price patterns, market cycles, and fractal analysis. It has been used to develop trading strategies based on the identification of patterns or signals derived from chaotic dynamics. However, it's important to note that Chaos Theory is a complex and evolving field, and its applications in the stock market are still subject to ongoing research and debate.",
                    "Can Chaos Theory predict stock market movements with certainty?": "No, Chaos Theory does not provide certainty in predicting stock market movements. While Chaos Theory offers insights into the potential presence of hidden patterns or structures in the markets, it does not provide a deterministic prediction of future prices. The stock market is influenced by numerous factors, including fundamental data, investor sentiment, and macroeconomic events, which makes it inherently unpredictable."
                }

                for question, answer in faq_chaos_theory.items():
                    with st.expander(question):
                        st.write(answer)


    except:
        # Prevent the error from propagating into your Streamlit app.
        pass

    # Set the timezone to GMT
    tz = pytz.timezone('GMT')

    # Get the current date and time in GMT
    now = datetime.datetime.now(tz=tz)

    # If today is a weekend, set the date to the previous Friday
    if now.weekday() >= 5:
        days_to_subtract = now.weekday() - 4
        date = now - datetime.timedelta(days=days_to_subtract)
    else:
        # Subtract one day and set the time to 23:00
        date = datetime.datetime.combine(now.date(), datetime.time(23)) - datetime.timedelta(days=1)

    # Convert the date and time to Eastern Time (ET)
    et_tz = pytz.timezone('US/Eastern')
    date_et = date.astimezone(et_tz)

    # Format the date as a string and print it
    date_str = date_et.strftime("Market data as of %Y-%m-%d %I:%M:%S %p GMT")
    st.write(date_str)

    if st.button("Logout"):
        # Remove the username from session state and redirect to login page
        del st.session_state["username"]
        st.experimental_rerun()
