import requests
import json
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from .config import CONFERENCE_LIST, YEARS  # assumes these are defined elsewhere


def check_url(url: str) -> tuple[str, bool, str]:
    """
    Check if a URL exists (returns status code 200–399).
    Returns (url, exists, error_message)
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        exists = response.status_code < 400
        return url, exists, "" if exists else f"HTTP {response.status_code}"
    except requests.Timeout:
        return url, False, "Timeout"
    except requests.ConnectionError:
        return url, False, "Connection Error"
    except requests.RequestException as e:
        return url, False, str(e)


def build_url_list():
    """Generate all (year, url) combinations."""
    return [(year, template.format(year=year)) for year in YEARS for template in CONFERENCE_LIST]


def main():
    urls_to_check = build_url_list()
    results = []

    print(f"🔍 Checking {len(urls_to_check)} URLs using ProcessPoolExecutor...\n")

    # Run checks in parallel
    with ProcessPoolExecutor() as executor:
        future_to_data = {executor.submit(check_url, url): (year, url) for year, url in urls_to_check}

        for future in as_completed(future_to_data):
            year, url = future_to_data[future]
            try:
                url_checked, exists, error = future.result()
                if exists:
                    results.append({"year": year, "url": url_checked})
                else:
                    print(f"[{year}] {url_checked} --> ❌ {error}")
            except Exception as e:
                print(f"[{year}] {url} --> ❌ Unexpected error: {e}")

    # Reverse the list so newest year is first
    results_sorted = sorted(results, key=lambda x: x["year"], reverse=True)

    # Write README.md
    lines = ["# Conference Link Status\n"]
    lines.append(f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")
    lines.append("\n| Year | Conference URL |")
    lines.append("|------|----------------|")

    for item in results_sorted:
        lines.append(f"| {item['year']} | [{item['url']}]({item['url']}) |")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Dump JSONL file
    with open("results.jsonl", "w", encoding="utf-8") as f_jsonl:
        for item in results_sorted:
            f_jsonl.write(json.dumps(item) + "\n")

    print(f"\n✅ Found {len(results_sorted)} valid links — written to README.md and results.jsonl")


if __name__ == "__main__":
    main()
