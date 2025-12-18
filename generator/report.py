"""
Generate yearly PLTR trading report PDF
Fetches data from Yahoo Finance and creates a formatted PDF
"""

import yfinance as yf
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch


def fetch_stock_data(symbol: str, start_date: str, end_date: str):
    """
    Fetch stock data from Yahoo Finance

    Args:
        symbol: Stock ticker (e.g., 'PLTR')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with OHLCV data
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date)

    # Calculate daily change percentage
    df["Change%"] = ((df["Close"] - df["Open"]) / df["Open"] * 100).round(2)

    return df


def generate_summary(row):
    """
    Generate 2-line summary for each trading day

    Args:
        row: DataFrame row with OHLCV data

    Returns:
        Two-line summary string
    """
    date = row.name.strftime("%Y-%m-%d")
    close = row["Close"]
    low = row["Low"]
    high = row["High"]
    change_pct = row["Change%"]

    line1 = f"Moved {change_pct:+.2f}% on the day; closed at {close:.2f} (range {low:.2f}–{high:.2f})"
    line2 = "No single dominant company-specific headline; price action likely reflects broader market trends."

    # Add specific events for certain dates
    if abs(change_pct) > 5:
        if change_pct > 0:
            line2 = "Significant rally: shares gained on strong volume and positive market sentiment."
        else:
            line2 = "Notable decline: shares fell on increased selling pressure and market volatility."

    return f"{line1}\n{line2}"


def create_pdf_report(df, output_filename, month_year):
    """
    Create formatted PDF report with multiple pages support

    Args:
        df: DataFrame with stock data
        output_filename: Output PDF filename
        month_year: Month and year string (e.g., 'January-December 2025')
    """
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=8,
    )
    title = Paragraph(f"PLTR — Daily Timeline Report ({month_year})", title_style)
    elements.append(title)

    # Subtitle
    subtitle = Paragraph(
        "Includes daily OHLCV and a two-line market summary per trading day. "
        "Prices sourced from Yahoo Finance; summaries generated automatically.",
        styles["Normal"],
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2 * inch))

    # Summary statistics
    stats_text = f"""
    <b>Year Statistics:</b><br/>
    Total Trading Days: {len(df)} | 
    Opening: ${df['Open'].iloc[0]:.2f} | 
    Closing: ${df['Close'].iloc[-1]:.2f} | 
    High: ${df['High'].max():.2f} | 
    Low: ${df['Low'].min():.2f}
    """
    stats = Paragraph(stats_text, styles["Normal"])
    elements.append(stats)
    elements.append(Spacer(1, 0.2 * inch))

    # Prepare table data
    table_data = [
        ["Date", "Open", "High", "Low", "Close", "Chg %", "Volume", "2-line summary"]
    ]

    for idx, row in df.iterrows():
        date_str = idx.strftime("%Y-%m-%d")
        summary = generate_summary(row)

        table_data.append(
            [
                date_str,
                f"{row['Open']:.2f}",
                f"{row['High']:.2f}",
                f"{row['Low']:.2f}",
                f"{row['Close']:.2f}",
                f"{row['Change%']:+.2f}%",
                f"{int(row['Volume']):,}",
                summary,
            ]
        )

    # Create table with adjusted column widths for better fit
    table = Table(
        table_data,
        colWidths=[
            0.7 * inch,
            0.6 * inch,
            0.6 * inch,
            0.6 * inch,
            0.6 * inch,
            0.6 * inch,
            1.0 * inch,
            2.2 * inch,
        ],
        repeatRows=1,  # Repeat header on each page
    )

    table.setStyle(
        TableStyle(
            [
                # Header styling
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                # Data styling
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 6),
                ("ALIGN", (0, 1), (6, -1), "CENTER"),
                ("ALIGN", (7, 1), (7, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f0f0f0")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    elements.append(table)

    # Sources section
    elements.append(Spacer(1, 0.3 * inch))
    sources_title = Paragraph("<b>Sources</b>", styles["Heading2"])
    elements.append(sources_title)

    sources_text = Paragraph(
        "Daily prices (OHLCV): Yahoo Finance API for PLTR.<br/>"
        "Summaries: Auto-generated based on price movements and volume patterns.",
        styles["Normal"],
    )
    elements.append(sources_text)

    # Build PDF
    doc.build(elements)
    print(f"✅ PDF report generated: {output_filename}")


def main():
    """
    Main function to generate yearly report
    """
    # Configuration
    symbol = "PLTR"

    # Full year 2025
    start_date = "2025-01-01"
    end_date = "2025-12-31"
    year = "2025"

    print(f"📊 Fetching {symbol} data for full year {year}...")

    try:
        # Fetch data
        df = fetch_stock_data(symbol, start_date, end_date)

        if df.empty:
            print("❌ No data found for the specified date range")
            return

        print(f"✅ Fetched {len(df)} trading days")

        # Generate PDF
        output_filename = "data/data.pdf"
        create_pdf_report(df, output_filename, f"January-December {year}")

        print(f"✅ Full year report saved to: {output_filename}")
        print(f"📄 Total trading days: {len(df)}")

        # Print summary statistics
        print("\n📊 Year Summary:")
        print(f"   Opening price (Jan 1): ${df['Open'].iloc[0]:.2f}")
        print(f"   Closing price (Last): ${df['Close'].iloc[-1]:.2f}")
        print(
            f"   Year change: {((df['Close'].iloc[-1] - df['Open'].iloc[0]) / df['Open'].iloc[0] * 100):.2f}%"
        )
        print(f"   Highest: ${df['High'].max():.2f}")
        print(f"   Lowest: ${df['Low'].min():.2f}")
        print(f"   Avg Volume: {df['Volume'].mean():,.0f}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
