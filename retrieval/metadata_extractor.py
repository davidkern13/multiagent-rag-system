import re
from dateutil import parser
from collections import Counter


def extract_timestamp(text: str):
    """Extract the first date found in text."""
    match = re.search(r"\b(?:\d{4}-\d{2}-\d{2}|\w{3,9} \d{1,2}, \d{4})\b", text)
    if match:
        try:
            return str(parser.parse(match.group(0)).date())
        except Exception:
            return None
    return None


def extract_entities_from_text(text: str, top_n: int = 10):
    """
    Dynamically extract entities from text.

    Args:
        text: Input text
        top_n: Number of top entities to return

    Returns:
        List of extracted entities
    """
    # Extract potential entities:
    # 1. Stock tickers (all caps, 1-5 letters)
    stock_tickers = re.findall(r"\b[A-Z]{1,5}\b", text)

    # 2. Numbers with context (prices, percentages)
    price_contexts = re.findall(r"\$[\d,]+\.?\d*|\d+\.?\d*%", text)

    # 3. Capitalized words (potential names, organizations)
    capitalized = re.findall(r"\b[A-Z][a-z]+\b", text)

    # 4. Common financial terms
    financial_terms = [
        "revenue",
        "profit",
        "loss",
        "earnings",
        "guidance",
        "forecast",
        "quarter",
        "annual",
        "shares",
        "stock",
        "dividend",
        "market",
        "trading",
        "volume",
        "price",
        "high",
        "low",
        "close",
        "open",
        "claim",
        "policy",
        "premium",
        "coverage",
        "deductible",
    ]

    found_terms = [term for term in financial_terms if term.lower() in text.lower()]

    # Combine and count
    all_entities = stock_tickers + capitalized + found_terms

    # Filter out common words
    stopwords = {
        "The",
        "This",
        "That",
        "With",
        "From",
        "Were",
        "Have",
        "More",
        "Been",
        "Their",
        "About",
        "Other",
    }
    filtered = [e for e in all_entities if e not in stopwords and len(e) > 1]

    # Get most common
    counter = Counter(filtered)
    return [entity for entity, count in counter.most_common(top_n)]


def extract_entities(text: str):
    """
    Legacy function - now calls dynamic extraction.
    Kept for backward compatibility.
    """
    return extract_entities_from_text(text, top_n=10)


def extract_doc_type(text: str) -> str:
    """
    Dynamically determine document type based on content.
    """
    text_lower = text.lower()

    # Check for different document types
    if any(
        term in text_lower for term in ["ohlcv", "trading", "daily", "stock", "ticker"]
    ):
        return "trading_report"
    elif any(term in text_lower for term in ["summary", "overview", "report"]):
        return "summary_report"
    elif any(term in text_lower for term in ["claim", "policy", "insurance"]):
        return "insurance_document"
    elif any(term in text_lower for term in ["earnings", "revenue", "quarterly"]):
        return "financial_report"

    return "general_document"


def extract_section_title(text: str) -> str:
    """
    Extract section title from text.
    """
    lines = text.strip().splitlines()
    for line in lines:
        # Look for lines that might be titles (short, capitalized)
        line = line.strip()
        if line and len(line) < 100:
            # Check if it looks like a title
            if line.isupper() or (line[0].isupper() and line.count(".") < 2):
                return line

    # Fallback: return first non-empty line
    for line in lines:
        if line.strip():
            return line.strip()[:100]

    return "Untitled Section"


def extract_metadata_summary(text: str) -> dict:
    """
    Extract comprehensive metadata from text.

    Returns:
        Dictionary with all extracted metadata
    """
    return {
        "doc_type": extract_doc_type(text),
        "timestamp": extract_timestamp(text),
        "entities": extract_entities_from_text(text, top_n=10),
        "section_title": extract_section_title(text),
        "text_length": len(text),
        "has_financial_data": any(
            term in text.lower() for term in ["$", "revenue", "profit", "price"]
        ),
        "has_dates": bool(re.search(r"\d{4}-\d{2}-\d{2}", text)),
    }
