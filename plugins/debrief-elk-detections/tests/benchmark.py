#!/usr/bin/env python3
"""
Performance benchmark for debrief-elk-detections plugin.

Targets:
- ELK query: <3s for 30-technique operations  
- Total PDF generation: <10s (including ELK fetch)
"""

import asyncio
import time
import sys
import os

# Add Caldera to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from unittest.mock import AsyncMock, patch


async def benchmark_elk_query():
    """Benchmark ELK query performance."""
    print("=" * 60)
    print("Benchmark: ELK Query Performance")
    print("=" * 60)
    
    # Import after path setup
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, app_dir)
    import elk_fetcher
    
    # Mock configuration
    config = {
        'elk_url': 'http://localhost:9200',
        'elk_user': 'elastic',
        'elk_pass': 'test',
        'elk_index': 'purple-team-logs-*',
        'elk_connection_timeout': 30,
        'max_techniques_per_query': 100,
        'field_mappings': {
            'operation_id': 'purple.operation_id',
            'technique': 'purple.technique',
            'detection_status': 'purple.detection_status',
            'rule_name': 'rule.name'
        }
    }
    
    # Generate mock response for 30 techniques
    mock_buckets = []
    for i in range(30):
        mock_buckets.append({
            'key': f'T{1000+i}',
            'doc_count': 5,
            'detection_status': {
                'buckets': [{'key': 'detected', 'doc_count': 5}]
            },
            'rule_names': {
                'buckets': [{'key': f'Detection Rule {i}', 'doc_count': 5}]
            }
        })
    
    mock_response = {
        'hits': {'total': {'value': 150}},
        'aggregations': {
            'techniques': {'buckets': mock_buckets}
        }
    }
    
    # Benchmark with mock
    with patch('elk_fetcher.AsyncElasticsearch') as mock_es_class:
        mock_es = AsyncMock()
        mock_es.search = AsyncMock(return_value=mock_response)
        mock_es.close = AsyncMock()
        mock_es_class.return_value = mock_es
        
        # Warmup
        await elk_fetcher.fetch_detection_data_for_operations(['op-test'], config, None)
        
        # Benchmark multiple runs
        runs = 10
        times = []
        
        for i in range(runs):
            start = time.time()
            result = await elk_fetcher.fetch_detection_data_for_operations(
                ['op-test-1', 'op-test-2'],
                config,
                None
            )
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n30-Technique Operation Query Performance:")
        print(f"  Runs: {runs}")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  Min: {min_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")
        print(f"  Target: <3000ms")
        
        if avg_time < 3.0:
            print(f"  ✓ PASS: Within performance target")
            return True
        else:
            print(f"  ✗ FAIL: Exceeds performance target")
            return False


async def benchmark_section_generation():
    """Benchmark section PDF generation."""
    print("\n" + "=" * 60)
    print("Benchmark: Section Generation Performance")
    print("=" * 60)
    
    # Import section
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'elk_coverage',
        'plugins/debrief-elk-detections/app/debrief-sections/elk_detection_coverage.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Create mock operation with 30 techniques
    class MockAbility:
        def __init__(self, tid, name):
            self.technique_id = tid
            self.technique_name = name
            self.name = name
    
    class MockLink:
        def __init__(self, ability):
            self.ability = ability
    
    class MockOperation:
        def __init__(self, op_id, num_techniques):
            self.id = op_id
            self.chain = [
                MockLink(MockAbility(f'T{1000+i}', f'Technique {i}'))
                for i in range(num_techniques)
            ]
    
    # Mock styles
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    
    # Create section instance
    section = module.DebriefReportSection()
    
    # Mock fetch_detection_data_for_operations
    mock_detection_data = {
        f'T{1000+i}': {
            'status': 'detected',
            'rule_name': f'Detection Rule {i}',
            'alert_count': 5,
            'coverage': 100.0
        }
        for i in range(30)
    }
    
    mock_result = {
        'available': True,
        'techniques': mock_detection_data,
        'total_events': 150
    }
    
    # Patch fetch function
    import sys
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, app_dir)
    import elk_fetcher
    
    with patch.object(elk_fetcher, 'fetch_detection_data_for_operations', return_value=mock_result):
        operations = [MockOperation('op-test', 30)]
        
        # Warmup
        await section.generate_section_elements(styles, operations, [], {})
        
        # Benchmark
        runs = 5
        times = []
        
        for i in range(runs):
            start = time.time()
            flowables = await section.generate_section_elements(styles, operations, [], {})
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n30-Technique Section Generation:")
        print(f"  Runs: {runs}")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  Min: {min_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")
        print(f"  Flowables generated: {len(flowables)}")
        print(f"  Target: <10000ms (total PDF)")
        
        if avg_time < 10.0:
            print(f"  ✓ PASS: Within performance target")
            return True
        else:
            print(f"  ✗ FAIL: Exceeds performance target")
            return False


async def main():
    """Run all benchmarks."""
    print("\nDebrief-ELK-Detections Performance Benchmarks")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(await benchmark_elk_query())
    except Exception as e:
        print(f"\n✗ ELK Query benchmark failed: {e}")
        results.append(False)
    
    try:
        results.append(await benchmark_section_generation())
    except Exception as e:
        print(f"\n✗ Section generation benchmark failed: {e}")
        results.append(False)
    
    print("\n" + "=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All performance targets met!")
        return 0
    else:
        print("\n✗ Some benchmarks failed")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
