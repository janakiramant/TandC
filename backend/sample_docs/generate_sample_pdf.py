import os
import fitz  # PyMuPDF

def generate_sample_pdf(output_path: str):
    doc = fitz.open()

    # Page 1: Overview, Definitions, Obligations
    page1 = doc.new_page()
    p1_text = """MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is entered into as of January 15, 2026, by and between Alpha Legal Tech Inc. ("Client") and Apex Consulting Services LLC ("Provider").

1. SCOPE OF SERVICES & OBLIGATIONS
1.1 Services. Provider shall perform software design, legal analysis integration, and security auditing services as described in Statement of Work #1.
1.2 Standard of Performance. Provider agrees to execute all duties with high commercial standards of skill and diligence.
1.3 Client Obligations. Client agrees to provide timely access to necessary documentation, test data, and technical contact personnel.

2. PAYMENT & FINANCIAL TERMS
2.1 Service Fees. Client agrees to pay Provider a fixed fee of $15,000 per month for the duration of the engagement.
2.2 Invoicing and Due Date. Invoices shall be issued on the 1st day of each month and are due within thirty (30) days of invoice date.
2.3 Late Payment Penalty. Any invoice unpaid after thirty (30) days shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by applicable law.
"""
    page1.insert_text((50, 50), p1_text, fontsize=11)

    # Page 2: Confidentiality, IP, Concerns/Risks (Automatic Renewal & Notice Period)
    page2 = doc.new_page()
    p2_text = """3. CONFIDENTIALITY & INTELLECTUAL PROPERTY
3.1 Proprietary Information. Each party agrees to hold in strict confidence all technical, business, and legal information disclosed by the other party.
3.2 IP Ownership. All work product, software code, custom analytical models, and deliverables created by Provider specifically for Client under this Agreement shall belong exclusively to Client.
3.3 License Grant. Provider grants Client a perpetual, royalty-free, worldwide license to use pre-existing tools integrated into deliverables.

4. TERM & AUTOMATIC RENEWAL (ATTENTION REQUIRED)
4.1 Initial Term. This Agreement commences on the Effective Date and continues for an initial period of twelve (12) months.
4.2 Automatic Renewal. Upon expiration of the Initial Term, this Agreement shall automatically renew for successive twelve (12) month terms unless either party provides written notice of non-renewal.
4.3 Notice Period for Non-Renewal. To prevent automatic renewal, written notice of termination must be delivered at least ninety (90) days prior to the expiration of the current term.
"""
    page2.insert_text((50, 50), p2_text, fontsize=11)

    # Page 3: Termination, Indemnification, Governing Law
    page3 = doc.new_page()
    p3_text = """5. TERMINATION & REMEDIES
5.1 Termination for Cause. Either party may terminate this Agreement immediately upon written notice if the other party materially breaches any provision and fails to cure such breach within fifteen (15) days.
5.2 Early Termination Penalty. If Client terminates this Agreement prior to the end of the Initial Term without cause, Client shall pay an early termination fee equal to fifty percent (50%) of the remaining monthly fees for the remainder of the Initial Term.

6. INDEMNIFICATION & GOVERNING LAW
6.1 Mutual Indemnification. Each party shall defend, indemnify, and hold harmless the other party against third-party claims arising from gross negligence or willful misconduct.
6.2 Governing Law & Jurisdiction. This Agreement shall be governed by, and construed in accordance with, the laws of the State of Delaware, without regard to its conflict of law principles. Any dispute arising hereunder shall be subject to exclusive jurisdiction in Wilmington, Delaware.

IN WITNESS WHEREOF, the parties hereto have executed this Master Services Agreement.
"""
    page3.insert_text((50, 50), p3_text, fontsize=11)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()
    print(f"Sample PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "sample_service_agreement.pdf")
    generate_sample_pdf(out)
