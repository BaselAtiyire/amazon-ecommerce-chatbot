import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path("data/products.db")


def init_db() -> None:
    """Create the SQLite DB + products table. Seed sample products if empty."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            name TEXT,
            price REAL,
            rating REAL,
            url TEXT
        )
        """
    )

    # Seed sample data only if table is empty
    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]

    if count == 0:
        # ✅ Amazon-only links + realistic USD prices
        sample = [
            ("NIKE", "Pegasus 40 Running Shoes (Women)", 129.99, 5.0, "https://www.amazon.com/s?k=nike+pegasus+40"),
            ("NIKE", "Winflo 9 Premium Running Shoes (Women)", 109.99, 5.0, "https://www.amazon.com/s?k=nike+winflo+9"),
            ("ADIDAS", "Ultraboost Light", 189.99, 4.7, "https://www.amazon.com/s?k=adidas+ultraboost+light"),
            ("PUMA", "Deviate Nitro 2", 159.99, 4.6, "https://www.amazon.com/s?k=puma+deviate+nitro+2"),
        ]

        cur.executemany(
            "INSERT INTO products (brand, name, price, rating, url) VALUES (?, ?, ?, ?, ?)",
            sample,
        )

    conn.commit()
    conn.close()


def query_products(
    brand: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Query products by optional brand, min_rating, min_price, max_price."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    sql = "SELECT brand, name, price, rating, url FROM products WHERE 1=1"
    params = []

    if brand:
        sql += " AND UPPER(brand) = UPPER(?)"
        params.append(brand)

    if min_rating is not None:
        sql += " AND rating >= ?"
        params.append(min_rating)

    if min_price is not None:
        sql += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)

    sql += " ORDER BY rating DESC, price ASC LIMIT ?"
    params.append(limit)

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    return [
        {"brand": r[0], "name": r[1], "price": r[2], "rating": r[3], "url": r[4]}
        for r in rows
    ]
