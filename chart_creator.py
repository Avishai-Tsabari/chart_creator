import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker
import sys
import os
from datetime import datetime, timedelta
import yfinance as yf

def create_chart(data_file, years=1):
    # Colors
    BG_COLOR = '#0f0f0f'
    GRID_COLOR = '#868686'
    UP_COLOR = '#15ff25'   # (21, 255, 37)
    DOWN_COLOR = '#ff8486' # (255, 132, 134)
    TEXT_COLOR = '#868686' # Matching grid/text color from analysis
    
    # Generate output filename automatically: remove .txt extension and add _chart.png
    base_name = os.path.splitext(data_file)[0]
    output_file = f"{base_name}_chart.png"

    # Load Data
    # First, try to read from file. If file doesn't exist, download from yfinance
    if not os.path.exists(data_file):
        print(f"File {data_file} not found. Attempting to download data from yfinance...")
        
        # Extract ticker symbol from filename (e.g., "tqqq.txt" -> "TQQQ")
        ticker = os.path.splitext(os.path.basename(data_file))[0].upper()
        
        try:
            # Download 2 years of data from today
            end_date = datetime.now()
            start_date = end_date - timedelta(days=2*365)
            
            print(f"Downloading {ticker} data from {start_date.date()} to {end_date.date()}...")
            yf_data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            
            if yf_data.empty:
                print(f"Error: No data found for ticker {ticker}")
                return
            
            # Transform yfinance data to match expected format
            # yfinance returns: Open, High, Low, Close, Adj Close, Volume (with Date as index)
            # Handle MultiIndex columns if present (flatten to single level)
            if isinstance(yf_data.columns, pd.MultiIndex):
                yf_data.columns = yf_data.columns.droplevel(1)
            
            df = pd.DataFrame()
            df['Date'] = pd.to_datetime(yf_data.index)
            df['Time'] = '00:00:00'  # yfinance doesn't provide time, use default
            df['Open'] = yf_data['Open'].values
            df['High'] = yf_data['High'].values
            df['Low'] = yf_data['Low'].values
            df['Close'] = yf_data['Close'].values
            df['Vol'] = yf_data['Volume'].values
            df['OI'] = 0  # Open Interest not available from yfinance, set to 0
            
            # Sort by date to ensure chronological order
            df = df.sort_values('Date')
            
            print(f"Successfully downloaded {len(df)} rows of data for {ticker}")
            
        except Exception as e:
            print(f"Error downloading data from yfinance: {e}")
            return
    else:
        # Load from file
        # Assuming the format from tqqq.txt: "Date","Time","Open","High","Low","Close","Vol","OI"
        try:
            df = pd.read_csv(data_file)
            # Strip quotes from column names if necessary (pandas usually handles this but good to be safe)
            df.columns = [c.strip('"').strip() for c in df.columns]
            
            # Parse Date
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
        except Exception as e:
            print(f"Error reading data file: {e}")
            return

    lookback_window = 150

    # Calculate SMA 150
    df[f'SMA{lookback_window}'] = df['Close'].rolling(window=lookback_window).mean()

    # Filter for the last N years
    # Ensure we have enough data
    if not df.empty:
        cutoff_date = df['Date'].max() - pd.Timedelta(days=years * 365)
        df = df[df['Date'] > cutoff_date].copy()
    
    # Reset index to use for x-axis (removes gaps)
    df = df.reset_index(drop=True)

    # Create Figure and Axis with Subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.patch.set_facecolor(BG_COLOR)
    
    # --- Main Chart (Price) ---
    ax1.set_facecolor(BG_COLOR)

    # Plot Candles
    width = 0.6
    
    up = df[df.Close >= df.Open]
    down = df[df.Close < df.Open]

    # Up candles
    ax1.vlines(up.index, up.Low, up.High, color=UP_COLOR, linewidth=1)
    ax1.bar(up.index, up.Close - up.Open, width, bottom=up.Open, color=UP_COLOR, align='center')

    # Down candles
    ax1.vlines(down.index, down.Low, down.High, color=DOWN_COLOR, linewidth=1)
    ax1.bar(down.index, down.Open - down.Close, width, bottom=down.Close, color=DOWN_COLOR, align='center')

    # Plot SMA
    # Use a light gray color for SMA
    SMA_COLOR = '#e2e2e2'
    ax1.plot(df.index, df[f'SMA{lookback_window}'], color=SMA_COLOR, linewidth=1.5, label=f'SMA {lookback_window}')

    # Grid for Price
    ax1.grid(True, color=GRID_COLOR, linestyle='-', linewidth=0.5, alpha=0.5)
    # Remove top and right spines
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False) 
    ax1.spines['bottom'].set_visible(False) # Hide bottom spine of top plot
    
    # Ticks and Labels for Price
    ax1.tick_params(axis='y', colors=TEXT_COLOR)
    ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) # Hide x ticks for top plot

    # --- Volume Chart ---
    ax2.set_facecolor(BG_COLOR)
    
    # Plot Volume
    # Color volume bars based on price action (same as candles)
    # Volume bars should have no gaps, so width=1.0 (since x-axis is days)
    volume_width = 1.0
    ax2.bar(up.index, up.Vol, volume_width, color=UP_COLOR, align='center')
    ax2.bar(down.index, down.Vol, volume_width, color=DOWN_COLOR, align='center')
    
    # Grid for Volume
    ax2.grid(True, color=GRID_COLOR, linestyle='-', linewidth=0.5, alpha=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False) 
    ax2.spines['bottom'].set_color(GRID_COLOR)
    
    # Ticks and Labels for Volume
    ax2.tick_params(axis='x', colors=TEXT_COLOR)
    ax2.tick_params(axis='y', colors=TEXT_COLOR)
    
    # X-axis formatting (applied to the shared axis, visible on bottom)
    # Custom formatter for index-based x-axis
    def date_fmt(x, pos=None):
        idx = int(x)
        if 0 <= idx < len(df):
            dt = df['Date'].iloc[idx]
            if dt.month == 1 and df['Date'].iloc[idx-1].year != dt.year if idx > 0 else True:
                 return dt.strftime('%b\n%Y')
            return dt.strftime('%b')
        return ''

    ax2.xaxis.set_major_formatter(plt.FuncFormatter(date_fmt))
    
    # Set ticks to show months roughly where they start
    # We can find indices where month changes
    month_starts = []
    for i in range(1, len(df)):
        if df['Date'].iloc[i].month != df['Date'].iloc[i-1].month:
            month_starts.append(i)
    # Add first date if needed, or just rely on month changes
    if not month_starts or month_starts[0] > 20: # Ensure first label isn't too far
         month_starts.insert(0, 0)
         
    ax2.set_xticks(month_starts)

    # Symbol Name and Indicator (on Main Chart)
    symbol = os.path.splitext(os.path.basename(data_file))[0].upper()
    
    # Determine Status
    last_close = df.iloc[-1]['Close']
    last_sma = df.iloc[-1][f'SMA{lookback_window}']
    
    status_text = ""
    status_color = UP_COLOR # Default to Green (Above)
    
    if pd.notna(last_sma):
        diff_pct = (last_close - last_sma) / last_sma
        if diff_pct < -0.005: # Below by more than 0.5%
            status_color = DOWN_COLOR
            status_text = f"Below ({lookback_window}) SMA"
        elif abs(diff_pct) <= 0.005: # Within 0.5%
            status_color = '#ffff00' # Yellow
            status_text = f"On ({lookback_window}) SMA"
        else:
            status_color = UP_COLOR
            status_text = f"Above ({lookback_window}) SMA"
            
    # Draw Symbol Text
    # Place symbol at top left of ax1
    ax1.text(0.02, 0.95, symbol, transform=ax1.transAxes, color=TEXT_COLOR, fontsize=16, fontweight='bold', va='top')
    
    # Draw Indicator Text below symbol
    if status_text:
        # Create text area
        text_box = TextArea(status_text, textprops=dict(color=TEXT_COLOR, fontsize=10, fontweight='bold'))
        
        # Create circle area (using a large dot character)
        dot_box = TextArea(" ●", textprops=dict(color=status_color, fontsize=14, fontweight='bold'))
        
        # Pack them horizontally
        packer = HPacker(children=[text_box, dot_box], align="baseline", pad=0, sep=2)
        
        # Create anchored offsetbox
        anchored_box = AnchoredOffsetbox(loc='upper left', child=packer, pad=0., frameon=False, 
                                         bbox_to_anchor=(0.02, 0.90), 
                                         bbox_transform=ax1.transAxes, borderpad=0.)
        ax1.add_artist(anchored_box)

    # Save
    plt.tight_layout()
    plt.savefig(output_file, facecolor=fig.get_facecolor(), dpi=100)
    plt.close()
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        years = float(sys.argv[2]) if len(sys.argv) > 2 else 1
        create_chart(data_file, years)
    else:
        print("Usage: python chart_creator.py <data_file> [years]")
