import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
def check_site(site, username, headers, session):
    uri_check = site["uri_check"].format(account=username)
    try:
        res = session.get(uri_check, headers=headers, timeout=10)
        estring_pos = site["e_string"] in res.text
        estring_neg = site["m_string"] in res.text
        if res.status_code == site["e_code"] and estring_pos and not estring_neg:
            return site["name"], uri_check
    except:
        pass
    return None
if __name__ == "__main__":
    headers = {
        "Accept": "text/html, application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-US;q=0.9,en,q=0,8",
        "accept-encoding": "gzip, deflate",
        "user-Agent": "Mozilla/5.0 (Windows NT 10.0;Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    }
    with requests.Session() as session:
        response = session.get("https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json")
        data = response.json()
        parser = argparse.ArgumentParser(description="Scan for a specific username across various sites")
        parser.add_argument("username", help="The username to search for")
        args = parser.parse_args()
        username = args.username
        sites = data["sites"]
        total_sites = len(sites)
        found_sites = 0
        try:
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(check_site, site, username, headers, session): site for site in sites}

                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            site_name, uri_check = result
                            print("- \033[32m{}\033[0m: {}".format(site_name, uri_check))
                            found_sites += 1
                    except:
                        pass
        except TimeoutError:
            print("Some sites took too long to respond and were skipped.")
        if found_sites:
            print(f"\nThe user \033[1m{username}\033[0m was found on {found_sites} sites.")
        else:
            print(f"\nNo sites found for the user \033[1m{username}\033[0m.")
