

````markdown
# Validate Email Python Package

Validate_email is a lightweight Python package designed to verify if an email address is valid, properly formatted, and actually exists. It can also optionally check the associated website for the email's domain, ensuring comprehensive validation.

## Installation

Install the core package via pip:

```bash
pip install validate_email
````

### Extra Dependencies

For advanced features like checking domain MX records, verifying email existence, and website availability, install these additional packages:

```bash
pip install pyDNS requests dnspython tqdm
```

These enable MX lookups, HTTP requests for websites, DNS resolution, and efficient multithreaded processing.

## Usage

### Basic Validation

Check if an email is properly formatted and syntactically correct:

```python
from validate_email import validate_email_pipeline

status, reason = validate_email_pipeline('example@example.com')
print(status, reason)  # Output: True, None (if valid)
```

### Check Domain SMTP Server

Verify the email domain's SMTP server availability:

```python
from validate_email import validate_email_pipeline

status, reason = validate_email_pipeline('example@example.com', web='example.com')
print(status, reason)
```

### Full Verification

Perform a complete check: email syntax, website availability, MX records, and optional SMTP RCPT verification:

```python
from validate_email import validate_email_pipeline

status, reason = validate_email_pipeline('example@example.com', web='www.example.com')
print(status, reason)
```

> Note: The package automatically prepends `https://` to domains like `www.example.com` for secure website checks.

### CSV Bulk Processing

Process large lists of emails from a CSV file. Your CSV should have these columns:

| Column      | Description          |
| ----------- | -------------------- |
| Email       | The email address    |
| Web Address | Optional website URL |

Run the bulk validation script:

```bash
python validate_email_pipeline.py
```

* Input: Prompt for your CSV filename.
* Output:

  * `pass.csv`: Validated emails.
  * `fail.csv`: Failed emails with detailed reasons.

> This feature uses multithreading for speed on large datasets.

## Features

* Email Syntax Validation: Ensures proper formatting.
* Website Availability Check: Tests if the domain's website is reachable.
* MX Records Verification: Confirms the domain has valid mail servers.
* SMTP RCPT Check: Optional deep verification to see if the email truly exists.
* Multithreaded Processing: Handles bulk validations efficiently.
* Smart Heuristics: Combines all checks for reliable decisions.

## Example CSV Input

```csv
Email,Web Address
onimisiadeolu@gmail.com,www.google.com
someone@example.com,example.com
test@outlook.com,www.microsoft.com
```

## Contribution

I (Reabot6) have added enhancements and improvements to the original project.
All contributions must respect the original license:

* Fork the repository.
* Add new features, fix bugs, or refine validation logic.
* Submit a Pull Request with clear descriptions.

> Original project by [Syrus Akbary](https://github.com/syrusakbary/validate_email)

## License

This project is licensed under the MIT License. The original code is © Syrus Akbary. My contributions are © Reabot6.

## Contact

GitHub: [reabot6](https://github.com/reabot6)
Website: [reabotportfolios.vercel.app](https://reabotportfolios.vercel.app)
