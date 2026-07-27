import 'package:flutter/material.dart';
import '../services/family_subaccount_service.dart';

class FamilySettingsScreen extends StatefulWidget {
  final String parentEmail;
  final String userTier;

  const FamilySettingsScreen({
    Key? key,
    required this.parentEmail,
    this.userTier = 'Pro',
  }) : super(key: key);

  @override
  State<FamilySettingsScreen> createState() => _FamilySettingsScreenState();

}

class _FamilySettingsScreenState extends State<FamilySettingsScreen> {
  final FamilySubaccountService _service = FamilySubaccountService();
  List<SubAccountModel> _subAccounts = [];
  bool _isLoading = true;

  final TextEditingController _aliasController = TextEditingController();
  final TextEditingController _relationshipController = TextEditingController();
  String _permissionLevel = 'VIEW_ONLY';
  double _bequestShare = 25.0;

  @override
  void initState() {
    super.initState();
    _loadSubAccounts();
  }

  Future<void> _loadSubAccounts() async {
    setState(() => _isLoading = true);
    final list = await _service.fetchSubAccounts(widget.parentEmail);
    setState(() {
      _subAccounts = list;
      _isLoading = false;
    });
  }

  Future<void> _createSubAccount() async {
    if (_aliasController.text.trim().isEmpty) return;

    try {
      await _service.createSubAccount(
        parentEmail: widget.parentEmail,
        childAlias: _aliasController.text.trim(),
        relationship: _relationshipController.text.trim().isEmpty
            ? 'Heir'
            : _relationshipController.text.trim(),
        permissionLevel: _permissionLevel,
        bequestPercentage: _bequestShare,
        userTier: widget.userTier,
      );
      _aliasController.clear();
      _relationshipController.clear();
      Navigator.of(context).pop();
      _loadSubAccounts();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}'), backgroundColor: Colors.red),
      );
    }
  }

  void _showAddModal() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Family Sub-Account'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _aliasController,
                decoration: const InputDecoration(labelText: 'Name / Alias (e.g. "Nat")'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _relationshipController,
                decoration: const InputDecoration(labelText: 'Relationship (e.g. "Daughter", "Trustee")'),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _permissionLevel,
                decoration: const InputDecoration(labelText: 'Permission Level'),
                items: const [
                  DropdownMenuItem(value: 'VIEW_ONLY', child: Text('View Only (Read-Only Access)')),
                  DropdownMenuItem(value: 'CONTRIBUTOR', child: Text('Contributor (Can Add Notes)')),
                  DropdownMenuItem(value: 'FULL_ACCESS', child: Text('Full Access (Manage Collection)')),
                ],
                onChanged: (val) {
                  if (val != null) setState(() => _permissionLevel = val);
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: _createSubAccount,
            child: const Text('Create Sub-Account'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final maxLimitText = widget.userTier.toLowerCase() == 'estate'
        ? 'Unlimited Sub-Accounts (Estate Tier)'
        : 'Up to 5 Sub-Accounts (Pro Tier)';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Family & Custodian Accounts'),
        backgroundColor: const Color(0xFF1E3A8A),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              color: Colors.blue.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    const Icon(Icons.family_restroom, size: 36, color: Color(0xFF1E3A8A)),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Family Vault & Custodian Access',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          const SizedBox(height: 4),
                          Text(maxLimitText, style: TextStyle(color: Colors.grey.shade700)),
                        ],
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: _showAddModal,
                      icon: const Icon(Icons.add),
                      label: const Text('Add Member'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Active Sub-Accounts',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _subAccounts.isEmpty
                      ? const Center(
                          child: Text(
                            'No sub-accounts created yet. Click "Add Member" above to invite family.',
                            style: TextStyle(color: Colors.grey),
                          ),
                        )
                      : ListView.builder(
                          itemCount: _subAccounts.length,
                          itemBuilder: (ctx, idx) {
                            final item = _subAccounts[idx];
                            return Card(
                              child: ListTile(
                                leading: const CircleAvatar(
                                  backgroundColor: Color(0xFF1E3A8A),
                                  child: Icon(Icons.person, color: Colors.white),
                                ),
                                title: Text(
                                  '${item.childAlias} (${item.relationship})',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: Text(
                                  'Permission: ${item.permissionLevel} | Bequest Share: ${item.bequestPercentage.toStringAsFixed(0)}%',
                                ),
                                trailing: IconButton(
                                  icon: const Icon(Icons.delete, color: Colors.red),
                                  onPressed: () async {
                                    await _service.deleteSubAccount(item.childId, widget.parentEmail);
                                    _loadSubAccounts();
                                  },
                                ),
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }
}
