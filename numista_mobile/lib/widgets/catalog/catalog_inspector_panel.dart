import 'package:flutter/material.dart';
import '../../services/catalog/catalog_service.dart';
import '../../services/catalog/nac_code_parser.dart';
import 'dual_sided_catalog_card.dart';

/// Sticky 4-column Right Inspector Panel for the U.S. Numismatics Master Catalog.
///
/// Displays:
/// - Full NAC1 9-segment breakdown & live Crockford-32 check digit verification
/// - Facility (`FAC`) vs physical mint mark (`mint_mark_on_coin`) distinction
/// - Official U.S. Mint (`mintageOfficialMint`) vs Commercial (`mintageCommercial`) figures
/// - Metrology specifications & primary Tier-A / Tier-B citations
/// - Kind-routed collection write contract + Founder Q3 Photo Toggle + Founder Q4 Guest Download Guard
class CatalogInspectorPanel extends StatelessWidget {
  final CatalogItemModel item;
  final bool isAuthenticated;
  final CollectionEntryState? collectionEntry;
  final VoidCallback onAddToCollection;
  final ValueChanged<bool>? onTogglePersonalPhoto;
  final VoidCallback? onRequestImageDownload;

  const CatalogInspectorPanel({
    super.key,
    required this.item,
    this.isAuthenticated = false,
    this.collectionEntry,
    required this.onAddToCollection,
    this.onTogglePersonalPhoto,
    this.onRequestImageDownload,
  });

  @override
  Widget build(BuildContext context) {
    final parsed = NacCodeParser.parseNac1(item.nacCode);
    final isChecksumValid = NacCodeParser.validateNac1(item.nacCode);
    final inCollection = collectionEntry != null;
    final usePersonal = collectionEntry?.usePersonalPhoto ?? false;

    return Container(
      key: const Key('catalog_inspector_panel'),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CatalogVaultPalette.slateSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: CatalogVaultPalette.borderHairline),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header badge
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'SPECIMEN INSPECTOR',
                  style: TextStyle(
                    color: CatalogVaultPalette.bullionGold,
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.1,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0x1F38BDF8),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: CatalogVaultPalette.verifyCyan),
                  ),
                  child: Text(
                    isChecksumValid
                        ? '✓ NAC1 CHK: ${parsed.chk}'
                        : 'INVALID CHK',
                    key: const Key('inspector_checksum_badge'),
                    style: const TextStyle(
                      color: CatalogVaultPalette.verifyCyan,
                      fontSize: 10,
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),

            Text(
              item.title,
              key: const Key('inspector_title'),
              style: const TextStyle(
                color: CatalogVaultPalette.textPrimary,
                fontSize: 17,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              item.subtitle,
              style: const TextStyle(
                color: CatalogVaultPalette.textMuted,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 10),

            // Canonical NAC1 Code Box
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: CatalogVaultPalette.obsidianBg,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: CatalogVaultPalette.borderHairline),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'CANONICAL NAC1 IDENTIFIER',
                    style: TextStyle(
                      color: CatalogVaultPalette.textMuted,
                      fontSize: 9,
                      letterSpacing: 0.8,
                    ),
                  ),
                  const SizedBox(height: 4),
                  SelectableText(
                    item.nacCode,
                    key: const Key('inspector_nac_code'),
                    style: const TextStyle(
                      color: CatalogVaultPalette.verifyCyan,
                      fontSize: 12,
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'KIND=${parsed.kind} · CC=${parsed.cc} · CLASS=${parsed.denominationClass} · FAC=${parsed.facilityCode} · VAR=${parsed.variety}',
                    style: const TextStyle(
                      color: CatalogVaultPalette.textMuted,
                      fontSize: 10,
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Collection Write Contract + Founder Q3 Photo Toggle + Founder Q4 Download Guard
            _InspectorSectionTitle('COLLECTION ROUTING & PHOTO POLICY'),
            Text(
              'Target Path: users/{uid}/${item.targetCollection}/${item.deterministicDocId}',
              key: const Key('inspector_target_path'),
              style: const TextStyle(
                color: CatalogVaultPalette.verifyCyan,
                fontSize: 11,
                fontFamily: 'monospace',
              ),
            ),
            const SizedBox(height: 10),

            if (inCollection && onTogglePersonalPhoto != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: SwitchListTile(
                  key: const Key('inspector_personal_photo_switch'),
                  contentPadding: EdgeInsets.zero,
                  dense: true,
                  title: const Text(
                    'Use My Specimen Photo (Keep Stock Backup)',
                    style: TextStyle(
                      color: CatalogVaultPalette.textPrimary,
                      fontSize: 12,
                    ),
                  ),
                  value: usePersonal,
                  onChanged: onTogglePersonalPhoto,
                ),
              ),

            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    key: const Key('inspector_add_button'),
                    onPressed: onAddToCollection,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: CatalogVaultPalette.bullionGold,
                      foregroundColor: CatalogVaultPalette.obsidianBg,
                    ),
                    child: Text(
                      inCollection
                          ? 'In /${item.targetCollection} (Idempotent)'
                          : 'Add to /${item.targetCollection}',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                OutlinedButton(
                  key: const Key('inspector_download_image_button'),
                  onPressed: onRequestImageDownload,
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(
                      color: CatalogVaultPalette.borderHairline,
                    ),
                  ),
                  child: Text(
                    isAuthenticated ? 'Download Hi-Res' : 'Download (Sign In)',
                    style: const TextStyle(
                      color: CatalogVaultPalette.textMuted,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Facility vs Physical Mint Mark section
            _InspectorSectionTitle('PRODUCTION FACILITY & MINT MARK'),
            _InspectorKeyValue(
              'Facility Code (FAC)',
              item.facilityCode,
            ),
            _InspectorKeyValue(
              'Mint Mark on Specimen',
              item.mintMarkOnCoin
                  ? 'Yes ("${item.mintMark}")'
                  : 'No Mint Mark on Specimen',
            ),
            if (item.facilityNote != null)
              _InspectorKeyValue('Facility Note', item.facilityNote!),
            const SizedBox(height: 12),

            // Mintage & Provenance section
            _InspectorSectionTitle('MINTAGE & PROVENANCE'),
            _InspectorKeyValue(
              'Official Gov Mintage (Tier A)',
              item.mintageOfficialMint?.toString() ?? 'N/A (Pre-Federal / Private)',
            ),
            _InspectorKeyValue(
              'Commercial Estimate (Tier B)',
              item.mintageCommercial != null
                  ? '${item.mintageCommercial}${item.mintageEstimated ? " (Est.)" : ""}'
                  : 'Unrecorded',
            ),
            if (item.mintageReconciliationNote != null)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  item.mintageReconciliationNote!,
                  style: const TextStyle(
                    color: CatalogVaultPalette.textMuted,
                    fontSize: 11,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            const SizedBox(height: 12),

            // Specifications section
            _InspectorSectionTitle('METROLOGY & SPECIFICATIONS'),
            _InspectorKeyValue('Composition', item.specifications.composition),
            _InspectorKeyValue(
              'Precious Metal',
              item.specifications.preciousMetalType,
            ),
            if (item.specifications.weightGrams != null)
              _InspectorKeyValue(
                'Weight (g)',
                '${item.specifications.weightGrams} g',
              ),
            if (item.specifications.diameterMm != null)
              _InspectorKeyValue(
                item.specifications.alignment == 'NOTE'
                    ? 'Dimensions (mm)'
                    : 'Diameter (mm)',
                item.specifications.heightMm != null
                    ? '${item.specifications.diameterMm} × ${item.specifications.heightMm} mm'
                    : '${item.specifications.diameterMm} mm',
              ),
            _InspectorKeyValue(
              'Default Display Face',
              item.defaultFace == 'REVERSE'
                  ? 'REVERSE (Unique Identity Side)'
                  : 'OBVERSE',
            ),
            const SizedBox(height: 12),

            // Citations
            _InspectorSectionTitle('PRIMARY CITATIONS'),
            ...item.primaryCitations.map(
              (c) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Text(
                  '[${c.tier}] ${c.sourceName} — ${c.citationText}',
                  style: const TextStyle(
                    color: CatalogVaultPalette.textMuted,
                    fontSize: 11,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InspectorSectionTitle extends StatelessWidget {
  final String title;
  const _InspectorSectionTitle(this.title);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Text(
        title,
        style: const TextStyle(
          color: CatalogVaultPalette.bullionGold,
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.9,
        ),
      ),
    );
  }
}

class _InspectorKeyValue extends StatelessWidget {
  final String label;
  final String value;

  const _InspectorKeyValue(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 5,
            child: Text(
              label,
              style: const TextStyle(
                color: CatalogVaultPalette.textMuted,
                fontSize: 11,
              ),
            ),
          ),
          Expanded(
            flex: 6,
            child: Text(
              value,
              style: const TextStyle(
                color: CatalogVaultPalette.textPrimary,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
