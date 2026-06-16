"""
Splices the reference-image-aware left panel into _showCoinInspectorDialog.
Replaces lines 1213..1293 (the old image panel Container) with new FutureBuilder version.
"""
import re

FILEPATH = r'c:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\my_collection_screen.dart'

with open(FILEPATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines are 1-indexed; Python list is 0-indexed
# Replace lines 1213..1293 inclusive (Python: 1212..1292)
START = 1212   # line 1213 (0-indexed)
END   = 1293   # line 1293 (0-indexed, exclusive end = 1293)

NEW_LINES = r"""                    // Left panel: image (300px)
                    Container(
                      width: 300,
                      decoration: const BoxDecoration(
                        color: Color(0xFFF8F9FB),
                        border: Border(right: BorderSide(color: _border)),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: _refFuture != null
                          // No user photo -- show reference image via FutureBuilder
                          ? FutureBuilder<CoinImageResult>(
                              future: _refFuture,
                              builder: (ctx2, snap) {
                                final ref       = snap.data;
                                final refObvUrl = ref?.obverseUrl ?? '';
                                final refRevUrl = ref?.reverseUrl ?? '';
                                final hasRefObv = refObvUrl.isNotEmpty;
                                final hasRefRev = refRevUrl.isNotEmpty;
                                final hasRef    = hasRefObv || hasRefRev;
                                final refUrl    = _vaultShowObverse
                                    ? (hasRefObv ? refObvUrl : refRevUrl)
                                    : (hasRefRev ? refRevUrl : refObvUrl);
                                final hasRefActive = refUrl.isNotEmpty;

                                return Column(children: [
                                  // Badge + toggle
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      if (hasRef) Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF1A237E).withAlpha(20),
                                          borderRadius: BorderRadius.circular(4),
                                          border: Border.all(color: const Color(0xFF1A237E), width: 1),
                                        ),
                                        child: const Row(mainAxisSize: MainAxisSize.min, children: [
                                          Icon(Icons.collections_outlined, size: 11, color: Color(0xFF1A237E)),
                                          SizedBox(width: 4),
                                          Text('REFERENCE', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF1A237E), letterSpacing: 0.8)),
                                        ]),
                                      ),
                                      if (hasRef) const SizedBox(width: 8),
                                      _vaultToggleButton('Obverse', showObv, hasRefObv, () {
                                        setState(() => _vaultShowObverse = true);
                                        setDlg(() {});
                                      }),
                                      const SizedBox(width: 8),
                                      _vaultToggleButton('Reverse', !showObv, hasRefRev, () {
                                        setState(() => _vaultShowObverse = false);
                                        setDlg(() {});
                                      }),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  // Image
                                  Expanded(
                                    child: GestureDetector(
                                      onTap: hasRefActive
                                          ? () => _showImageLightbox(refUrl,
                                                label: showObv ? 'Obverse' : 'Reverse',
                                                isMicroscope: false)
                                          : null,
                                      child: ClipRRect(
                                        borderRadius: BorderRadius.circular(8),
                                        child: hasRefActive
                                            ? Stack(fit: StackFit.expand, children: [
                                                Image.network(refUrl, fit: BoxFit.contain,
                                                  loadingBuilder: (_, child, prog) => prog == null
                                                      ? child
                                                      : const Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2)),
                                                  errorBuilder: (_, __, ___) => _vaultPlaceholder(
                                                      showObv ? 'Obverse' : 'Reverse', isError: true),
                                                ),
                                                Positioned(bottom: 8, right: 8,
                                                  child: Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                                    decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                                                    child: const Row(mainAxisSize: MainAxisSize.min, children: [
                                                      Icon(Icons.zoom_in, size: 12, color: Colors.white),
                                                      SizedBox(width: 3),
                                                      Text('Enlarge', style: TextStyle(fontSize: 10, color: Colors.white)),
                                                    ]),
                                                  ),
                                                ),
                                              ])
                                            : snap.connectionState == ConnectionState.waiting
                                                ? const Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2))
                                                : _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse'),
                                      ),
                                    ),
                                  ),
                                  // Attribution
                                  if (hasRef && ref!.attribution != null) ...[
                                    const SizedBox(height: 6),
                                    Text(ref.attribution!,
                                        style: const TextStyle(fontSize: 9, color: _subtext, fontStyle: FontStyle.italic),
                                        textAlign: TextAlign.center),
                                  ],
                                  const SizedBox(height: 12),
                                  // Upload buttons
                                  Row(children: [
                                    Expanded(child: _vaultUploadButton(
                                      label: '+ Add My Photo',
                                      icon: Icons.add_photo_alternate_outlined,
                                      progress: _uploadProgressObverse,
                                      onTap: () async {
                                        await _onUploadVaultImage(side: 'obverse', field: _F.imageObverse,
                                          setProgress: (p) { setState(() => _uploadProgressObverse = p); setDlg(() {}); });
                                      },
                                    )),
                                    const SizedBox(width: 8),
                                    Expanded(child: _vaultUploadButton(
                                      label: '+ Add Reverse',
                                      icon: Icons.add_photo_alternate_outlined,
                                      progress: _uploadProgressReverse,
                                      onTap: () async {
                                        await _onUploadVaultImage(side: 'reverse', field: _F.imageReverse,
                                          setProgress: (p) { setState(() => _uploadProgressReverse = p); setDlg(() {}); });
                                      },
                                    )),
                                  ]),
                                ]);
                              },
                            )
                          // User HAS their own photo -- show it directly
                          : Column(children: [
                              Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                _vaultToggleButton('Obverse', showObv, hasObv, () {
                                  setState(() => _vaultShowObverse = true);
                                  setDlg(() {});
                                }),
                                const SizedBox(width: 8),
                                _vaultToggleButton('Reverse', !showObv, hasRev, () {
                                  setState(() => _vaultShowObverse = false);
                                  setDlg(() {});
                                }),
                              ]),
                              const SizedBox(height: 12),
                              Expanded(
                                child: GestureDetector(
                                  onTap: hasActive ? () => _showImageLightbox(activeUrl,
                                      label: showObv ? 'Obverse' : 'Reverse',
                                      isMicroscope: data['scan_source'] == 'microscope') : null,
                                  child: ClipRRect(
                                    borderRadius: BorderRadius.circular(8),
                                    child: hasActive
                                        ? Stack(fit: StackFit.expand, children: [
                                            Image.network(activeUrl, fit: BoxFit.contain,
                                              loadingBuilder: (_, child, prog) => prog == null ? child
                                                  : const Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2)),
                                              errorBuilder: (_, err, __) {
                                                debugPrint('Image load error: $err  url: $activeUrl');
                                                return _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse', isError: true);
                                              },
                                            ),
                                            Positioned(bottom: 8, right: 8,
                                              child: Container(
                                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                                decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                                                child: const Row(mainAxisSize: MainAxisSize.min, children: [
                                                  Icon(Icons.zoom_in, size: 12, color: Colors.white),
                                                  SizedBox(width: 3),
                                                  Text('Enlarge', style: TextStyle(fontSize: 10, color: Colors.white)),
                                                ]),
                                              ),
                                            ),
                                          ])
                                        : _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse'),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 12),
                              Row(children: [
                                Expanded(child: _vaultUploadButton(
                                  label: hasObv ? 'Replace Obverse' : '+ Obverse',
                                  icon: hasObv ? Icons.refresh : Icons.add_photo_alternate_outlined,
                                  progress: _uploadProgressObverse,
                                  onTap: () async {
                                    await _onUploadVaultImage(side: 'obverse', field: _F.imageObverse,
                                      setProgress: (p) { setState(() => _uploadProgressObverse = p); setDlg(() {}); });
                                  },
                                )),
                                const SizedBox(width: 8),
                                Expanded(child: _vaultUploadButton(
                                  label: hasRev ? 'Replace Reverse' : '+ Reverse',
                                  icon: hasRev ? Icons.refresh : Icons.add_photo_alternate_outlined,
                                  progress: _uploadProgressReverse,
                                  onTap: () async {
                                    await _onUploadVaultImage(side: 'reverse', field: _F.imageReverse,
                                      setProgress: (p) { setState(() => _uploadProgressReverse = p); setDlg(() {}); });
                                  },
                                )),
                              ]),
                            ]),
                    ),
"""

new_line_list = [l + '\n' for l in NEW_LINES.split('\n')]
# Remove the trailing extra newline
if new_line_list and new_line_list[-1] == '\n':
    new_line_list = new_line_list[:-1]

result = lines[:START] + new_line_list + lines[END:]

with open(FILEPATH, 'w', encoding='utf-8') as f:
    f.writelines(result)

print(f"Done. Old lines {START+1}..{END}: {END-START} lines replaced with {len(new_line_list)} new lines.")
print(f"New total: {len(result)} lines")
