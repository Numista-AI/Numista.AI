# Numista.AI — Estate Planning & Lot Division Logic Specification

> **Version:** August 2026 | **Author:** Numista Estate & Legal Engineering | **Status:** Active Production Specification

---

## 1. Overview

The Numista.AI Estate Division Engine (`estate_planning_screen.dart` & `attorney_portal_screen.dart`) enables collectors, executors, and estate attorneys to partition numismatic inventories among $N$ heirs with mathematical precision, transparent audit trails, and legal accountability.

---

## 2. Partitioning Algorithm: Longest Processing Time (LPT) Greedy Solver

The lot division engine utilizes a modified **Longest Processing Time (LPT)** greedy bin-packing solver:

1. **Valuation Matrix Assembly**:
   - Total inventory value $V_{total} = \sum v(c_i)$ for all un-locked coins.
   - Target lot value per heir $k$: $T_k = V_{total} 	imes P_k$, where $P_k$ is the target percentage allocation (e.g., Heir A = 50%, Heir B = 50%).

2. **Sorting & Allocation Loop**:
   - Sort all un-locked items in descending order of calculated market value: $v(c_1) \ge v(c_2) \ge \dots \ge v(c_m)$.
   - For each coin $c_i$, assign it to the heir whose current accumulated lot value is furthest below their target $T_k$.

3. **Lock Pre-Assignment Precedence**:
   - Coins marked with `heir_lock: "Heir Name"` are pre-allocated to that beneficiary *before* the LPT algorithm executes.
   - Pre-allocated item values count toward that beneficiary's accumulated lot total before distributing remaining un-locked items.

---

## 3. Cash Offset Compensation Logic

When physical coin values cannot be divided evenly to exact dollar amounts, the engine calculates monetary cash equalization offsets:

$$	ext{Cash Offset}_k = 	ext{Target Value}_k - 	ext{Allocated Coin Value}_k$$

- **Positive Offset**: Beneficiary received less physical coin value than their target split; they receive a cash payout from the estate.
- **Negative Offset**: Beneficiary received higher-value physical coins than their target split; they owe a cash balancing payment into the estate pool.
- Net cash sum across all heirs equals zero: $\sum 	ext{Cash Offset}_k = 0$.

---

## 4. Valuation Floor Hierarchy Defaults

For tax assessment, probate accounting, and estate distributions, the engine supports 4 configurable valuation tiers:

1. **Greysheet CPG Wholesale (Default for Estate Partition)**: Standard dealer buy/wholesale valuation baseline.
2. **Greysheet Retail**: Fair market retail valuation baseline for estate sale planning.
3. **Precious Metal Melt Floor**: Liquidation floor based on live spot metal prices (Gold, Silver, Platinum).
4. **Tax Cost Basis (Stepped-Up Basis)**: Historical purchase cost or date-of-death valuation basis for IRS Form 706 reporting.

---

## 5. Numismatic Passport Export Specification

The ReportLab engine (`passport_pdf_generator.py`) serializes the approved division into a legal-grade PDF containing:
- Certificate of Executor Verification & Timestamp
- Detailed Heir Distribution Schedules with High-Res Image Proofs
- Cash Equalization Summary Table
- Attorney Read-Only Portal Audit Signature Block
