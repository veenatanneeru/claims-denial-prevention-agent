"""Write fictional payer policy documents used by the RAG agent."""
from pathlib import Path

POLICIES = {
    "prior_auth_mri.md": """# Policy PA-101: Prior Authorization for Advanced Imaging
Applies to CPT 70553 (MRI brain with and without contrast) and 72148 (MRI lumbar spine).
Prior authorization is required for all non-emergency outpatient MRI studies.
Claims submitted without an authorization number are denied as "authorization not obtained".
Retroactive authorization is not available after the date of service.
""",
    "prior_auth_surgery.md": """# Policy PA-102: Prior Authorization for Elective Joint Replacement
Applies to CPT 27447 (total knee arthroplasty).
Requires prior authorization, documented failure of at least 3 months of conservative therapy,
and imaging showing joint degeneration. Missing documentation results in denial or pend for review.
""",
    "timely_filing.md": """# Policy TF-201: Timely Filing
Claims must be submitted within 90 days of the date of service.
Claims filed after 90 days are denied unless the provider shows proof of an earlier timely submission
or a payer-caused delay. Medicare claims follow a separate 12-month limit.
""",
    "network_status.md": """# Policy NW-301: Network Participation
Services from out-of-network providers are reimbursed at a reduced rate or denied for HMO-type plans.
Emergency services are exempt. Providers should verify network status on the date of service.
""",
    "medical_necessity.md": """# Policy MN-401: Diagnosis and Procedure Consistency
The diagnosis code must support the medical necessity of the billed procedure.
Mismatched diagnosis and procedure codes are the most common reason for medical-necessity denials.
Example: lumbar MRI (72148) must be supported by a back-pain or disc diagnosis such as M54.50 or M51.16.
""",
    "evaluation_management.md": """# Policy EM-501: Office Visits (CPT 99213, 99214)
Office visits do not require prior authorization. The level billed must match documented complexity.
Repeated high-level visits for the same diagnosis within 14 days may be flagged for review.
""",
    "colonoscopy.md": """# Policy SC-601: Colonoscopy (CPT 45378)
Screening colonoscopies for average-risk patients are covered without cost sharing.
Diagnostic colonoscopy requires a supporting diagnosis such as Z12.11 or K92.1.
Prior authorization is not required.
""",
    "physical_therapy.md": """# Policy PT-701: Therapeutic Exercise (CPT 97110)
Coverage is limited to 20 visits per calendar year. Claims must include a supporting musculoskeletal
diagnosis such as M54.50 or M17.11. Visits beyond the limit require a medical necessity review.
""",
    "appeals.md": """# Policy AP-801: Appeals Process
Denied claims may be appealed within 180 days of the denial notice.
Include the denial reason, corrected claim data, and supporting clinical documentation.
Common fixes: attach the authorization number, correct the diagnosis code, or submit proof of timely filing.
""",
}

if __name__ == "__main__":
    out = Path(__file__).parent / "policies"
    out.mkdir(exist_ok=True)
    for name, text in POLICIES.items():
        (out / name).write_text(text)
    print(f"wrote {len(POLICIES)} policy files to {out}")