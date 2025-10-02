"""
DSA Demonstration Script
Shows the performance comparison between Linear Search and Dictionary Lookup
"""

import sys
import os

# Add dsa directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dsa'))

from xml_parser import parse_xml_to_json
from search_algorithms import demonstrate_search_algorithms, measure_search_performance

def main():
    """Run DSA demonstration"""
    print("Data Structures & Algorithms Demonstration")
    print("=" * 50)
    
    # Parse XML data
    print("Loading transaction data...")
    transactions = parse_xml_to_json("modified_sms_v2.xml")
    
    if not transactions:
        print("❌ No transaction data found. Make sure modified_sms_v2.xml exists.")
        return
    
    print(f"✓ Loaded {len(transactions)} transactions")
    
    # Run demonstration
    demonstrate_search_algorithms(transactions)
    
    print("\n" + "=" * 50)
    print("DSA demonstration completed!")

if __name__ == "__main__":
    main()
