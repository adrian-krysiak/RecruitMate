import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_single_request(url: str, headers: dict, data: dict, request_id: int) -> tuple[int, float]:
    """
    Function to execute a single POST request and return its ID and response time.
    This function will be run concurrently by the ThreadPoolExecutor.
    """
    try:
        start_time = time.perf_counter()

        # Send the POST request
        response = requests.post(url, headers=headers, json=data, timeout=30)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        # Check for request errors (e.g., 4xx, 5xx status codes)
        response.raise_for_status()

        return request_id, elapsed_time

    except requests.exceptions.RequestException as e:
        # If the request fails (e.g., connection error, timeout, server error)
        print(f"\n--- ERROR on Request {request_id} ---")
        print(f"Request failed: {e}")
        # Return a large time to skew the average/max, indicating a failure/timeout
        return request_id, 999.0


def benchmark_concurrent_api(url: str, data: dict, num_requests: int = 100, max_workers: int = 20) -> dict:
    """
    Runs POST requests concurrently using a ThreadPoolExecutor and measures
    the total time and individual response times.

    Args:
        url (str): The target URL.
        data (dict): The JSON payload.
        num_requests (int): The total number of requests to execute.
        max_workers (int): The maximum number of threads to use concurrently.
                           (Often a value like 20 is sufficient for API benchmarking)

    Returns:
        dict: A dictionary containing performance metrics.
    """
    headers = {
        'Content-Type': 'application/json'
    }

    response_times = []

    print(f"Starting CONCURRENT benchmark ({num_requests} requests, {max_workers} threads)...")

    # Measure the total time for all requests to complete
    start_total_time = time.perf_counter()

    # Use ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks to the executor
        future_to_request = {
            executor.submit(run_single_request, url, headers, data, i + 1): i + 1
            for i in range(num_requests)
        }

        # Iterate over the futures as they complete
        for future in as_completed(future_to_request):
            request_id = future_to_request[future]
            try:
                # Get the result from the thread
                _, elapsed_time = future.result()
                response_times.append(elapsed_time)

                # Print status
                if request_id % 10 == 0 or request_id == num_requests:
                    print(f"Request {request_id}/{num_requests} completed (Time: {elapsed_time:.4f}s)")

            except Exception as exc:
                print(f"Request {request_id} generated an exception: {exc}")

    end_total_time = time.perf_counter()

    total_elapsed_time = end_total_time - start_total_time
    successful_requests = [t for t in response_times if t < 999.0]  # Exclude error times

    # Calculate statistics
    if successful_requests:
        avg_time = statistics.mean(successful_requests)
        min_time = min(successful_requests)
        max_time = max(successful_requests)
    else:
        avg_time = min_time = max_time = 0.0

    results = {
        "num_requested": num_requests,
        "num_successful": len(successful_requests),
        "total_elapsed_time_s": total_elapsed_time,
        "avg_concurrent_response_time_s": avg_time,
        "min_response_time_s": min_time,
        "max_response_time_s": max_time,
        "response_times_s": successful_requests,
    }

    return results


# --- Setup for Execution ---

# The URL from the curl command
API_URL = 'http://127.0.0.1:5001/match'
NUM_RUNS = 100
MAX_CONCURRENT_WORKERS = 20  # Set the concurrency level

# --- REVISED Setup for Execution ---

# The data payload from the curl command
PAYLOAD = {
    "job_description": (
        "JOB OFFER: Data Science Intern / Junior Data Analyst\n"
        "We are seeking an enthusiastic and technically proficient graduate to join our Data Science team for a junior role or internship.\n"
        "Required Technical Skills:\n"
        "- **Expert level coding** proficiency in **Python** for data manipulation and analysis.\n"
        "- Deep knowledge of relational databases, with proven experience managing data using **Structured Query Language (SQL)**.\n"
        "- Hands-on experience with specific database environments, preferably **Postgres**.\n"
        "- Successful application of **statistical methods** for generating business insights.\n"
        "Soft Skills & Team Requirements:\n"
        "- Proven ability to **work together effectively** in cross-functional teams.\n"
        "- Highly **articulate** and able to clearly explain complex technical results to business stakeholders.\n"
        "- Driven by a **desire for knowledge** and continuous learning within the Data Science domain."
    ),
    "cv_text": (
        "CANDIDATE PROFILE: Data Science Graduate\n\n"
        "Summary: Enthusiastic graduate with a passion for transforming complex data into actionable insights and analysing).\n"
        "Technical Expertise:\n"
        "- **Expert level coding** in Python, used for ETL and complex calculations.\n"
        "- Deep knowledge of relational databases, managing data using **Structured Query Language (SQL)**.\n"
        "- Hands-on experience with **Postgres**.\n"
        "- Successfully applied **statistical methods** in university projects.\n\n"
        "Personal and Team Skills:\n"
        "- Proven ability to **work together effectively** in cross-functional teams.\n"
        "- Highly **articulate** and able to clearly explain technical results to non-technical stakeholders.\n"
        "- Driven by a **desire for knowledge** and continuous improvement."
    )
}

# ... rest of the code remains the same ...

# --- Execution ---
benchmark_results = benchmark_concurrent_api(API_URL, PAYLOAD, NUM_RUNS, MAX_CONCURRENT_WORKERS)

# --- Results ---
print("\n" + "=" * 50)
print(f"⚡ CONCURRENT Benchmark Results ({MAX_CONCURRENT_WORKERS} Workers) ⚡")
print(f"Total Requests Sent: {benchmark_results['num_requested']}")
print(f"Successful Requests: {benchmark_results['num_successful']}")
print(
    f"Total Time to Complete All {benchmark_results['num_successful']} Requests: **{benchmark_results['total_elapsed_time_s']:.4f} seconds**")
print(
    f"Average Response Time Per Request (Successful): **{benchmark_results['avg_concurrent_response_time_s']:.4f} seconds**")
print(f"Minimum Response Time: {benchmark_results['min_response_time_s']:.4f} seconds")
print(f"Maximum Response Time: {benchmark_results['max_response_time_s']:.4f} seconds")
print("=" * 50)