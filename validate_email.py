import csv
import re
import socket
import smtplib
import requests
import dns.resolver
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------------------
# GLOBAL HISTORICAL CACHES
# -----------------------------------------
MX_CACHE = {}
DOMAIN_CACHE = {}
WEBSITE_CACHE = {}
SMTP_BANNER_CACHE = {}
SMTP_RESULT_CACHE = {}

# -----------------------------------------
# 1 — REGEX SYNTAX VALIDATION (FASTEST)
# -----------------------------------------
EMAIL_REGEX = re.compile(
    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
)

def validate_syntax(email: str) -> bool:
    return EMAIL_REGEX.match(email) is not None


# -----------------------------------------
# 2 — DOMAIN HEALTH CHECKS
# -----------------------------------------
def check_website(domain: str) -> bool:
    if domain in WEBSITE_CACHE:
        return WEBSITE_CACHE[domain]

    try:
        url = domain
        if not url.startswith("http"):
            url = "http://" + url
        r = requests.get(url, timeout=5)
        WEBSITE_CACHE[domain] = (200 <= r.status_code < 400)
        return WEBSITE_CACHE[domain]
    except:
        WEBSITE_CACHE[domain] = False
        return False


def check_mx(domain: str):
    if domain in MX_CACHE:
        return MX_CACHE[domain]

    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=4)
        recs = [str(r.exchange).rstrip('.') for r in answers]
        MX_CACHE[domain] = recs
        return recs
    except:
        MX_CACHE[domain] = []
        return []


# -----------------------------------------
# 3 — INDIRECT SMTP BANNER ANALYSIS
# -----------------------------------------
def smtp_banner(host: str) -> str:
    if host in SMTP_BANNER_CACHE:
        return SMTP_BANNER_CACHE[host]

    try:
        server = smtplib.SMTP(timeout=5)
        server.connect(host)
        banner = server.sock.recv(1024).decode(errors="ignore")
        server.quit()
        SMTP_BANNER_CACHE[host] = banner
        return banner
    except:
        SMTP_BANNER_CACHE[host] = ""
        return ""


# -----------------------------------------
# 4 — NULL SENDER RFC-COMPLIANT RCPT TEST
# -----------------------------------------
def smtp_null_sender(host: str, email: str) -> int:
    key = host + "|" + email
    if key in SMTP_RESULT_CACHE:
        return SMTP_RESULT_CACHE[key]

    try:
        server = smtplib.SMTP(host, 25, timeout=7)
        server.helo("example.com")
        server.mail("")
        code, msg = server.rcpt(email)
        server.quit()
        SMTP_RESULT_CACHE[key] = code
        return code
    except:
        SMTP_RESULT_CACHE[key] = 0
        return 0


# -----------------------------------------
# 5 — SMART HEURISTICS ENGINE
# -----------------------------------------
def heuristics(banner: str, rcpt_code: int) -> str:
    b = banner.lower()

    # Gmail fingerprint
    if "google" in b:
        if rcpt_code == 250: return "alive"
        if rcpt_code in [550, 551, 553]: return "dead"
        return "unknown"

    # Outlook fingerprint
    if "outlook" in b or "microsoft" in b:
        if rcpt_code == 250: return "alive"
        if rcpt_code == 550: return "dead"
        return "unknown"

    # Generic patterns
    if rcpt_code == 250: return "alive"
    if rcpt_code in [550, 551, 552, 553]: return "dead"

    return "unknown"


# -----------------------------------------
# 6 — FULL PIPELINE VALIDATOR
# -----------------------------------------
def validate_email_pipeline(email: str, web: str = None):
    # Stage 1 — Syntax
    if not validate_syntax(email):
        return "fail", "bad_syntax"

    domain = email.split("@")[-1].strip()

    # Stage 2 — Website Presence
    if web:
        if not check_website(web):
            return "fail", "website_down"

    # Stage 3 — Domain MX Check
    mx = check_mx(domain)
    if not mx:
        return "fail", "no_mx"

    mx_host = mx[0]

    # Stage 4 — SMTP Banner
    banner = smtp_banner(mx_host)

    # Stage 5 — Null Sender RCPT
    rcpt_code = smtp_null_sender(mx_host, email)

    # Stage 6 — Smart Heuristics
    decision = heuristics(banner, rcpt_code)

    if decision == "alive":
        return "pass", ""
    return "fail", decision


# -----------------------------------------
# 7 — BULK CSV PROCESSOR (MULTITHREADED)
# -----------------------------------------
def process_row(row):
    email = row.get("Email", "").strip()
    web = row.get("Web Address", "").strip()
    status, reason = validate_email_pipeline(email, web)
    row["Validation Status"] = status
    row["Validation Reason"] = reason
    return row


def process_csv(input_file, pass_file="pass.csv", fail_file="fail.csv", workers=25):
    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames + ["Validation Status", "Validation Reason"]
        rows = list(reader)

    pass_rows = []
    fail_rows = []

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(process_row, row): row for row in rows}

        for fut in tqdm(as_completed(futures), total=len(rows), desc="Validating"):
            result = fut.result()
            if result["Validation Status"] == "pass":
                pass_rows.append(result)
            else:
                fail_rows.append(result)

    # Save results
    with open(pass_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(pass_rows)

    with open(fail_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(fail_rows)

    print(f"\n✓ Completed.")
    print(f"Passed: {len(pass_rows)}")
    print(f"Failed: {len(fail_rows)}")
    print(f"Output → {pass_file}, {fail_file}")


# -----------------------------------------
# CLI
# -----------------------------------------
if __name__ == "__main__":
    filename = input("Enter CSV filename: ").strip()
    process_csv(filename)
