/// "Mark Sold, never delete" (R3, PLAN v1.2): a sold item keeps its doc with status == "sold".
/// Sold is keyed on `status`, never `transferStatus` (which moves to "pending" during a buyer transfer).
bool isSoldItem(Map<String, dynamic> data) => data['status']?.toString() == 'sold';

/// Free-tier overflow lock set by the server after a claim or a downgrade.
bool isLockedItem(Map<String, dynamic> data) => data['locked_pending_upgrade'] == true;
