import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../models/coin_model.dart';
import '../../models/program_model.dart';

/// A widget that resolves the best available image for a coin based on a 3-tier hierarchy:
/// 1. User Capture (imageUrlObverse)
/// 2. Official Reference (referenceImagePath from GCS)
/// 3. Local Fallback (assets/kaggle/ or generic placeholder)
class RefImageWidget extends StatelessWidget {
  final CoinModel? userCoin;
  final ProgramCoin? programCoin;
  final ChecklistVariety? variety;
  final double? width;
  final double? height;
  final BoxShape shape;
  final BoxFit fit;

  const RefImageWidget({
    super.key,
    this.userCoin,
    this.programCoin,
    this.variety,
    this.width,
    this.height,
    this.shape = BoxShape.rectangle,
    this.fit = BoxFit.cover,
  });

  @override
  Widget build(BuildContext context) {
    // Tier 1: User Capture
    if (userCoin != null && userCoin!.imageUrlObverse.isNotEmpty) {
      return _buildImage(userCoin!.imageUrlObverse, isNetwork: true);
    }

    // Tier 2: Variety-specific Reference
    if (variety != null && variety!.referenceImagePath != null) {
      return _buildGCSImage(variety!.referenceImagePath!);
    }

    // Tier 2.5: Program-level Reference
    if (programCoin != null && programCoin!.referenceImagePath != null) {
      return _buildGCSImage(programCoin!.referenceImagePath!);
    }

    // Tier 3: Local Kaggle/Platform Fallback
    return _buildPlaceholder();
  }

  Widget _buildGCSImage(String path) {
    // Assuming a standard base URL for the GCS bucket or Firebase Storage
    // In a real implementation, this would use FirebaseStorage.instance.ref(path).getDownloadURL()
    // For now, we construct a placeholder URL or use the path directly if it's a full URL
    final fullUrl = path.startsWith('http') 
      ? path 
      : 'https://storage.googleapis.com/us_mint_coin_images/$path';

    return _buildImage(fullUrl, isNetwork: true);
  }

  Widget _buildImage(String source, {required bool isNetwork}) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        shape: shape,
        borderRadius: shape == BoxShape.circle ? null : BorderRadius.circular(12),
        color: const Color(0xFFF1F5F9),
      ),
      clipBehavior: Clip.antiAlias,
      child: isNetwork
          ? CachedNetworkImage(
              imageUrl: source,
              fit: fit,
              placeholder: (context, url) => const Center(
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
              errorWidget: (context, url, error) => _buildPlaceholder(),
            )
          : Image.asset(source, fit: fit),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: const Color(0xFFE2E8F0),
        shape: shape,
        borderRadius: shape == BoxShape.circle ? null : BorderRadius.circular(12),
      ),
      child: Center(
        child: Icon(
          Icons.copyright, // Using copyright as a subtle nod to "Reference"
          size: (width ?? 40) * 0.5,
          color: const Color(0xFF94A3B8),
        ),
      ),
    );
  }
}
