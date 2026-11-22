import 'package:flutter/material.dart';

/// Approved Morgan AI cartoon owl avatar (`assets/morgan_avatar.png`),
/// clipped cleanly in a circle with optional border ring.
class MorganOwlAvatar extends StatelessWidget {
  final double size;
  final double borderWidth;
  final Color? borderColor;

  const MorganOwlAvatar({
    super.key,
    this.size = 28.0,
    this.borderWidth = 0.0,
    this.borderColor,
  });

  @override
  Widget build(BuildContext context) {
    final innerSize = (size - (borderWidth * 2)).clamp(8.0, size);
    final avatar = ClipOval(
      child: Image.asset(
        'assets/morgan_avatar.png',
        width: innerSize,
        height: innerSize,
        fit: BoxFit.cover,
        gaplessPlayback: true,
        errorBuilder: (_, _, _) => Container(
          width: innerSize,
          height: innerSize,
          color: const Color(0xFF0F172A),
          child: Icon(
            Icons.smart_toy_outlined,
            size: innerSize * 0.58,
            color: const Color(0xFFFFD700),
          ),
        ),
      ),
    );

    if (borderWidth <= 0) return avatar;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: borderColor ?? const Color(0xFFC9A227),
          width: borderWidth,
        ),
      ),
      child: Center(child: avatar),
    );
  }
}
