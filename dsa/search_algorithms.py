import time
from typing import List, Dict, Optional

def linear_search(transactions: List[Dict], transaction_id: str) -> Optional[Dict]:
    """
    Linear Search: O(n) complexity
    Scans through list sequentially to find transaction by ID
    
    Args:
        transactions: List of transaction dictionaries
        transaction_id: ID to search for
        
    Returns:
        Transaction dict if found, None otherwise
    """
    for transaction in transactions:
        if transaction['id'] == transaction_id:
            return transaction
    return None

def build_transaction_dict(transactions: List[Dict]) -> Dict[str, Dict]:
    """
    Build dictionary for O(1) lookup
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Dictionary with id as key and transaction as value
    """
    return {trans['id']: trans for trans in transactions}

def dictionary_lookup(trans_dict: Dict[str, Dict], transaction_id: str) -> Optional[Dict]:
    """
    Dictionary Lookup: O(1) complexity
    Direct hash-based lookup
    
    Args:
        trans_dict: Dictionary of transactions
        transaction_id: ID to search for
        
    Returns:
        Transaction dict if found, None otherwise
    """
    return trans_dict.get(transaction_id)

def measure_search_performance(transactions: List[Dict], num_searches: int = 100):
    """
    Measure and compare performance of both search methods
    
    Args:
        transactions: List of transactions
        num_searches: Number of search operations to perform
    """
    if not transactions:
        print("No transactions to search")
        return
    
    # Build dictionary for lookup
    trans_dict = build_transaction_dict(transactions)
    
    # Select transaction IDs to search (including some that don't exist)
    search_ids = [trans['id'] for trans in transactions[:min(10, len(transactions))]]
    search_ids.extend(['999', '1000'])  # Non-existent IDs
    
    print(f"\n{'='*70}")
    print("PERFORMANCE MEASUREMENT")
    print(f"{'='*70}")
    print(f"Dataset: {len(transactions)} transactions")
    print(f"Iterations: {num_searches} cycles")
    print(f"Searches per cycle: {len(search_ids)}")
    print(f"Total searches: {num_searches * len(search_ids)}")
    
    # Measure Linear Search
    print("\n⏱️  Measuring Linear Search...")
    start_time = time.time()
    for _ in range(num_searches):
        for search_id in search_ids:
            linear_search(transactions, search_id)
    linear_time = time.time() - start_time
    
    # Measure Dictionary Lookup
    print("⏱️  Measuring Dictionary Lookup...")
    start_time = time.time()
    for _ in range(num_searches):
        for search_id in search_ids:
            dictionary_lookup(trans_dict, search_id)
    dict_time = time.time() - start_time
    
    # Display results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Linear Search Time:     {linear_time:.6f} seconds")
    print(f"Dictionary Lookup Time: {dict_time:.6f} seconds")
    print(f"\nSpeedup: {linear_time/dict_time:.2f}x faster")
    print(f"Time saved: {(linear_time - dict_time)*1000:.2f} milliseconds")
    
    # Per-search analysis
    total_searches = num_searches * len(search_ids)
    print(f"\nPer-Search Performance:")
    print(f"  Linear Search:     {(linear_time/total_searches)*1000000:.2f} microseconds/search")
    print(f"  Dictionary Lookup: {(dict_time/total_searches)*1000000:.2f} microseconds/search")
    
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}")
    print("Linear Search: O(n)")
    print("  • Must check each element sequentially")
    print("  • Performance degrades as dataset grows")
    print("  • Time increases linearly with data size")
    
    print("\nDictionary Lookup: O(1)")
    print("  • Direct hash-based access")
    print("  • Constant time regardless of dataset size")
    print("  • Uses hash table for instant retrieval")
    
    print(f"\nFor {len(transactions)} transactions:")
    print(f"  • Dictionary is ~{linear_time/dict_time:.0f}x faster")
    print(f"  • Difference becomes more dramatic with larger datasets")
    
    # Scalability projection
    print(f"\n{'='*70}")
    print("SCALABILITY PROJECTION")
    print(f"{'='*70}")
    
    sizes = [100, 1000, 10000, 100000]
    print(f"{'Dataset Size':<15} {'Linear (est)':<20} {'Dictionary':<20} {'Speedup':<15}")
    print("-" * 70)
    
    for size in sizes:
        ratio = size / len(transactions)
        linear_est = linear_time * ratio
        dict_est = dict_time  # Stays constant
        speedup = linear_est / dict_est if dict_est > 0 else 0
        
        print(f"{size:<15} {linear_est:.4f}s{'':<14} {dict_est:.6f}s{'':<13} {speedup:.0f}x")
    
    print(f"\n{'='*70}")
    print("ALTERNATIVE DATA STRUCTURES")
    print(f"{'='*70}")
    print("\n1. Binary Search Tree (BST)")
    print("   • Time Complexity: O(log n)")
    print("   • Best for: Sorted data with range queries")
    print("   • Use case: Finding all transactions in amount range")
    
    print("\n2. B-Tree")
    print("   • Time Complexity: O(log n)")
    print("   • Best for: Database indexing, disk storage")
    print("   • Use case: Large datasets stored on disk")
    
    print("\n3. Trie (Prefix Tree)")
    print("   • Time Complexity: O(k) where k = key length")
    print("   • Best for: Phone number or prefix searches")
    print("   • Use case: Autocomplete, phone number lookup")
    
    print("\n4. Bloom Filter")
    print("   • Time Complexity: O(1) probabilistic")
    print("   • Best for: Quick existence checks")
    print("   • Use case: Fast 'does transaction exist?' queries")
    
    print(f"\n{'='*70}")

def demonstrate_search_algorithms(transactions: List[Dict]):
    """
    Demonstrate both search algorithms with examples
    
    Args:
        transactions: List of transactions
    """
    print("\n" + "="*70)
    print("SEARCH ALGORITHM DEMONSTRATION")
    print("="*70)
    
    if not transactions:
        print("❌ No transactions available")
        return
    
    # Build dictionary
    trans_dict = build_transaction_dict(transactions)
    
    # Example 1: Search for existing transaction
    test_id = transactions[0]['id']
    print(f"\n📋 Test 1: Searching for existing transaction (ID: {test_id})")
    print("-" * 70)
    
    # Linear Search
    start = time.time()
    result_linear = linear_search(transactions, test_id)
    time_linear = (time.time() - start) * 1000000  # microseconds
    
    if result_linear:
        print(f"✓ Linear Search: Found in {time_linear:.2f} microseconds")
        print(f"  Transaction: {result_linear['type']} - ${result_linear['amount']}")
    
    # Dictionary Lookup
    start = time.time()
    result_dict = dictionary_lookup(trans_dict, test_id)
    time_dict = (time.time() - start) * 1000000  # microseconds
    
    if result_dict:
        print(f"✓ Dictionary Lookup: Found in {time_dict:.2f} microseconds")
        print(f"  Transaction: {result_dict['type']} - ${result_dict['amount']}")
    
    print(f"\n  Speed comparison: Dictionary is {time_linear/time_dict:.1f}x faster")
    
    # Example 2: Search for non-existent transaction
    test_id = '99999'
    print(f"\n📋 Test 2: Searching for non-existent transaction (ID: {test_id})")
    print("-" * 70)
    
    # Linear Search
    start = time.time()
    result_linear = linear_search(transactions, test_id)
    time_linear = (time.time() - start) * 1000000
    
    print(f"✗ Linear Search: Not found (checked all {len(transactions)} records)")
    print(f"  Time: {time_linear:.2f} microseconds")
    
    # Dictionary Lookup
    start = time.time()
    result_dict = dictionary_lookup(trans_dict, test_id)
    time_dict = (time.time() - start) * 1000000
    
    print(f"✗ Dictionary Lookup: Not found (instant check)")
    print(f"  Time: {time_dict:.2f} microseconds")
    
    print(f"\n  Linear search had to check ALL records")
    print(f"  Dictionary knew instantly the key doesn't exist")
    
    # Example 3: Multiple searches
    print(f"\n📋 Test 3: Multiple consecutive searches")
    print("-" * 70)
    
    search_ids = [trans['id'] for trans in transactions[:5]]
    
    # Linear Search
    start = time.time()
    for sid in search_ids:
        linear_search(transactions, sid)
    time_linear = (time.time() - start) * 1000
    
    print(f"Linear Search: {len(search_ids)} searches in {time_linear:.3f} ms")
    
    # Dictionary Lookup
    start = time.time()
    for sid in search_ids:
        dictionary_lookup(trans_dict, sid)
    time_dict = (time.time() - start) * 1000
    
    print(f"Dictionary Lookup: {len(search_ids)} searches in {time_dict:.3f} ms")
    print(f"\nSpeedup: {time_linear/time_dict:.1f}x faster with dictionary")
    
    # Run full performance comparison
    measure_search_performance(transactions)

if __name__ == "__main__":
    from xml_parser import parse_xml_to_json
    
    # Load transactions
    transactions = parse_xml_to_json("../modified_sms_v2.xml")
    
    if transactions:
        demonstrate_search_algorithms(transactions)
    else:
        print("Failed to load transactions")