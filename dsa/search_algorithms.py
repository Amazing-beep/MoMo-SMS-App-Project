"""
Data Structures and Algorithms Implementation
Linear Search vs Dictionary Lookup comparison
"""

import time
import json
from typing import List, Dict, Any, Optional


def linear_search_by_id(transactions: List[Dict[str, Any]], target_id: int) -> Optional[Dict[str, Any]]:
    """
    Linear search to find transaction by ID
    Time Complexity: O(n)
    
    Args:
        transactions (List[Dict[str, Any]]): List of transactions
        target_id (int): ID to search for
        
    Returns:
        Optional[Dict[str, Any]]: Found transaction or None
    """
    for transaction in transactions:
        if transaction['id'] == target_id:
            return transaction
    return None


def create_id_dictionary(transactions: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Create dictionary mapping ID to transaction
    Time Complexity: O(n) for creation, O(1) for lookup
    
    Args:
        transactions (List[Dict[str, Any]]): List of transactions
        
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary with ID as key
    """
    return {transaction['id']: transaction for transaction in transactions}


def dictionary_lookup(transaction_dict: Dict[int, Dict[str, Any]], target_id: int) -> Optional[Dict[str, Any]]:
    """
    Dictionary lookup to find transaction by ID
    Time Complexity: O(1)
    
    Args:
        transaction_dict (Dict[int, Dict[str, Any]]): Dictionary of transactions
        target_id (int): ID to search for
        
    Returns:
        Optional[Dict[str, Any]]: Found transaction or None
    """
    return transaction_dict.get(target_id)


def benchmark_search_methods(transactions: List[Dict[str, Any]], num_tests: int = 100) -> Dict[str, float]:
    """
    Benchmark linear search vs dictionary lookup
    
    Args:
        transactions (List[Dict[str, Any]]): List of transactions
        num_tests (int): Number of test iterations
        
    Returns:
        Dict[str, float]: Average execution times
    """
    # Create dictionary for lookup
    transaction_dict = create_id_dictionary(transactions)
    
    # Test IDs (random selection)
    import random
    test_ids = [random.randint(1, len(transactions)) for _ in range(num_tests)]
    
    # Benchmark linear search
    start_time = time.time()
    for test_id in test_ids:
        linear_search_by_id(transactions, test_id)
    linear_search_time = time.time() - start_time
    
    # Benchmark dictionary lookup
    start_time = time.time()
    for test_id in test_ids:
        dictionary_lookup(transaction_dict, test_id)
    dictionary_lookup_time = time.time() - start_time
    
    return {
        'linear_search_avg': linear_search_time / num_tests,
        'dictionary_lookup_avg': dictionary_lookup_time / num_tests,
        'linear_search_total': linear_search_time,
        'dictionary_lookup_total': dictionary_lookup_time,
        'speedup_factor': linear_search_time / dictionary_lookup_time
    }


def analyze_performance(transactions: List[Dict[str, Any]]) -> None:
    """
    Analyze and display performance comparison
    
    Args:
        transactions (List[Dict[str, Any]]): List of transactions
    """
    print(f"Performance Analysis for {len(transactions)} transactions")
    print("=" * 50)
    
    # Run benchmark
    results = benchmark_search_methods(transactions, 1000)
    
    print(f"Linear Search Average Time: {results['linear_search_avg']:.6f} seconds")
    print(f"Dictionary Lookup Average Time: {results['dictionary_lookup_avg']:.6f} seconds")
    print(f"Speedup Factor: {results['speedup_factor']:.2f}x")
    print()
    
    # Test specific searches
    print("Testing specific searches:")
    test_ids = [1, 10, 25]  # Test first, middle, and last
    
    for test_id in test_ids:
        if test_id <= len(transactions):
            # Linear search
            start = time.time()
            result_linear = linear_search_by_id(transactions, test_id)
            linear_time = time.time() - start
            
            # Dictionary lookup
            transaction_dict = create_id_dictionary(transactions)
            start = time.time()
            result_dict = dictionary_lookup(transaction_dict, test_id)
            dict_time = time.time() - start
            
            print(f"ID {test_id}: Linear={linear_time:.6f}s, Dict={dict_time:.6f}s")
            print(f"  Found: {result_linear['sender']} -> {result_linear['recipient']}")


if __name__ == "__main__":
    # Load data
    try:
        with open('sms_data.json', 'r') as f:
            transactions = json.load(f)
        
        print("DSA Performance Analysis")
        print("=" * 30)
        analyze_performance(transactions)
        
        print("\nReflection:")
        print("- Dictionary lookup is faster because it uses hash tables (O(1) vs O(n))")
        print("- Linear search must check each element sequentially")
        print("- For large datasets, the difference becomes more significant")
        print("- Alternative data structures: Binary Search Trees (O(log n)), Hash Tables (O(1))")
        
    except FileNotFoundError:
        print("Error: sms_data.json not found. Run xml_parser.py first.")
