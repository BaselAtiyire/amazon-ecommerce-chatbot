# router.py
import re

PRODUCT_HINTS = [
    "price", "under", "below", "cheap", "best", "top", "recommend",
    "buy", "link", "amazon", "shoe", "shoes", "nike", "adidas", "puma",
    "laptop", "headphones"
]

FAQ_HINTS = [
    "refund", "return", "policy", "shipping", "delivery",
    "warranty", "cancel", "payment", "prime"
]

def route_intent(text: str) -> str:
    t = text.lower().strip()

    # If user mentions policy-ish words, prefer FAQ
    if any(k in t for k in FAQ_HINTS):
        return "faq"

    # If user mentions price/product-ish words, prefer product
    if any(k in t for k in PRODUCT_HINTS) or re.search(r"\$\s*\d+|\d+\s*usd", t):
        return "product"

    # default to FAQ (safer)
    return "faq"
