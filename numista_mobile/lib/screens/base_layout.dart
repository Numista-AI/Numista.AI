import 'package:flutter/material.dart';
import 'home_dashboard.dart';
import 'my_collection_screen.dart';

class BaseLayout extends StatefulWidget {
  const BaseLayout({super.key});

  @override
  State<BaseLayout> createState() => _BaseLayoutState();
}

class _BaseLayoutState extends State<BaseLayout> {
  String _activeRoute = 'Home Dashboard';

  Widget _buildBody() {
    switch (_activeRoute) {
      case 'Home Dashboard':
        return const HomeDashboard();
      case 'My Collection':
        return const MyCollectionScreen();
      default:
        return const Center(child: Text('Under Construction'));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F6), // Streamlit light background
      body: Row(
        children: [
          // Sidebar
          Container(
            width: 260,
            color: const Color(0xFF0E1117), // Streamlit dark navy sidebar
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 32),
                // Logo Section
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  child: Image.asset(
                    'assets/logo_owl.png',
                    height: 140,
                    fit: BoxFit.contain,
                  ),
                ),
                const SizedBox(height: 24),
                
                // Vault indicator
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 24.0),
                  child: Text(
                    'Vault: guest@numista.ai',
                    style: TextStyle(color: Colors.blueAccent, fontSize: 14),
                  ),
                ),
                const SizedBox(height: 24),
                
                // Navigation Items
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    children: [
                      _buildNavItem('Home Dashboard'),
                      _buildNavItem('My Collection'),
                      _buildNavItem('Coin Programs'),
                      _buildNavItem('Add New Coins'),
                      _buildNavItem('Inventory'),
                      _buildNavItem('My Wishlist'),
                      _buildNavItem('Settings & Backup'),
                      _buildNavItem('Our Team'),
                      _buildNavItem('Customer Service'),
                      _buildNavItem('🔍 Numista Lookup'),
                    ],
                  ),
                ),
                
                // Log Out
                Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black87,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    ),
                    onPressed: () {},
                    child: const Text('Log Out'),
                  ),
                ),
              ],
            ),
          ),
          
          // Main Content Area
          Expanded(
            child: _buildBody(),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(String title) {
    final bool isActive = _activeRoute == title;
    
    return InkWell(
      onTap: () {
        setState(() {
          _activeRoute = title;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 8.0),
        child: Row(
          children: [
            // Radio button literal visualization
            Container(
              width: 16,
              height: 16,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isActive ? const Color(0xFFF63366) : Colors.white,
                border: Border.all(
                  color: isActive ? const Color(0xFFF63366) : Colors.white54,
                  width: isActive ? 4 : 1,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Text(
              title,
              style: TextStyle(
                color: isActive ? Colors.white : Colors.white70,
                fontSize: 14,
                fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
