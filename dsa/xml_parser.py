
import xml.etree.ElementTree as ET
import json
from typing import List, Dict

def parse_xml_to_json(xml_file: str) -> List[Dict]:
    """
    Parse XML file containing SMS transaction records
    
    Args:
        xml_file: Path to the XML file
        
    Returns:
        List of transaction dictionaries
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        transactions = []
        
        for transaction in root.findall('transaction'):
            trans_dict = {
                'id': transaction.get('id'),
                'type': transaction.find('type').text,
                'amount': float(transaction.find('amount').text),
                'sender': transaction.find('sender').text,
                'receiver': transaction.find('receiver').text,
                'timestamp': transaction.find('timestamp').text,
                'status': transaction.find('status').text,
                'description': transaction.find('description').text
            }
            transactions.append(trans_dict)
        
        return transactions
    
    except FileNotFoundError:
        print(f"Error: File '{xml_file}' not found")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def save_to_json(transactions: List[Dict], output_file: str = 'transactions.json'):
    """
    Save transactions to JSON file
    
    Args:
        transactions: List of transaction dictionaries
        output_file: Output JSON file path
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
        print(f"✓ Successfully saved {len(transactions)} transactions to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

if __name__ == "__main__":
    # Parse XML and save to JSON
    transactions = parse_xml_to_json("modified_sms_v2.xml")
    if transactions:
        save_to_json(transactions)
        print(f"\nParsed {len(transactions)} transactions")
        print(f"Sample transaction: {json.dumps(transactions[0], indent=2)}")