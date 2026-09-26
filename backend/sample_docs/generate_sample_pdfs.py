import os
import fitz  # PyMuPDF

def generate_all_sample_pdfs():
    out_dir = os.path.dirname(__file__)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Master Services Agreement
    doc1 = fitz.open()
    p1 = doc1.new_page()
    p1.insert_text((50, 50), """MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is dated January 15, 2026, by and between Alpha Tech Solutions LLC ("Client") and Apex Global Consulting Inc. ("Provider").

1. SCOPE & SERVICES
1.1 Provider shall perform enterprise software implementation, cloud architecture setup, and technical maintenance.
1.2 Standard of Care. All services shall be performed in accordance with highest industry standards.

2. COMPENSATION & PAYMENT TERMS
2.1 Monthly Retainer Fee: Client shall pay Provider $12,500 per month.
2.2 Payment Due Date: Invoices are due within thirty (30) days of receipt.
2.3 Late Payment Charge: Overdue payments accrue interest at 1.5% per month.
""", fontsize=11)

    p2 = doc1.new_page()
    p2.insert_text((50, 50), """3. INTELLECTUAL PROPERTY & CONFIDENTIALITY
3.1 IP Rights: Custom code written under this Agreement shall belong to Client.
3.2 Pre-existing IP: Provider retains ownership of pre-existing core frameworks.
3.3 Non-Disclosure: Confidential information disclosed shall be kept strictly confidential.

4. TERM & AUTOMATIC RENEWAL
4.1 Term: 12 months starting from Effective Date.
4.2 Automatic Renewal: Agreement automatically renews for consecutive 12-month periods unless notice of non-renewal is delivered at least 60 days prior to term end.
""", fontsize=11)

    p3 = doc1.new_page()
    p3.insert_text((50, 50), """5. TERMINATION & INDEMNIFICATION
5.1 Termination for Cause: Either party may terminate upon 15 days written notice for material breach.
5.2 Early Termination Fee: Client shall pay 40% of remaining fees if terminated without cause.
5.3 Governing Law: Governed by the laws of the State of Delaware.
""", fontsize=11)
    doc1.save(os.path.join(out_dir, "sample_service_agreement.pdf"))
    doc1.close()

    # 2. Employment Agreement
    doc2 = fitz.open()
    p1 = doc2.new_page()
    p1.insert_text((50, 50), """EXECUTIVE EMPLOYMENT AGREEMENT

This Executive Employment Agreement ("Agreement") is entered into on February 1, 2026, between Horizon Innovations Inc. ("Company") and Jane Doe ("Employee").

1. POSITION & DUTIES
1.1 Position: Vice President of Engineering.
1.2 Responsibilities: Employee shall oversee product architecture, team management, and strategic technology direction.

2. COMPENSATION & BENEFIT PACKAGE
2.1 Base Salary: Annual base salary of $220,000 paid semi-monthly.
2.2 Executive Bonus: Eligible for annual performance bonus up to 25% of base salary.
""", fontsize=11)

    p2 = doc2.new_page()
    p2.insert_text((50, 50), """3. RESTRICTIVE COVENANTS
3.1 Non-Compete: During employment and for twelve (12) months thereafter, Employee shall not engage with direct competitors in North America.
3.2 Non-Solicitation: Employee shall not solicit employees or customers for 18 months following separation.

4. NOTICE PERIOD & TERMINATION
4.1 Resignation Notice: Employee must provide ninety (90) days advance written notice prior to voluntary resignation.
4.2 Severance: Upon termination without Cause, Employee receives 6 months base salary.
""", fontsize=11)

    p3 = doc2.new_page()
    p3.insert_text((50, 50), """5. INTELLECTUAL PROPERTY ASSIGNMENT
5.1 Inventions: All software, patents, and designs created during employment belong to Company.
5.2 Governing Law: Governed by California law.
""", fontsize=11)
    doc2.save(os.path.join(out_dir, "sample_employment_agreement.pdf"))
    doc2.close()

    # 3. Rental Agreement
    doc3 = fitz.open()
    p1 = doc3.new_page()
    p1.insert_text((50, 50), """COMMERCIAL REAL ESTATE LEASE AGREEMENT

This Lease Agreement ("Lease") is made on March 10, 2026, between Metro Properties LLC ("Landlord") and Nova Software Corp ("Tenant").

1. PREMISES & TERM
1.1 Premises: Suite 400, 500 Market Street, San Francisco, CA.
1.2 Lease Term: Initial term of three (3) years starting April 1, 2026.

2. RENT & SECURITY DEPOSIT
2.1 Monthly Base Rent: $8,500 due on the 1st of each month.
2.2 Security Deposit: $17,000 deposited upon execution.
""", fontsize=11)

    p2 = doc3.new_page()
    p2.insert_text((50, 50), """3. MAINTENANCE & UTILITIES
3.1 Operational Expenses: Tenant pays proportionate share of HVAC and building common area maintenance.
3.2 Alterations: Tenant shall not make structural modifications without Landlord consent.

4. LEASE RENEWAL & ESCALATION
4.1 Rent Escalation: Base rent increases by 3% annually on lease anniversary.
4.2 Renewal Option: Tenant has option to extend for 3 additional years with 120 days advance notice.
""", fontsize=11)

    p3 = doc3.new_page()
    p3.insert_text((50, 50), """5. DEFAULT & SURRENDER
5.1 Default Notice: 10 days written notice to cure monetary default.
5.2 Surrender Condition: Premises must be restored to original condition upon move-out.
""", fontsize=11)
    doc3.save(os.path.join(out_dir, "sample_rental_agreement.pdf"))
    doc3.close()

    # 4. Non-Disclosure Agreement (NDA)
    doc4 = fitz.open()
    p1 = doc4.new_page()
    p1.insert_text((50, 50), """MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("NDA") is made on January 20, 2026, by and between Nexus Cyber Security Inc. and Orion Data Labs LLC.

1. CONFIDENTIAL INFORMATION
1.1 Definition: All proprietary algorithms, customer lists, financial data, and technical specifications disclosed by either party.
1.2 Exclusions: Information publicly known or independently developed without reference to disclosed data.

2. OBLIGATIONS & CARE
2.1 Duty of Confidentiality: Recipient shall protect information using the same degree of care as its own proprietary data, but no less than reasonable care.
""", fontsize=11)

    p2 = doc4.new_page()
    p2.insert_text((50, 50), """3. DURATION & RETURN OF MATERIALS
3.1 Term of Confidentiality: Confidentiality obligations survive for three (3) years from date of disclosure.
3.2 Return or Destruction: Disclosing party may request written certification of destruction of all copies within 30 days.

4. GOVERNING LAW
4.1 Jurisdiction: Governed by New York law without regard to conflict of law principles.
""", fontsize=11)
    doc4.save(os.path.join(out_dir, "sample_nda.pdf"))
    doc4.close()

    print("All sample PDFs successfully generated!")

if __name__ == "__main__":
    generate_all_sample_pdfs()
