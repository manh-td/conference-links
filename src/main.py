import requests
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from .config import CONFERENCE_LIST, YEARS  # assumes these are defined elsewhere


def check_url(url: str) -> tuple[str, str, str]:
    """
    Check if a URL exists (returns status code 200–399).
    Returns (url, status_text, error_message)
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code < 400:
            return url, "✅ Exists", ""
        else:
            return url, f"❌ HTTP {response.status_code}", f"HTTP {response.status_code}"
    except requests.Timeout:
        return url, "❌ Timeout", "Timeout"
    except requests.ConnectionError:
        return url, "❌ Connection Error", "Connection Error"
    except requests.RequestException as e:
        return url, "❌ Request Failed", str(e)


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
                url_checked, status, error = future.result()
                if status == "✅ Exists":
                    results.append((year, url_checked, status))
                else:
                    print(f"[{year}] {url_checked} --> {status} ({error})")
            except Exception as e:
                print(f"[{year}] {url} --> ❌ Unexpected error: {e}")

    # Write only existing links to README.md
    lines = ["# Conference Link Status\n"]
    lines.append(f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")
    lines.append("\n| Year | Conference URL | Status |")
    lines.append("|------|----------------|--------|")

    # Sort results for nicer readability
    for year, url, status in sorted(results, key=lambda x: (x[0], x[1])):
        lines.append(f"| {year} | [{url}]({url}) | {status} |")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n✅ Found {len(results)} valid links — written to README.md")


if __name__ == "__main__":
    main()
