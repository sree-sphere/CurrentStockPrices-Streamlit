import datetime
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import time

# Function to fetch stock data
def get_stock_data(symbol, start_date, end_date):
    try:
        ticker_data = yf.Ticker(symbol)
        # Add one day to the end date to make it inclusive
        end_date += datetime.timedelta(days=1)
        ticker_df = ticker_data.history(period="1d", start=start_date, end=end_date)
        return ticker_data, ticker_df
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

# Function to fetch live stock price
def get_live_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        return ticker.history(period='1d').iloc[-1]['Close']
    except Exception as e:
        st.error(f"Error fetching live price: {e}")
        return None

# Function to display stock data
def display_stock_data(ticker_data, ticker_df, live_price):
    if ticker_df is not None:
        # Calculate technical indicators
        ticker_df['MACD'] = ta.trend.macd(ticker_df['Close'])
        ticker_df['RSI'] = ta.momentum.rsi(ticker_df['Close'])

        # Display stock data
        st.write(f"📊 Stock Data")
        st.write(f"Date Range: {ticker_df.index[0].date()} - {ticker_df.index[-1].date()}")
        st.dataframe(ticker_df)

        # Display closing price chart with tooltip
        fig_close = go.Figure()
        fig_close.add_trace(go.Scatter(x=ticker_df.index, y=ticker_df["Close"], mode='lines', name='Close'))
        fig_close.update_layout(title=f"📈 Closing Price Chart",
                                xaxis_title='Date',
                                yaxis_title='Price',
                                hovermode='x',
                                showlegend=False)
        st.plotly_chart(fig_close, use_container_width=True)

        # Display volume chart with tooltip
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Scatter(x=ticker_df.index, y=ticker_df["Volume"], mode='lines', name='Volume'))
        fig_volume.update_layout(title=f"📉 Volume Chart",
                                  xaxis_title='Date',
                                  yaxis_title='Volume',
                                  hovermode='x',
                                  showlegend=False)
        st.plotly_chart(fig_volume, use_container_width=True)

        # Display MACD chart
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=ticker_df.index, y=ticker_df["MACD"], mode='lines', name='MACD'))
        fig_macd.update_layout(title=f"📊 MACD Chart",
                               xaxis_title='Date',
                               yaxis_title='MACD',
                               hovermode='x',
                               showlegend=False)
        st.plotly_chart(fig_macd, use_container_width=True)

        # Display RSI chart
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=ticker_df.index, y=ticker_df["RSI"], mode='lines', name='RSI'))
        fig_rsi.update_layout(title=f"📊 RSI Chart",
                              xaxis_title='Date',
                              yaxis_title='RSI',
                              hovermode='x',
                              showlegend=False)
        st.plotly_chart(fig_rsi, use_container_width=True)

        # Display candlestick chart
        st.write(f"🕯️ Candlestick Chart")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)
        fig.add_trace(go.Candlestick(x=ticker_df.index,
                                      open=ticker_df["Open"],
                                      high=ticker_df["High"],
                                      low=ticker_df["Low"],
                                      close=ticker_df["Close"]),
                      row=1, col=1)
        fig.add_trace(go.Bar(x=ticker_df.index, y=ticker_df["Volume"]), row=2, col=1)
        fig.update_layout(margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Additional information panel
        st.write("Additional Information:")
        if live_price is not None:
            st.write(f"Live Price (Today): {live_price:.2f}")
        else:
            st.warning("Live price not available.")
        st.write(f"Market Cap: {ticker_data.info['marketCap']:.2f}B")
        st.write(f"P/E Ratio: {ticker_data.info['trailingPE']:.2f}")

st.title("📊 Stock Price Analyzer")

# Sidebar to select stock symbol and date range
symbol = st.sidebar.selectbox('📌 Select Stock Symbol:', ('AAPL', 'GOOG', 'TSLA', 'MSFT', 'NFLX'))
start_date = st.sidebar.date_input("📅 Enter Start Date", datetime.date(2019, 7, 6))
end_date = st.sidebar.date_input("📅 Enter End Date", datetime.date(2019, 7, 10))

# Fetch and display stock data
with st.spinner("✅ Data fetched successfully!"):
    ticker_data, ticker_df = get_stock_data(symbol, start_date, end_date)
    if ticker_df is not None:
        live_price = get_live_price(symbol)  # Fetch live price
        display_stock_data(ticker_data, ticker_df, live_price)
        # Download button for CSV
        st.download_button(label="💾 Download data as CSV",
                           data=ticker_df.to_csv().encode("utf-8"),
                           file_name=f"{symbol}_stock_data.csv",
                           mime="text/csv")
        time.sleep(2)
        st.empty()
