TEST_CASES = [
    {
        "question": "What was the highest daily percentage increase in price?",
        "intent": "needle",
        "ground_truth": "The highest daily percentage increase was 17.85% on November 15, 2025.",
    },
    {
        "question": "Give a summary of PLTR trading activity in November 2025",
        "intent": "summary",
        "ground_truth": "PLTR showed significant trading activity in November 2025 with notable price movements and volume changes across multiple trading days.",
    },
    {
        "question": "On what date was there an insider sale filing?",
        "intent": "needle",
        "ground_truth": "There was an insider sale filing on November 15, 2025 when an officer filed a Form 144.",
    },
    {
        "question": "What was the price range on November 15?",
        "intent": "needle",
        "ground_truth": "The price range on November 15 was between 154.40 and 170 (approximately).",
    },
    {
        "question": "Provide an overview of the data sources used",
        "intent": "summary",
        "ground_truth": "The data comes from Stooq CSV for daily OHLCV prices and news items from financial sources.",
    },
    {
        "question": "What was the closing price on the day with highest percentage increase?",
        "intent": "needle",
        "ground_truth": "The closing price was 155.75 on November 15, 2025.",
    },
    {
        "question": "List the key events mentioned in the document",
        "intent": "summary",
        "ground_truth": "Key events include significant price movements, insider trading filings, and daily trading activities throughout November 2025.",
    },
    {
        "question": "What type of form was filed for the insider sale?",
        "intent": "needle",
        "ground_truth": "Form 144 was filed for the insider sale.",
    },
]
