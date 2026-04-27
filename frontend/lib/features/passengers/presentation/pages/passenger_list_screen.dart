import 'package:flutter/material.dart';
import '../../../../core/colors.dart';
import '../data/passenger_model.dart';
import '../data/passenger_repository.dart';
import 'passenger_form_screen.dart';

class PassengerListScreen extends StatefulWidget {
  const PassengerListScreen({super.key});

  @override
  State<PassengerListScreen> createState() => _PassengerListScreenState();
}

class _PassengerListScreenState extends State<PassengerListScreen> {
  final PassengerRepository _repository = PassengerRepository();
  List<Passenger> _passengers = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchPassengers();
  }

  Future<void> _fetchPassengers() async {
    setState(() => _isLoading = true);
    final passengers = await _repository.getPassengers();
    if (mounted) {
      setState(() {
        _passengers = passengers;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Passengers', style: TextStyle(color: AppColors.white)),
        backgroundColor: AppColors.primaryBlue,
        iconTheme: const IconThemeData(color: AppColors.white),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _passengers.isEmpty
              ? _buildEmptyState()
              : _buildPassengerList(),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primaryBlue,
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const PassengerFormScreen()),
          );
          if (result == true) {
            _fetchPassengers();
          }
        },
        icon: const Icon(Icons.add, color: AppColors.white),
        label: const Text('Add Passenger', style: TextStyle(color: AppColors.white)),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.group_off, size: 80, color: AppColors.grey.withOpacity(0.5)),
          const SizedBox(height: 16),
          const Text(
            'No passengers saved yet.',
            style: TextStyle(fontSize: 18, color: AppColors.darkGrey, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Add family and friends for quicker booking.',
            style: TextStyle(color: AppColors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildPassengerList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _passengers.length,
      itemBuilder: (context, index) {
        final passenger = _passengers[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          color: AppColors.white,
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: ListTile(
            contentPadding: const EdgeInsets.all(16),
            leading: CircleAvatar(
              backgroundColor: AppColors.lightBlue,
              child: Icon(
                passenger.gender == 'MALE' ? Icons.face : Icons.face_3,
                color: AppColors.primaryBlue,
              ),
            ),
            title: Text(
              '${passenger.firstName} ${passenger.lastName}',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text('Type: ${passenger.passengerType}'),
                Text('ID: ${passenger.idNumber}'),
              ],
            ),
            trailing: IconButton(
              icon: const Icon(Icons.delete_outline, color: AppColors.error),
              onPressed: () => _confirmDelete(passenger),
            ),
            onTap: () async {
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => PassengerFormScreen(passenger: passenger),
                ),
              );
              if (result == true) {
                _fetchPassengers();
              }
            },
          ),
        );
      },
    );
  }

  Future<void> _confirmDelete(Passenger passenger) async {
    final bool? confirm = await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Passenger'),
        content: Text('Are you sure you want to delete ${passenger.firstName}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel', style: TextStyle(color: AppColors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete', style: TextStyle(color: AppColors.error)),
          ),
        ],
      ),
    );

    if (confirm == true && passenger.id != null) {
      final success = await _repository.deletePassenger(passenger.id!);
      if (success) {
        _fetchPassengers();
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to delete passenger')),
          );
        }
      }
    }
  }
}
