# ingest_faq.py
import sys
from pathlib import Path

# Make sure chains.py helpers are importable
sys.path.insert(0, str(Path(__file__).parent))
from chains import add_to_index

FAQS = [
    "Most items can be returned within the return window shown on your order. "
    "Refunds are typically issued after the return is received and processed. "
    "During holidays, return windows may be extended for eligible purchases.",

    "To return an item: go to Your Orders → choose the item → select Return or Replace Items → "
    "choose reason → select return method → print label or use a QR code drop-off if available.",

    "Shipping speed depends on your selected option (Standard, Expedited, Prime) and item availability. "
    "The estimated delivery date is shown at checkout and in Your Orders.",

    "You can cancel an order from Your Orders if it hasn't entered the shipping process. "
    "If it shipped already, you may need to return it after delivery.",
]

def main():
    print("Building FAQ index with faiss...")
    add_to_index(FAQS)
    print(f"✅ FAQ index built with {len(FAQS)} entries.")

if __name__ == "__main__":
    main()
