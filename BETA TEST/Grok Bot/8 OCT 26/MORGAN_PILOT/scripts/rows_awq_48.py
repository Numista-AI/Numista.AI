# Claims and queries for the 48 AWQ rows (built from EVIDENCE_PACK_2026-10-06_AWQ_SOURCED.csv slot ids).
H = [('maya_angelou',2022,'Maya Angelou'),('dr_sally_ride',2022,'Dr. Sally Ride'),('wilma_mankiller',2022,'Wilma Mankiller'),
     ('nina_otero_warren',2022,'Nina Otero-Warren'),('anna_may_wong',2022,'Anna May Wong'),
     ('bessie_coleman',2023,'Bessie Coleman'),('edith_kanaka_ole',2023,'Edith Kanakaʻole'),('eleanor_roosevelt',2023,'Eleanor Roosevelt'),
     ('jovita_idar',2023,'Jovita Idar'),('maria_tallchief',2023,'Maria Tallchief'),
     ('dr_pauli_murray',2024,'Rev. Dr. Pauli Murray'),('patsy_mink',2024,'Patsy Takemoto Mink'),('dr_mary_edwards_walker',2024,'Dr. Mary Edwards Walker'),
     ('celia_cruz',2024,'Celia Cruz'),('zitkala_a',2024,'Zitkala-Ša'),
     ('ida_b_wells',2025,'Ida B. Wells'),('juliette_gordon_low',2025,'Juliette Gordon Low'),('dr_vera_rubin',2025,'Dr. Vera Rubin'),
     ('stacey_milbern',2025,'Stacey Park Milbern'),('althea_gibson',2025,'Althea Gibson')]
ROWS = []
for i, (slug, y, n) in enumerate(H):
    ROWS.append(dict(row=2*i+1, slot=f'american_women_quarters_{slug}_{y}#W-UNC', ours='REMOVE the West Point (W) uncirculated slot',
        claim=f'The {y} {n} quarter was minted at Philadelphia (P), Denver (D) and San Francisco (S).',
        opposite=f'The {y} {n} quarter was struck at the West Point Mint with a W mint mark.',
        queries=[f'{y} {n} quarter rolls and bags mint and mint mark Philadelphia Denver San Francisco',
                 f'{y} {n} quarter West Point W mint mark']))
    ROWS.append(dict(row=2*i+2, slot=f'NEW:american_women_quarters_{slug}_{y}#S-SILVER-PROOF', ours='ADD S Silver Proof (99.9% silver) slot',
        claim=f'The {y} American Women Quarters Silver Proof Set includes the {n} quarter. The quarters in the {y} American Women Quarters Silver Proof Set are 99.9 percent silver. The {y} American Women Quarters Silver Proof Set is struck at the San Francisco Mint (S).',
        opposite=None,
        queries=[f'{y} American Women Quarters Silver Proof Set {n} 99.9 percent silver San Francisco',
                 f'{y} {n} quarter silver proof',
                 f'{y} American Women Quarters Silver Proof Set specifications mint and mint mark San Francisco - S']))
ROWS += [
 dict(row=41, slot='ALL 20 slots#S (label)', ours='label "S Uncirculated"',
      claim='American Women Quarters with uncirculated finishes were minted at San Francisco (S). American Women Quarters are sold in 3-roll sets containing P, D and S coins.',
      opposite=None, queries=['American Women Quarters rolls uncirculated finishes San Francisco 3-Roll Set P D S']),
 dict(row=42, slot='ALL 20 slots#S-PROOF (label)', ours='label "S Proof (clad)"',
      claim='The American Women Quarters Proof Set contains proof quarters struck at San Francisco (S). The proof quarters in the American Women Quarters Proof Set have a composition of 8.33% nickel and the balance copper.',
      opposite=None, queries=['American Women Quarters Proof Set proof quarters composition nickel copper San Francisco']),
 dict(row=43, slot='american_women_quarters_stacey_milbern_2025#name', ours='Stacey Park Milbern',
      claim='The 2025 American Women Quarter honors Stacey Park Milbern. The coin is inscribed STACEY PARK MILBERN.',
      opposite=None, queries=['Stacey Park Milbern quarter inscriptions']),
 dict(row=44, slot='american_women_quarters_dr_pauli_murray_2024#name', ours='Rev. Dr. Pauli Murray (THE REVEREND DR. PAULI MURRAY)',
      claim='The 2024 American Women Quarter honors the Reverend Dr. Pauli Murray. The coin is inscribed THE REVEREND DR. PAULI MURRAY.',
      opposite=None, queries=['Reverend Dr. Pauli Murray quarter inscriptions']),
 dict(row=45, slot='american_women_quarters_patsy_mink_2024#name', ours='Patsy Takemoto Mink',
      claim='The 2024 American Women Quarter honors Patsy Takemoto Mink. The coin is inscribed PATSY TAKEMOTO MINK.',
      opposite=None, queries=['Patsy Takemoto Mink quarter inscriptions']),
 dict(row=46, slot='american_women_quarters_edith_kanaka_ole_2023#name', ours='Edith Kanakaʻole (with ʻokina)',
      claim='The 2023 American Women Quarter honors Edith Kanakaʻole. The coin is inscribed EDITH KANAKAʻOLE.',
      opposite=None, queries=['Edith Kanakaʻole quarter inscriptions']),
 dict(row=47, slot='american_women_quarters_zitkala_a_2024#program_slot_id', ours='slug zitkala_sa (name Zitkala-Ša)',
      claim='The 2024 American Women Quarter honors Zitkala-Ša. The coin is inscribed ZITKALA-ŠA.',
      opposite=None, queries=['Zitkala-Ša quarter inscriptions']),
 dict(row=48, slot='program#total_slots', ours='100 slots (20 honorees x P, D, S, S Proof, S Silver Proof)',
      claim='The American Women Quarters Program ran from 2022 through 2025 with five new reverse designs each year. Each American Women Quarter design was minted at Philadelphia (P), Denver (D) and San Francisco (S). American Women Quarters were issued in San Francisco (S) proof sets. American Women Quarters were issued in San Francisco (S) 99.9 percent silver proof sets.',
      opposite=None, queries=['American Women Quarters Program 2022 through 2025 five designs each year honorees',
                              'American Women Quarters 3-Roll Set P D S San Francisco',
                              'American Women Quarters Proof Set mint and mint mark San Francisco (S)',
                              'American Women Quarters Silver Proof Set 99.9 percent silver mint and mint mark San Francisco - S'])]
ROWS.sort(key=lambda r: r['row'])
assert [r['row'] for r in ROWS] == list(range(1, 49))
