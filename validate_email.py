import csv
import re
import socket
import smtplib
import requests
import dns.resolver
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

# -------------------------
# CACHES
# -------------------------
MX_CACHE = {}
WEBSITE_CACHE = {}
SMTP_BANNER_CACHE = {}
SMTP_RESULT_CACHE = {}

# -------------------------
# REGEX SYNTAX
# -------------------------
EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

def validate_syntax(email: str) -> bool:
    if not email or "@" not in email:
        return False
    return EMAIL_REGEX.match(email.strip()) is not None

# -------------------------
# WEBSITE PRESENCE (convert www → https automatically)
# -------------------------
def check_website(domain: str) -> bool:
    if not domain:
        return False

    if domain in WEBSITE_CACHE:
        return WEBSITE_CACHE[domain]

    domain = domain.strip()

    # Convert www.* or bare domain to https://www.domain or https://domain
    if domain.startswith("www."):
        url = "https://" + domain
    elif not domain.startswith("http://") and not domain.startswith("https://"):
        url = "https://" + domain
    else:
        url = domain

    try:
        r = requests.get(url, timeout=6)
        WEBSITE_CACHE[domain] = (200 <= r.status_code < 400)
        return WEBSITE_CACHE[domain]
    except:
        WEBSITE_CACHE[domain] = False
        return False

# -------------------------
# MX RECORD CHECK
# -------------------------
def check_mx(domain: str, lifetime: float = 5.0) -> List[str]:
    domain = domain.lower().strip()
    if domain in MX_CACHE:
        return MX_CACHE[domain]

    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=lifetime)
        recs = sorted([str(r.exchange).rstrip(".") for r in answers])
        MX_CACHE[domain] = recs
        return recs
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.DNSException):
        MX_CACHE[domain] = []
        return []

# -------------------------
# SMTP BANNER
# -------------------------
def smtp_banner(host: str, port: int = 25, timeout: float = 6.0) -> str:
    key = f"{host}:{port}"
    if key in SMTP_BANNER_CACHE:
        return SMTP_BANNER_CACHE[key]

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            banner = sock.recv(1024).decode(errors="ignore").strip()
            SMTP_BANNER_CACHE[key] = banner
            return banner
    except Exception:
        SMTP_BANNER_CACHE[key] = ""
        return ""

# -------------------------
# NULL SENDER RCPT CHECK
# -------------------------
def smtp_null_sender(host: str, email: str, port: int = 25, timeout: float = 8.0) -> int:
    key = f"{host}:{port}|{email}"
    if key in SMTP_RESULT_CACHE:
        return SMTP_RESULT_CACHE[key]

    code = 0
    try:
        server = smtplib.SMTP(host=host, port=port, timeout=timeout)
        server.set_debuglevel(0)
        try:
            server.ehlo()
        except Exception:
            try:
                server.helo()
            except Exception:
                pass
        server.mail('')
        rcpt = server.rcpt(email)
        if isinstance(rcpt, tuple) and len(rcpt) >= 1:
            raw_code = rcpt[0]
            try:
                code = int(raw_code)
            except Exception:
                try:
                    code = int(raw_code.decode() if isinstance(raw_code, bytes) else raw_code)
                except Exception:
                    code = 0
        server.quit()
    except Exception:
        code = 0

    SMTP_RESULT_CACHE[key] = code
    return code

# -------------------------
# HEURISTICS
# -------------------------
def heuristics(banner: str, rcpt_code: int, website_up: bool) -> str:
    b = (banner or "").lower()
    if rcpt_code is None:
        rcpt_code = 0

    if "google" in b or "gmail" in b:
        if rcpt_code == 250: return "alive"
        if rcpt_code in (550, 551, 553): return "dead"
        return "unknown" if not website_up else "likely_alive"

    if "outlook" in b or "microsoft" in b or "hotmail" in b:
        if rcpt_code == 250: return "alive"
        if rcpt_code in (550, 551, 553): return "dead"
        return "unknown" if not website_up else "likely_alive"

    if rcpt_code == 250:
        return "alive"
    if rcpt_code in (550, 551, 552, 553):
        return "dead"
    if website_up and rcpt_code == 0:
        return "likely_alive"
    return "unknown"

# -------------------------
# FULL PIPELINE
# -------------------------
def validate_email_pipeline(email: str, web: str = None) -> Tuple[str, str]:
    email = (email or "").strip()
    web = (web or "").strip()

    if not validate_syntax(email):
        return "fail", "bad_syntax"

    domain = email.split("@")[-1].strip().lower()
    if not domain:
        return "fail", "bad_domain"

    website_up = False
    if web:
        website_up = check_website(web)

    mx = check_mx(domain)
    fallback_hosts = mx if mx else [domain]

    banner = ""
    rcpt_code = 0
    for host in fallback_hosts:
        banner = smtp_banner(host)
        rcpt_code = smtp_null_sender(host, email)
        if rcpt_code in (250, 550, 551, 552, 553):
            break

    decision = heuristics(banner, rcpt_code, website_up)

    if website_up and mx and rcpt_code == 250:
        return "pass", "website_up_mx_rcpt250"
    if decision == "alive" or decision == "likely_alive":
        return "pass", decision
    return "fail", decision

# -------------------------
# CSV / Bulk
# -------------------------
def process_row(row: dict) -> dict:
    email = row.get("Email", "").strip()
    web = row.get("Web Address", "").strip()
    status, reason = validate_email_pipeline(email, web)
    row["Validation Status"] = status
    row["Validation Reason"] = reason
    return row

def process_csv(input_file: str, pass_file: str = "pass.csv", fail_file: str = "fail.csv", workers: int = 10):
    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or []) + ["Validation Status", "Validation Reason"]
        rows = list(reader)

    pass_rows = []
    fail_rows = []

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(process_row, row) for row in rows]
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Validating"):
            try:
                result = fut.result()
            except Exception as e:
                result = {"Email": "", "Web Address": "", "Validation Status": "fail", "Validation Reason": f"exception:{e}"}
            if result.get("Validation Status") == "pass":
                pass_rows.append(result)
            else:
                fail_rows.append(result)

    with open(pass_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(pass_rows)

    with open(fail_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(fail_rows)

    print(f"\n✓ Completed. Passed: {len(pass_rows)}  Failed: {len(fail_rows)}")
    print(f"Outputs → {pass_file}, {fail_file}")

# CLI
if __name__ == "__main__":
    fname = input("Enter CSV filename: ").strip()
    process_csv(fname)
