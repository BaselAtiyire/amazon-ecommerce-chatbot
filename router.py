def route_intent(text: str) -> str:
    """
    Lightweight intent router (no embeddings).
    Returns: 'product' or 'faq'
    """
    t = text.lower()

    product_keywords = [
        "product", "price", "rating", "top", "best", "buy", "recommend",
        "nike", "adidas", "puma", "shoes", "sneakers", "running"
    ]

    if any(k in t for k in product_keywords):
        return "product"
    return "faq"
