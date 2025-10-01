"""
XML Parser for SMS Data
Converts XML SMS transactions to JSON format
"""

import xml.etree.ElementTree as ET
import json
from typing import List, Dict, Any


def parse_xml_to_json(xml_file_path: str) -> List[Dict[str, Any]]:
    """
    Parse XML file and convert SMS transactions to JSON format
    
    Args:
        xml_file_path (str): Path to the XML file
        
    Returns:
        List[Dict[str, Any]]: List of transaction dictionaries
    """
    try:
        # Parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        transactions = []
        
        # Extract each transaction
        for transaction in root.findall('transaction'):
            transaction_data = {
                'id': int(transaction.get('id')),
                'sender': transaction.find('sender').text,
                'recipient': transaction.find('recipient').text,
                'message': transaction.find('message').text,
                'timestamp': transaction.find('timestamp').text,
                'amount': float(transaction.find('amount').text),
                'status': transaction.find('status').text
            }
            transactions.append(transaction_data)
        
        return transactions
        
    except FileNotFoundError:
        print(f"Error: XML file '{xml_file_path}' not found")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def save_json_data(transactions: List[Dict[str, Any]], output_file: str) -> None:
    """
    Save transaction data to JSON file
    
    Args:
        transactions (List[Dict[str, Any]]): List of transactions
        output_file (str): Output JSON file path
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")


def load_json_data(json_file_path: str) -> List[Dict[str, Any]]:
    """
    Load transaction data from JSON file
    
    Args:
        json_file_path (str): Path to JSON file
        
    Returns:
        List[Dict[str, Any]]: List of transactions
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


if __name__ == "__main__":
    # Parse XML and convert to JSON
    xml_file = "../modified_sms_v2.xml"
    json_file = "sms_data.json"
    
    print("Parsing XML file...")
    transactions = parse_xml_to_json(xml_file)
    
    if transactions:
        print(f"Successfully parsed {len(transactions)} transactions")
        save_json_data(transactions, json_file)
        
        # Display first transaction as example
        print("\nFirst transaction:")
        print(json.dumps(transactions[0], indent=2))
    else:
        print("No transactions found or error occurred")
