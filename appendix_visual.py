
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

CSV_PATH = r"/Users/Ray.Fang/RSM336/out/bottom_10pct.csv"

def create_top_performers_table():
    """Create a formatted table of top 10 performing stocks"""
    
    # Read the data
    df = pd.read_csv(CSV_PATH)
    
    # Get top 10 performers
    top_10 = df.head(10)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare data for table
    table_data = []
    for i, (_, row) in enumerate(top_10.iterrows(), 1):
        rank = str(i)
        ticker = row['ticker']
        return_pct = f"{row['mom_12_1'] * 100:.2f}%"
        table_data.append([rank, ticker, return_pct])
    
    # Add header
    headers = ['Rank', 'Ticker', '12-1 Month Return']
    
    # Create table
    table = ax.table(cellText=table_data, 
                    colLabels=headers,
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.2, 0.3, 0.4])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2)
    
    # Define color scheme - dark blue based on RGB(30, 60, 96)
    header_color = '#1E3C60'  # RGB(30, 60, 96)
    alt_row_color = '#F5F7FA'  # Light blue-gray
    
    # Style header
    for i in range(len(headers)):
        table[(0, i)].set_facecolor(header_color)
        table[(0, i)].set_text_props(weight='bold', color='white', fontfamily='Palatino')
        table[(0, i)].set_height(0.08)
    
    # Style data rows with alternating colors
    for i in range(1, len(table_data) + 1):
        if i % 2 == 1:
            for j in range(len(headers)):
                table[(i, j)].set_facecolor(alt_row_color)
                table[(i, j)].set_text_props(fontfamily='Palatino')
        else:
            for j in range(len(headers)):
                table[(i, j)].set_facecolor('white')
                table[(i, j)].set_text_props(fontfamily='Palatino')
        
        # Set row height
        for j in range(len(headers)):
            table[(i, j)].set_height(0.06)
    
    # Add title with Palatino font
    plt.title('Top 10 Momentum Performers\n(12-1 Month Returns)', 
              fontsize=16, fontweight='bold', pad=10, fontfamily='Palatino', color=header_color)
    
    # Add border around the table
    table_bbox = table.get_window_extent(fig.canvas.get_renderer())
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('/Users/Ray.Fang/RSM336/out/top_performers_table.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print("Table saved as 'top_performers_table.png' in the out folder")
    print("\nTop 10 Performers:")
    for i, (_, row) in enumerate(top_10.iterrows(), 1):
        print(f"{i:2d}. {row['ticker']:8s} {row['mom_12_1'] * 100:8.2f}%")

if __name__ == "__main__":
    create_top_performers_table()
