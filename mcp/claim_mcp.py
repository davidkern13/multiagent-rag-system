from mcp.claim_tools import (
    analyze_claim_timeline,
    validate_required_documents,
    extract_price_range,
    analyze_trading_patterns,
    calculate_moving_average,
)


class ClaimMCP:
    """
    MCP wrapper that extends LLM capabilities with structured tools.
    Now includes Pandas-powered trading analysis!
    """

    def run(self, query: str, contexts: list[str]) -> str | None:
        q = query.lower()
        text = "\n".join(contexts)

        # Timeline analysis
        if "timeline" in q or "duration" in q or "how long" in q:
            result = analyze_claim_timeline(text)
            if result["claim_duration_days"] != -1:
                dates = result["dates_found"]
                duration = result["claim_duration_days"]
                return f"Timeline Analysis: Found {len(dates)} dates spanning {duration} days (from {dates[0] if dates else 'N/A'} to {dates[-1] if dates else 'N/A'})"

        # Data validation (for trading data)
        if "missing" in q or "required" in q or "validation" in q:
            result = validate_required_documents(
                text,
                ["OHLCV data", "price", "volume", "date"],
            )
            missing = [doc for doc, found in result.items() if not found]
            if missing:
                return f"Missing Data Fields: {', '.join(missing)}"
            else:
                return "All required trading data fields are present"

        # Price range extraction
        if "price range" in q or ("high" in q and "low" in q):
            result = extract_price_range(text)
            if result["high"] and result["low"]:
                return f"Price Range: Low ${result['low']}, High ${result['high']}"

        # Trading pattern analysis with Pandas
        if "pattern" in q or "statistics" in q or "volatility" in q or "analysis" in q:
            result = analyze_trading_patterns(text)
            if "error" not in result:
                return (
                    f"Trading Analysis (Pandas):\n"
                    f"  • Avg Price: ${result['avg_price']}\n"
                    f"  • Volatility: {result['price_volatility']}%\n"
                    f"  • Price Change: {result['price_change_pct']}%\n"
                    f"  • Range: ${result['min_price']} - ${result['max_price']}"
                )

        # Moving average calculation
        if "moving average" in q or "ma" in q or "trend" in q:
            result = calculate_moving_average(text, window=5)
            if "error" not in result:
                signal = "📈 Above" if result["above_ma"] else "📉 Below"
                return (
                    f"Moving Average Analysis:\n"
                    f"  • Latest Price: ${result['latest_price']}\n"
                    f"  • 5-day MA: ${result['moving_average']}\n"
                    f"  • Signal: {signal} MA"
                )

        return None
