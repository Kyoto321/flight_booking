import 'package:flutter/material.dart';
import '../../../../core/colors.dart';
import '../data/passenger_model.dart';
import '../data/passenger_repository.dart';

class PassengerFormScreen extends StatefulWidget {
  final Passenger? passenger;

  const PassengerFormScreen({super.key, this.passenger});

  @override
  State<PassengerFormScreen> createState() => _PassengerFormScreenState();
}

class _PassengerFormScreenState extends State<PassengerFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _repository = PassengerRepository();
  bool _isLoading = false;

  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _dobController;
  late TextEditingController _idNumberController;

  String _selectedGender = 'MALE';
  String _selectedType = 'ADULT';
  String _selectedRelationship = 'SELF';
  String _selectedIdType = 'PASSPORT';

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController(text: widget.passenger?.firstName);
    _lastNameController = TextEditingController(text: widget.passenger?.lastName);
    _dobController = TextEditingController(text: widget.passenger?.dob);
    _idNumberController = TextEditingController(text: widget.passenger?.idNumber);

    if (widget.passenger != null) {
      _selectedGender = widget.passenger!.gender;
      _selectedType = widget.passenger!.passengerType;
      _selectedRelationship = widget.passenger!.relationship;
      _selectedIdType = widget.passenger!.idType;
    }
  }

  Future<void> _savePassenger() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final passenger = Passenger(
      id: widget.passenger?.id,
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      dob: _dobController.text.trim(),
      gender: _selectedGender,
      nationality: 'Nigerian',
      passengerType: _selectedType,
      relationship: _selectedRelationship,
      idType: _selectedIdType,
      idNumber: _idNumberController.text.trim(),
    );

    bool success;
    if (widget.passenger == null) {
      success = await _repository.createPassenger(passenger);
    } else {
      success = await _repository.updatePassenger(widget.passenger!.id!, passenger);
    }

    setState(() => _isLoading = false);

    if (success && mounted) {
      Navigator.pop(context, true);
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to save passenger details')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.passenger != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Edit Passenger' : 'Add Passenger', style: const TextStyle(color: AppColors.white)),
        backgroundColor: AppColors.primaryBlue,
        iconTheme: const IconThemeData(color: AppColors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildTextField('First Name', _firstNameController),
              const SizedBox(height: 16),
              _buildTextField('Last Name', _lastNameController),
              const SizedBox(height: 16),
              _buildTextField('Date of Birth (YYYY-MM-DD)', _dobController),
              const SizedBox(height: 16),
              
              _buildDropdown('Gender', _selectedGender, ['MALE', 'FEMALE'], (val) => setState(() => _selectedGender = val!)),
              const SizedBox(height: 16),
              
              _buildDropdown('Passenger Type', _selectedType, ['ADULT', 'CHILD', 'INFANT'], (val) => setState(() => _selectedType = val!)),
              const SizedBox(height: 16),
              
              _buildDropdown('Relationship', _selectedRelationship, ['SELF', 'SPOUSE', 'CHILD', 'FRIEND', 'STAFF', 'OTHER'], (val) => setState(() => _selectedRelationship = val!)),
              const SizedBox(height: 16),
              
              _buildDropdown('ID Type', _selectedIdType, ['PASSPORT', 'NIN', 'VOTERS'], (val) => setState(() => _selectedIdType = val!)),
              const SizedBox(height: 16),
              
              _buildTextField('ID Number', _idNumberController),
              const SizedBox(height: 32),
              
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _savePassenger,
                  child: _isLoading 
                      ? const CircularProgressIndicator(color: AppColors.white)
                      : Text(isEditing ? 'Save Changes' : 'Add Passenger', style: const TextStyle(fontSize: 18)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        filled: true,
        fillColor: AppColors.white,
      ),
      validator: (value) => (value?.isEmpty ?? true) ? 'Required field' : null,
    );
  }

  Widget _buildDropdown(String label, String value, List<String> items, Function(String?) onChanged) {
    return DropdownButtonFormField<String>(
      value: value,
      decoration: InputDecoration(
        labelText: label,
        filled: true,
        fillColor: AppColors.white,
      ),
      items: items.map((item) => DropdownMenuItem(value: item, child: Text(item))).toList(),
      onChanged: onChanged,
    );
  }
}
