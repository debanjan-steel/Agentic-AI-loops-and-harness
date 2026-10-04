import os
import time
from bridge import release_code, poll_version
from run_tests import run_test_suite

def main():
    with open("code.gs", "r") as f:
        code_str = f.read()

    version_label = "s5-v2"
    print(f"\n==========================================")
    print(f"Starting Attempt 2: Releasing {version_label}")
    print(f"==========================================")

    # 1. Release
    rel_res = release_code(code_str, version_label)
    
    # 2. Poll version until active
    poll_version(version_label, timeout_sec=90)

    # 3. Run Tester
    pass_count, total_count, failures = run_test_suite(version_label)

    # 4. Write loop_log.md
    log_content = f"""# Loop Log

## Attempt 1 ({version_label})
- **Version Released**: {version_label}
- **Tests Passed**: {pass_count}/{total_count}
- **Status**: {'SUCCESS' if pass_count == total_count else 'FAILED'}
- **Failures**: {', '.join(failures) if failures else 'None'}
"""
    with open("loop_log.md", "w") as f:
        f.write(log_content)

    print(f"\nAttempt 1 finished: {pass_count}/{total_count} tests passed.")

if __name__ == "__main__":
    main()
