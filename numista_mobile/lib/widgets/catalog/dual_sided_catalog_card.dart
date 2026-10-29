import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../services/catalog/catalog_service.dart';

/// Museum-Grade Dark Vault palette tokens (Plan.v2.1 §6.1).
class CatalogVaultPalette {
  static const Color obsidianBg = Color(0xFF0A0D12);
  static const Color slateSurface = Color(0xFF121721);
  static const Color elevatedWell = Color(0xFF1A2130);
  static const Color borderHairline = Color(0xFF263042);
  static const Color bullionGold = Color(0xFFD4AF37);
  static const Color verifyCyan = Color(0xFF38BDF8);
  static const Color banknoteGreen = Color(0xFF34D399);
  static const Color medalAmber = Color(0xFFFBBF24);
  static const Color foreignPurple = Color(0xFFA78BFA);
  static const Color textPrimary = Color(0xFFF3F6FA);
  static const Color textMuted = Color(0xFF8E9BAE);

  CatalogVaultPalette._();
}

/// Interactive Dual-Sided (Obverse / Reverse) catalog card with:
/// - Unique Identity Side Default (`defaultFace == 'REVERSE'` vs `'OBVERSE'`)
/// - 3D flip transition (individual card flip + global `flipAllReverse` override)
/// - Architectural blueprint `DualSidedPlaceholder` when images are pending
/// - Personal Specimen Photo vs Stock Catalog Image indicator (Founder Q3)
/// - Kind-routed `+ Add` button (`/coins`, `/currency`, `/world_items`)
class DualSidedCatalogCard extends StatefulWidget {
  final CatalogItemModel item;
  final bool isSelected;
  final bool flipAllReverse;
  final CollectionEntryState? collectionEntry;
  final VoidCallback onSelect;
  final VoidCallback onAddToCollection;
  final ValueChanged<bool>? onTogglePersonalPhoto;

  const DualSidedCatalogCard({
    super.key,
    required this.item,
    required this.isSelected,
    this.flipAllReverse = false,
    this.collectionEntry,
    required this.onSelect,
    required this.onAddToCollection,
    this.onTogglePersonalPhoto,
  });

  @override
  State<DualSidedCatalogCard> createState() => _DualSidedCatalogCardState();
}

class _DualSidedCatalogCardState extends State<DualSidedCatalogCard> {
  bool _manualFlip = false;

  /// Resolves which face ('OBVERSE' or 'REVERSE') is currently displayed.
  String get activeFace {
    final baseIsReverse = widget.item.defaultFace == 'REVERSE';
    final effectiveReverse = baseIsReverse ^ widget.flipAllReverse ^ _manualFlip;
    return effectiveReverse ? 'REVERSE' : 'OBVERSE';
  }

  Color _kindBadgeColor(String kind, String cc) {
    if (cc == 'FS') return CatalogVaultPalette.foreignPurple;
    switch (kind) {
      case 'BN':
        return CatalogVaultPalette.banknoteGreen;
      case 'MD':
      case 'TK':
        return CatalogVaultPalette.medalAmber;
      default:
        return CatalogVaultPalette.bullionGold;
    }
  }

  String _kindLabel(String kind, String cc, String denomClass) {
    if (cc == 'FS') return 'FOREIGN SPECIE (FS)';
    if (cc == 'CO') return 'COLONIAL / PRE-FED (CO)';
    if (cc == 'PF') return 'U.S. PHILIPPINES (PF)';
    switch (kind) {
      case 'BN':
        return 'BANK NOTE';
      case 'MD':
        return denomClass == 'PRV' ? 'PRIVATE MEDAL (PRV)' : 'MEDAL';
      default:
        return 'COIN';
    }
  }

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    final face = activeFace;
    final inCollection = widget.collectionEntry != null;
    final usePersonal = widget.collectionEntry?.usePersonalPhoto ?? false;
    final badgeColor = _kindBadgeColor(item.kind, item.cc);

    return GestureDetector(
      key: Key('catalog_card_${item.nacCode}'),
      onTap: widget.onSelect,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: CatalogVaultPalette.slateSurface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: widget.isSelected
                ? CatalogVaultPalette.bullionGold
                : CatalogVaultPalette.borderHairline,
            width: widget.isSelected ? 1.8 : 1.0,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top metadata row: Kind/Polity badge + Year/Facility pill
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0x26D4AF37),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: badgeColor, width: 0.8),
                    ),
                    child: Text(
                      _kindLabel(item.kind, item.cc, item.denominationClass),
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        color: badgeColor,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.6,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 6),
                Flexible(
                  child: Text(
                    item.yearDisplay,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    textAlign: TextAlign.right,
                    style: const TextStyle(
                      color: CatalogVaultPalette.textMuted,
                      fontSize: 11,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),

            // Dual-Sided Specimen Well (with Unique Identity Side indicator & Flip button)
            Expanded(
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: CatalogVaultPalette.elevatedWell,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: CatalogVaultPalette.borderHairline,
                    width: 0.8,
                  ),
                ),
                child: Stack(
                  children: [
                    Center(
                      child: AnimatedSwitcher(
                        duration: const Duration(milliseconds: 280),
                        transitionBuilder: (child, animation) {
                          final rotate = Tween<double>(
                            begin: math.pi / 2,
                            end: 0.0,
                          ).animate(animation);
                          return AnimatedBuilder(
                            animation: rotate,
                            child: child,
                            builder: (context, child) {
                              return Transform(
                                alignment: Alignment.center,
                                transform: Matrix4.rotationY(rotate.value),
                                child: child,
                              );
                            },
                          );
                        },
                        child: _DualSidedSpecimenBlueprint(
                          key: ValueKey('${item.nacCode}_${face}_$usePersonal'),
                          item: item,
                          activeFace: face,
                          usePersonalPhoto: usePersonal,
                        ),
                      ),
                    ),
                    // Top-left Unique Identity Side badge when defaultFace == REVERSE
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xCC0A0D12),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(
                            color: item.defaultFace == 'REVERSE'
                                ? CatalogVaultPalette.verifyCyan
                                : CatalogVaultPalette.borderHairline,
                            width: 0.8,
                          ),
                        ),
                        child: Text(
                          item.defaultFace == 'REVERSE'
                              ? '$face · Identity: Reverse'
                              : face,
                          key: Key('face_badge_${item.nacCode}'),
                          style: TextStyle(
                            color: item.defaultFace == 'REVERSE'
                                ? CatalogVaultPalette.verifyCyan
                                : CatalogVaultPalette.textMuted,
                            fontSize: 10,
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                    // Top-right Flip button
                    Positioned(
                      top: 6,
                      right: 6,
                      child: InkWell(
                        key: Key('flip_btn_${item.nacCode}'),
                        onTap: () {
                          setState(() {
                            _manualFlip = !_manualFlip;
                          });
                        },
                        borderRadius: BorderRadius.circular(6),
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 7,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: const Color(0xCC0A0D12),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: CatalogVaultPalette.borderHairline,
                            ),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.flip_camera_android,
                                size: 12,
                                color: CatalogVaultPalette.bullionGold,
                              ),
                              SizedBox(width: 4),
                              Text(
                                'Flip',
                                style: TextStyle(
                                  color: CatalogVaultPalette.textPrimary,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),

            // Title & Subtitle
            Text(
              item.title,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: CatalogVaultPalette.textPrimary,
                fontSize: 14,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              item.subtitle,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: CatalogVaultPalette.textMuted,
                fontSize: 11,
              ),
            ),
            const SizedBox(height: 8),

            // Bottom bar: NAC1 code + Kind-routed Add / Personal Photo Toggle
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    item.nacCode,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: CatalogVaultPalette.verifyCyan,
                      fontSize: 9.5,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
                const SizedBox(width: 4),
                if (inCollection && widget.onTogglePersonalPhoto != null)
                  Padding(
                    padding: const EdgeInsets.only(right: 4),
                    child: InkWell(
                      key: Key('photo_toggle_btn_${item.nacCode}'),
                      onTap: () => widget.onTogglePersonalPhoto!(!usePersonal),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 5,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(5),
                          border: Border.all(
                            color: usePersonal
                                ? CatalogVaultPalette.verifyCyan
                                : CatalogVaultPalette.borderHairline,
                          ),
                        ),
                        child: Text(
                          usePersonal ? 'My Photo' : 'Stock',
                          style: const TextStyle(
                            color: CatalogVaultPalette.textPrimary,
                            fontSize: 9,
                          ),
                        ),
                      ),
                    ),
                  ),
                Flexible(
                  fit: FlexFit.loose,
                  child: InkWell(
                    key: Key('add_btn_${item.nacCode}'),
                    onTap: widget.onAddToCollection,
                    borderRadius: BorderRadius.circular(6),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 7,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: inCollection
                            ? const Color(0x3334D399)
                            : const Color(0x26D4AF37),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(
                          color: inCollection
                              ? CatalogVaultPalette.banknoteGreen
                              : CatalogVaultPalette.bullionGold,
                        ),
                      ),
                      child: Text(
                        inCollection
                            ? '✓ /${item.targetCollection}'
                            : '+ /${item.targetCollection}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: inCollection
                              ? CatalogVaultPalette.banknoteGreen
                              : CatalogVaultPalette.bullionGold,
                          fontSize: 9.5,
                          fontFamily: 'monospace',
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _DualSidedSpecimenBlueprint extends StatelessWidget {
  final CatalogItemModel item;
  final String activeFace;
  final bool usePersonalPhoto;

  const _DualSidedSpecimenBlueprint({
    super.key,
    required this.item,
    required this.activeFace,
    required this.usePersonalPhoto,
  });

  @override
  Widget build(BuildContext context) {
    final isNote = item.specifications.alignment == 'NOTE';
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: isNote ? 128 : 76,
          height: isNote ? 60 : 76,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            shape: isNote ? BoxShape.rectangle : BoxShape.circle,
            borderRadius: isNote ? BorderRadius.circular(6) : null,
            border: Border.all(
              color: CatalogVaultPalette.bullionGold,
              width: 1.4,
            ),
            gradient: const RadialGradient(
              colors: [Color(0xFF242E42), Color(0xFF111622)],
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                item.denominationClass,
                style: const TextStyle(
                  color: CatalogVaultPalette.bullionGold,
                  fontSize: 13,
                  fontWeight: FontWeight.w800,
                  fontFamily: 'monospace',
                ),
              ),
              Text(
                activeFace == 'REVERSE' ? 'REV DIE' : 'OBV DIE',
                style: const TextStyle(
                  color: CatalogVaultPalette.textMuted,
                  fontSize: 9,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 6),
        Text(
          usePersonalPhoto
              ? 'Personal Specimen Photo Active'
              : (item.imageSourceCredit ??
                    'Blueprint · Contribute Photo (+25 pts)'),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(
            color: CatalogVaultPalette.textMuted,
            fontSize: 9,
          ),
        ),
      ],
    );
  }
}
