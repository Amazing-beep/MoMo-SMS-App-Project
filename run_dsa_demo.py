import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add dsa directory to path
dsa_path = os.path.join(script_dir, 'dsa')
if os.path.exists(dsa_path):
    sys.path.insert(0, dsa_path)
else:
    print(f"Warning: dsa directory not found at {dsa_path}")

try:
    from xml_parser import parse_xml_to_json
    from search_algorithms import demonstrate_search_algorithms
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

def main():
    """Run DSA demonstration"""
    print("Data Structures & Algorithms Demonstration")
    print("=" * 50)
    
    # Parse XML data
    print("\nLoading transaction data...")
    xml_file = os.path.join(script_dir, "modified_sms_v2.xml")
    
    if not os.path.exists(xml_file):
        print(f"❌ Error: {xml_file} not found")
        print("Make sure modified_sms_v2.xml is in the project root directory")
        return
    
    transactions = parse_xml_to_json(xml_file)
    
    if not transactions:
        print("❌ No transaction data found.")
        return
    
    print(f"✓ Loaded {len(transactions)} transactions")
    
    # Run demonstration
    demonstrate_search_algorithms(transactions)
    
    print("\n" + "=" * 50)
    print("DSA demonstration completed!")

if __name__ == "__main__":
    main()