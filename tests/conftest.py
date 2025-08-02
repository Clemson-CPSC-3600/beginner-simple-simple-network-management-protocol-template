#!/usr/bin/env python3
"""
Pytest Configuration for SNMP Autograder
Handles test setup, teardown, and fixtures
"""

import pytest
import subprocess
import socket
import time
import os
import sys
import signal
import json
import tempfile
import shutil
from typing import Generator, Tuple, Optional
# Add tests directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from integration.common import wait_for_port, kill_process_on_port

# Test configuration
TEST_TIMEOUT = 30  # Maximum time for any single test
AGENT_START_TIMEOUT = 5  # Time to wait for agent to start
DEFAULT_TEST_PORT = 11610  # Base port for tests (will increment if needed)

# Point allocation for grading
TOTAL_POINTS = 100
POINT_CATEGORIES = {
    'protocol_compliance': 25,
    'buffering': 20,
    'get_operations': 20,
    'set_operations': 15,
    'error_handling': 10,
    'code_quality': 10
}


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--solution",
        action="store_true",
        default=False,
        help="Test solution files instead of student files"
    )


def pytest_configure(config):
    """Configure pytest with custom markers"""
    # Set environment variable based on command line option
    if config.getoption("--solution"):
        os.environ['SNMP_TEST_SOLUTION'] = 'true'
        print("\n" + "="*60)
        print("TESTING SOLUTION FILES")
        print("="*60 + "\n")
    else:
        os.environ['SNMP_TEST_SOLUTION'] = 'false'
    
    config.addinivalue_line(
        "markers", "points(n): mark test with point value"
    )
    config.addinivalue_line(
        "markers", "category(name): mark test with grading category"
    )
    config.addinivalue_line(
        "markers", "timeout(seconds): set custom timeout for test"
    )
    config.addinivalue_line(
        "markers", "requires_agent: test requires SNMP agent to be available"
    )
    config.addinivalue_line(
        "markers", "requires_manager: test requires SNMP manager to be available"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add metadata"""
    for item in items:
        # Add default timeout if not specified
        if not any(marker.name == 'timeout' for marker in item.iter_markers()):
            item.add_marker(pytest.mark.timeout(TEST_TIMEOUT))


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment for the entire session"""
    # Create temporary directory for test artifacts
    test_dir = tempfile.mkdtemp(prefix="snmp_test_")
    
    # Set up environment variables
    original_env = os.environ.copy()
    os.environ['SNMP_TEST_MODE'] = '1'
    os.environ['SNMP_TEST_DIR'] = test_dir
    
    yield test_dir
    
    # Cleanup
    os.environ.clear()
    os.environ.update(original_env)
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def find_free_port():
    """Find an available port for testing"""
    def _find_port(base_port: int = DEFAULT_TEST_PORT) -> int:
        for offset in range(100):  # Try 100 ports
            port = base_port + offset
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                continue
        raise RuntimeError("Could not find free port")
    
    return _find_port


@pytest.fixture
def start_agent(find_free_port):
    """Start an SNMP agent for testing"""
    agents = []
    
    def _start_agent(port: Optional[int] = None, 
                    env_vars: Optional[dict] = None,
                    wait: bool = True) -> Tuple[subprocess.Popen, int]:
        if port is None:
            port = find_free_port()
        
        # Kill any existing process on this port
        kill_process_on_port(port)
        time.sleep(0.1)
        
        # Set up environment
        env = os.environ.copy()
        env['SNMP_AGENT_PORT'] = str(port)
        if env_vars:
            env.update(env_vars)
        
        # Start agent - use solution path if configured
        use_solution = os.environ.get('SNMP_TEST_SOLUTION', 'false').lower() == 'true'
        if use_solution:
            agent_path = os.path.join('solution', 'snmp_agent.py')
            if not os.path.exists(agent_path):
                agent_path = 'snmp_agent.py'  # Fallback
            # Add solution directory to PYTHONPATH so imports work correctly
            solution_dir = os.path.abspath('solution')
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = solution_dir + os.pathsep + env['PYTHONPATH']
            else:
                env['PYTHONPATH'] = solution_dir
        else:
            agent_path = 'snmp_agent.py'
        
        cmd = [sys.executable, agent_path]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            preexec_fn=os.setsid if sys.platform != 'win32' else None
        )
        
        agents.append((proc, port))
        
        if wait:
            # Wait for agent to start
            if not wait_for_port(port, timeout=AGENT_START_TIMEOUT):
                proc.terminate()
                stdout, stderr = proc.communicate(timeout=1)
                raise RuntimeError(
                    f"Agent failed to start on port {port}\n"
                    f"stdout: {stdout.decode()}\n"
                    f"stderr: {stderr.decode()}"
                )
        
        return proc, port
    
    yield _start_agent
    
    # Cleanup all started agents
    for proc, port in agents:
        try:
            if sys.platform == 'win32':
                proc.terminate()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=2)
        except:
            proc.kill()
            proc.wait()


@pytest.fixture
def create_test_agent(start_agent):
    """Create a test agent and return its port"""
    def _create():
        _, port = start_agent()
        return port
    return _create


@pytest.fixture
def snmp_client():
    """Create an SNMP client socket"""
    sockets = []
    
    def _create_client(port: int) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)  # 5 second timeout
        sock.connect(('localhost', port))
        sockets.append(sock)
        return sock
    
    yield _create_client
    
    # Cleanup
    for sock in sockets:
        try:
            sock.close()
        except:
            pass


@pytest.fixture
def capture_network_traffic():
    """Capture network traffic for debugging (if available)"""
    # This could integrate with tcpdump or Wireshark if needed
    # For now, just a placeholder
    yield None




@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Process test results for grading"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # Extract points from marker
        points_marker = item.get_closest_marker('points')
        points = points_marker.args[0] if points_marker else 0
        
        # Store result in item's stash
        if not hasattr(item.config, '_test_results'):
            item.config._test_results = []
        
        item.config._test_results.append({
            'test': item.nodeid,
            'points': points,
            'passed': report.passed
        })


def pytest_sessionfinish(session, exitstatus):
    """Generate final grade report"""
    if hasattr(session.config, '_test_results'):
        results = session.config._test_results
        
        # Calculate totals
        total_points = sum(r['points'] for r in results)
        earned_points = sum(r['points'] for r in results if r['passed'])
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        
        # Group by category
        categories = {}
        for result in results:
            cat = _get_category(result['test'])
            if cat not in categories:
                categories[cat] = {'earned': 0, 'possible': 0}
            categories[cat]['possible'] += result['points']
            if result['passed']:
                categories[cat]['earned'] += result['points']
        
        # Calculate percentages
        for cat in categories.values():
            cat['percentage'] = (cat['earned'] / cat['possible'] * 100) if cat['possible'] > 0 else 0
        
        # Save results
        summary = {
            'total_score': earned_points,
            'total_possible': total_points,
            'percentage': percentage,
            'categories': categories,
            'test_results': results
        }
        
        try:
            with open('autograder_results.json', 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save results: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("AUTOGRADER RESULTS")
        print("="*60)
        print(f"Total Score: {earned_points:.1f}/{total_points:.1f} ({percentage:.1f}%)")
        print("\nCategory Breakdown:")
        for cat_name, data in categories.items():
            print(f"  {cat_name.replace('_', ' ').title()}: {data['earned']:.1f}/{data['possible']:.1f} ({data['percentage']:.1f}%)")
        print("="*60)


def _get_category(test_name: str) -> str:
    """Extract category from test class name"""
    if 'Protocol' in test_name or 'MessageHeader' in test_name:
        return 'protocol_compliance'
    elif 'Buffering' in test_name:
        return 'buffering'
    elif 'GetOperation' in test_name:
        return 'get_operations'
    elif 'SetOperation' in test_name:
        return 'set_operations'
    elif 'Error' in test_name:
        return 'error_handling'
    else:
        return 'code_quality'


@pytest.fixture
def mock_mib_database():
    """Provide a mock MIB database for testing"""
    return {
        '1.3.6.1.2.1.1.1.0': ('STRING', 'Test System Description'),
        '1.3.6.1.2.1.1.2.0': ('OID', '1.3.6.1.4.1.9.1.1234'),
        '1.3.6.1.2.1.1.3.0': ('TIMETICKS', 0),
        '1.3.6.1.2.1.1.4.0': ('STRING', 'test@example.com'),
        '1.3.6.1.2.1.1.5.0': ('STRING', 'test-system'),
        '1.3.6.1.2.1.1.6.0': ('STRING', 'Test Location'),
        '1.3.6.1.2.1.1.7.0': ('INTEGER', 72),
    }


@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests"""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = []
        
        def record(self, test_name: str, metric_name: str, value: float):
            self.metrics.append({
                'test': test_name,
                'metric': metric_name,
                'value': value,
                'timestamp': time.time()
            })
        
        def get_summary(self) -> dict:
            summary = {}
            for metric in self.metrics:
                key = f"{metric['test']}:{metric['metric']}"
                if key not in summary:
                    summary[key] = []
                summary[key].append(metric['value'])
            
            # Calculate averages
            result = {}
            for key, values in summary.items():
                result[key] = {
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
            return result
    
    return PerformanceMonitor()


# Timeout handler for tests
def timeout_handler(signum, frame):
    raise TimeoutError("Test exceeded time limit")


if sys.platform != 'win32':
    signal.signal(signal.SIGALRM, timeout_handler)