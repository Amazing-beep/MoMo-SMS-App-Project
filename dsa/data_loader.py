from lxml import etree as ET
import re
import json
import time

# DATA CLEANING UTILITIES


def clean_amount(text):
    """
    Pulls out the transaction amount (like '27,000 RWF') and gives us a clean number (27000.0).
    """
    if not text:
        return 0.0

    # Looks for the amount pattern near 'RWF'
    match = re.search(r"(\d[\d,]*)\s*RWF", text)
    if match:
        # Removes commas so we can convert it to a float
        return float(match.group(1).replace(",", ""))
    return 0.0


def extract_tx_id(text):
    """
    Extracts the official Transaction ID (TxId) from the message body.
    """
    if not text:
        return "N/A"

    match = re.search(r"TxId:\s*(\d+)", text)
    if match:
        return match.group(1)

    # Catching the case where it might be called 'Financial Transaction Id'
    match_ftid = re.search(r"Financial Transaction Id:\s*(\d+)", text)
    if match_ftid:
        return match_ftid.group(1)

    return "N/A"


def get_transaction_type(body):
    """
    Tries to figure out the transaction type (In/Out/Payment) based on keywords in the SMS body.
    """
    if "You have received" in body:
        return "money_in"
    if "Your payment of" in body:
        return "payment"
    if "You have successfully sent" in body:
        return "transfer_out"
    if "Your transaction has been cancelled" in body:
        return "cancellation"
    return "unknown"


# 2. MAIN DATA LOADING FUNCTION


def load_data_from_xml(xml_filepath):
    """
    This reads the XML, processes every SMS, and returns a neat list of dictionaries.
    """
    print(f"--- Loading and preparing data from XML file... ---")

    # We use a simple counter ('row_id') as the main API primary key (PK).
    transaction_list = []
    row_id = 1

    try:
        # Use a forgiving XML parser to handle minor malformations in exported SMS files
        parser = ET.XMLParser(recover=True)
        tree = ET.parse(xml_filepath, parser)
        root = tree.getroot()

        # Loop through all <sms> tags in the XML
        for sms_element in root.findall("sms"):
            body = sms_element.get("body", "")

            # Extracting the relevant information
            transaction = {
                "id": row_id,  # Pkey for our API
                "tx_id": extract_tx_id(body),  # System transaction ID
                "timestamp_ms": int(
                    sms_element.get("date", 0)
                ),  # Time in milliseconds for quick sorting
                "readable_date": sms_element.get(
                    "readable_date", "N/A"
                ),  # The date we read easily
                "raw_body": body,  # Keeping the original text, just in case
                # The cleaned values:
                "amount": clean_amount(body),
                "type": get_transaction_type(body),
                "fee": (
                    clean_amount(body.lower().split("fee was")[-1])
                    if "fee was" in body.lower()
                    else 0.0
                ),
                "status": (
                    "completed"
                    if "completed" in body or "received" in body
                    else "pending/failed"
                ),
                # The address (usually the service name)
                "sms_address": sms_element.get("address", "N/A"),
            }

            transaction_list.append(transaction)
            row_id += 1

    except FileNotFoundError:
        print(f"ERROR: XML file '{xml_filepath}' not found. Did you check the path?")
        return []
    except ET.XMLSyntaxError as e:
        print(f"real error: {e}")
        print(
            f"ERROR: Hmm, there was an issue parsing the XML structure in '{xml_filepath}'."
        )
        return []

    print(f"--- Data loading complete! {len(transaction_list)} transactions ready. ---")
    return transaction_list