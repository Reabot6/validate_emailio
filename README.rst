Validate Email Python PackageValidate Email Banner
(Placeholder for a banner image – consider adding a custom graphic for better appeal!)Validate_email is a lightweight Python package designed to verify if an email address is valid, properly formatted, and actually exists. It can also optionally check the associated website for the email's domain, ensuring comprehensive validation. InstallationInstall the core package easily via pip:bash

pip install validate_email

 Extra DependenciesFor advanced features like checking domain MX records, verifying email existence, and website availability, install these additional packages:bash

pip install pyDNS requests dnspython tqdm

These enable MX lookups, HTTP requests for websites, DNS resolution, and efficient multithreaded processing. UsageBasic ValidationCheck if an email is properly formatted and syntactically correct:python

from validate_email import validate_email_pipeline

status, reason = validate_email_pipeline('example@example.com')
print(status, reason)  # Output: True, None (if valid)

Check Domain SMTP ServerVerify the email domain's SMTP server availability:python

from validate_email import validate_email_pipeline

status, reason = validate_email_pipeline('example@example.com', web='example.com')
print(status, reason)

Full VerificationPerform a complete check: email syntax, website availability, MX records, and optional SMTP RCPT verification for maximum confidence:python

from validate_email import validate_email_pipeline

status, reason = validate_email_pipeline('example@example.com', web='www.example.com')
print(status, reason)

Note: The package automatically prepends https:// to domains like www.example.com for secure website checks.
 CSV Bulk ProcessingProcess large lists of emails from a CSV file. Your CSV should have these columns:Column
Description
Email
The email address
Web Address
Optional website URL

Run the bulk validation script:bash

python validate_email_pipeline.py

Input: Prompt for your CSV filename.
Output:pass.csv: Validated emails.
fail.csv: Failed emails with detailed reasons.

This feature uses multithreading for speed on large datasets! Features Email Syntax Validation: Ensures proper formatting.
 Website Availability Check: Tests if the domain's website (e.g., https://www.example.com) is reachable.
 MX Records Verification: Confirms the domain has valid mail servers.
 SMTP RCPT Check: Optional deep verification to see if the email truly exists (use with caution for privacy).
 Multithreaded Processing: Handles bulk validations efficiently.
 Smart Heuristics: Combines all checks for intelligent, reliable decisions.

 Example CSV Inputcsv

Email,Web Address
onimisiadeolu@gmail.com,www.google.com
someone@example.com,example.com
test@outlook.com,www.microsoft.com

 ContributionWe welcome improvements! Here's how to contribute:Fork the repository.
Add new features, fix bugs, or refine validation logic.
Submit a Pull Request with clear descriptions.

Your ideas can make this package even better! LicenseThis project is licensed under the MIT License. Feel free to use, modify, and distribute. ContactGitHub: reabot6
Website: reabotportfolios.vercel.app

If you have questions or suggestions, open an issue on GitHub!Built with  by reabot6. Star the repo if you find it useful!

