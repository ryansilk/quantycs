import os
import webbrowser
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyEX as p
import streamlit as st
from keras.layers import Dense, LSTM as LSTMLayer
from keras.models import Sequential
from tqdm import tqdm

def display_subscription_message():
    st.write(
        "This is for premium users only, please login or subscribe to access our premium machine learning algorithms")

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

token = 'pk_94d120d039ca45a2b435d9e5a040515f'

pd.options.mode.chained_assignment = None
np.random.seed(0)

os.environ['SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL'] = 'True'

st.set_page_config(layout="wide")
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)

st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "username" not in st.session_state:

    display_subscription_message()
else:

    LSTM, Linear_Regression, Other = st.tabs(["LSTM", "Linear Regression", "How To Use"])

    with LSTM:
        pd.options.mode.chained_assignment = None
        np.random.seed(0)

        def calculate_rmse(y_true, y_pred):
            return np.sqrt(np.mean((y_true - y_pred) ** 2))

        def calculate_r2(y_true, y_pred):
            ssr = np.sum((y_true - y_pred) ** 2)
            sst = np.sum((y_true - np.mean(y_true)) ** 2)
            return 1 - (ssr / sst)

        def scale_data(data):
            min_val = np.min(data)
            max_val = np.max(data)
            return (data - min_val) / (max_val - min_val)

        def unscale_data(data, scaled_data):
            min_val = np.min(data)
            max_val = np.max(data)
            return scaled_data * (max_val - min_val) + min_val

        def predict_stock(stock, epochs, lstm_units, forecast_period, lookback_period):
            c = p.Client(api_token=token, version='stable')

            df = c.chartDF(symbol=stock, timeframe='2y')[['open', 'high', 'low', 'close', 'volume']]
            df = df[::-1]

            df = df.fillna(method='ffill')
            df = df.fillna(method='bfill')

            y = df['close'].values.reshape(-1, 1)

            y_scaled = scale_data(y)

            n_lookback = lookback_period
            n_forecast = forecast_period

            X = []
            Y = []

            for i in range(n_lookback, len(y_scaled) - n_forecast + 1):
                X.append(y_scaled[i - n_lookback: i].flatten())
                Y.append(y_scaled[i: i + n_forecast])

            X = np.array(X)
            Y = np.array(Y)

            model = Sequential()
            lstm_layer = LSTMLayer(units=lstm_units, activation='relu', return_sequences=True,
                                   input_shape=(n_lookback, 1))
            model.add(lstm_layer)
            model.add(LSTMLayer(units=lstm_units))
            model.add(Dense(n_forecast))

            model.compile(loss='mean_squared_error', optimizer='adam')

            for _ in tqdm(range(epochs), desc='Training epochs'):
                model.train_on_batch(X, Y)

            X_ = y_scaled[- n_lookback - n_forecast:-n_forecast].flatten()
            X_ = X_.reshape(1, -1)  # Reshape to 2D array
            Y_true = y_scaled[-n_forecast:]

            Y_pred_scaled = model.predict(X_, verbose=0).reshape(-1, 1)
            Y_pred = unscale_data(y, Y_pred_scaled)

            accuracy_rmse = calculate_rmse(Y_true, Y_pred)
            accuracy_r2 = calculate_r2(Y_true, Y_pred)

            df_future = pd.DataFrame(columns=['date', 'Actual', 'Forecast'])
            df_future['date'] = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=n_forecast)
            df_future['Forecast'] = Y_pred.flatten()
            df_future['Actual'] = np.nan

            return (stock, df_future, accuracy_rmse, accuracy_r2, df)


        def run_streamlit_app():
            st.title("Long Short Term Memory")

            # Load the Excel file
            excel_file = '/Users/ryansilk/PycharmProjects/MyQ_v1_dash/pages/Stock_List.xlsx'
            df = pd.read_excel(excel_file)

            options = df['symbol'].tolist()  # Replace 'Column_Name' with the actual column name from your Excel sheet

            stock = st.selectbox('Select a stock:', options, key='stock_selection')

            # Perform VLOOKUP to get the corresponding value
            value = df.loc[df['symbol'] == stock, 'name'].values[
                0]  # Replace 'Value_Column' with the actual column name containing the values

            st.write(value)

            epochs = st.slider("Number of Epochs", min_value=10, max_value=200, value=100, step=10,
                               key="lstm_epochs")
            lstm_units = st.slider("LSTM Units", min_value=10, max_value=100, value=50, step=10, key="lstm_units")
            forecast_period = st.slider("Forecast Period", min_value=10, max_value=30, value=20, step=5,
                                        key="lstm_forecast")
            lookback_period = st.slider("Lookback Period", min_value=30, max_value=90, value=60, step=10,
                                        key="lstm_lookback")

            if st.button("Predict", key="lstm_predict"):
                result = predict_stock(stock, epochs, lstm_units, forecast_period, lookback_period)
                stock_name, df_future, accuracy_rmse, accuracy_r2, df = result

                col97, col98, col99 = st.tabs(["Chart View", "Table of Results", "Accuracy", ])

                with col97:
                    # Plotting the chart using Plotly
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Actual'))
                    fig.add_trace(
                        go.Scatter(x=df_future['date'], y=df_future['Forecast'], mode='lines', name='Forecast'))
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Stock Price",
                        title="Stock Price Prediction",
                    )
                    st.plotly_chart(fig)

                with col98:
                    st.write("Forecast:")
                    st.dataframe(df_future)

                with col99:
                    st.write("RMSE:", round(accuracy_rmse, 2))  # Round RMSE to 2 decimal places
                    st.write("R2 Score:", round(accuracy_r2, 2))  # Round R2 Score to 2 decimal places


        if __name__ == '__main__':
            run_streamlit_app()

    with Linear_Regression:
        def predict_stock(stock, epochs, forecast_period, lookback_period):
            c = p.Client(api_token=token, version='stable')

            df = c.chartDF(symbol=stock, timeframe='2y')[['open', 'high', 'low', 'close', 'volume']]
            df = df[::-1]

            df = df.fillna(method='ffill')
            df = df.fillna(method='bfill')

            y = df['close'].values.reshape(-1, 1)

            y_scaled = scale_data(y)

            n_lookback = lookback_period
            n_forecast = forecast_period

            X = []
            Y = []

            for i in range(n_lookback, len(y_scaled) - n_forecast + 1):
                X.append(y_scaled[i - n_lookback: i])
                Y.append(y_scaled[i: i + n_forecast])

            X = np.array(X)
            Y = np.array(Y)

            X_ = X.reshape(-1, n_lookback)
            Y_true = Y.reshape(-1, n_forecast)

            # Manually calculate linear regression coefficients
            X_transpose = X_.T
            coefficients = np.linalg.inv(X_transpose @ X_) @ X_transpose @ Y_true

            # Predict the future values
            X_ = y_scaled[-n_lookback:].reshape(1, n_lookback)
            Y_pred_scaled = X_ @ coefficients
            Y_pred = unscale_data(y, Y_pred_scaled)

            accuracy_rmse = calculate_rmse(Y_true, Y_pred)
            accuracy_r2 = calculate_r2(Y_true, Y_pred)

            df_future = pd.DataFrame(columns=['date', 'Actual', 'Forecast'])
            df_future['date'] = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=n_forecast)
            df_future['Forecast'] = Y_pred.flatten()
            df_future['Actual'] = np.nan

            return (stock, df_future, accuracy_rmse, accuracy_r2, df)


        def run_streamlit_app():
            st.title("Linear Regression")

            # Load the Excel file
            excel_file = '/Users/ryansilk/PycharmProjects/MyQ_v1_dash/pages/Stock_List.xlsx'
            df = pd.read_excel(excel_file)

            options = df['symbol'].tolist()  # Replace 'Column_Name' with the actual column name from your Excel sheet

            stock = st.selectbox('Select a stock:', options, key='stock_selection_2')

            # Perform VLOOKUP to get the corresponding value
            value = df.loc[df['symbol'] == stock, 'name'].values[
                0]  # Replace 'Value_Column' with the actual column name containing the values

            st.write(value)

            epochs = st.slider("Number of Epochs", min_value=10, max_value=200, value=100, step=10,
                               key="linear_epochs")
            forecast_period = st.slider("Forecast Period", min_value=10, max_value=30, value=20, step=5,
                                        key="linear_forecast")
            lookback_period = st.slider("Lookback Period", min_value=30, max_value=90, value=60, step=10,
                                        key="linear_lookback")

            if st.button("Predict", key="linear_predict"):
                result = predict_stock(stock, epochs, forecast_period, lookback_period)
                stock_name, df_future, accuracy_rmse, accuracy_r2, df = result

                col197, col198, col199 = st.tabs(["Chart View", "Table of Results", "Accuracy", ])

                with col197:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Actual'))
                    fig.add_trace(
                        go.Scatter(x=df_future['date'], y=df_future['Forecast'], mode='lines', name='Forecast'))
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Stock Price",
                        title="Stock Price Prediction",
                    )
                    st.plotly_chart(fig)

                with col198:
                    st.write("Forecast:")
                    st.dataframe(df_future)

                with col199:
                    st.write("RMSE:", round(accuracy_rmse, 2))  # Round RMSE to 2 decimal places
                    st.write("R2 Score:", round(accuracy_r2, 2))  # Round R2 Score to 2 decimal places


        if __name__ == '__main__':
            run_streamlit_app()

    with Other:

        faq = {
            "What information do I need to provide?": "You need to enter a stock symbol (e.g., AAPL) and adjust the parameters: Number of Epochs, Forecast Period, and Lookback Period.",
            "What is the Number of Epochs?": "The Number of Epochs refers to the number of times the machine learning model will iterate over the training dataset during training.",
            "What is the Forecast Period?": "The Forecast Period is the number of future time steps for which the stock prices will be predicted.",
            "What is the Lookback Period?": "The Lookback Period is the number of past time steps that the model will consider to make predictions.",
            "How do I adjust the parameters?": "You can adjust the parameters using the sliders provided. Move the sliders to select the desired values.",
            "How do I start the prediction?": "Click on the 'Predict' button to start the prediction based on the entered stock symbol and selected parameters.",
            "What does the prediction result include?": "The prediction result includes the stock name, a dataframe showing the forecasted stock prices, the RMSE accuracy score, and the R2 score.",
            "What is the RMSE accuracy score?": "RMSE (Root Mean Square Error) is a measure of the average difference between the predicted and actual stock prices. It indicates the accuracy of the prediction.",
            "What is the R2 score?": "The R2 score, also known as the coefficient of determination, measures the proportion of the variance in the dependent variable (stock prices) that can be explained by the independent variables (input features). It ranges from 0 to 1, with 1 indicating a perfect fit."
        }

        st.title("FAQ - Machine Learning")

        for question, answer in faq.items():
            with st.expander(question):
                st.write(answer)
