import requests
import json
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
from .config import CONFERENCE_LIST, YEARS, CONFERENCE


def get_conference(url: str):
    """Return the conference name based on substring match in the URL."""
    for conf in CONFERENCE:
        if conf.lower() in url.lower():
            return conf
    return "Unknown"


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
                    results.append({
                        "year": year,
                        "conference": get_conference(url_checked),
                        "url": url_checked
                    })
                else:
                    print(f"[{year}] {url_checked} --> ❌ {error}")
            except Exception as e:
                print(f"[{year}] {url} --> ❌ Unexpected error: {e}")

    # Group results by (year, conference)
    merged_results = defaultdict(list)
    for item in results:
        merged_results[(item["year"], item["conference"])].append(item["url"])

    # Sort by year (descending)
    sorted_results = sorted(merged_results.items(), key=lambda x: x[0][0], reverse=True)

    # Write README.md
    lines = ["# Conference Link Status\n"]
    lines.append(f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")
    lines.append("\n| Year | Conference | Links |")
    lines.append("|------|-------------|--------|")

    for (year, conference), urls in sorted_results:
        link_list = [f"[Link {i+1}]({url})" for i, url in enumerate(urls)]
        lines.append(f"| {year} | {conference} | {'; '.join(link_list)} |")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Dump JSONL file
    with open("results.jsonl", "w", encoding="utf-8") as f_jsonl:
        for (year, conference), urls in sorted_results:
            record = {
                "year": year,
                "conference": conference,
                "links": urls
            }
            f_jsonl.write(json.dumps(record) + "\n")

    print(f"\n✅ Found {len(results)} valid links merged into {len(sorted_results)} entries — written to README.md and results.jsonl")


if __name__ == "__main__":
    main()
