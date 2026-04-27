import 'package:flutter/material.dart';
import '../../../../core/colors.dart';
import '../../data/auth_repository.dart';
import '../../../booking/presentation/pages/dashboard_screen.dart';

class OTPVerificationScreen extends StatefulWidget {
  final String email;
  const OTPVerificationScreen({super.key, required this.email});

  @override
  State<OTPVerificationScreen> createState() => _OTPVerificationScreenState();
}

class _OTPVerificationScreenState extends State<OTPVerificationScreen> {
  final List<TextEditingController> _controllers = List.generate(6, (index) => TextEditingController());
  final List<FocusNode> _focusNodes = List.generate(6, (index) => FocusNode());

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(backgroundColor: Colors.transparent, elevation: 0),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 20),
            Text(
              'Verify Account',
              style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 32),
            ),
            const SizedBox(height: 8),
            Text(
              'Enter the 6-digit code sent to ${widget.email}',
              style: const TextStyle(color: AppColors.grey),
            ),
            const SizedBox(height: 48),
            
            // OTP Input Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: List.generate(6, (index) {
                return SizedBox(
                  width: 48,
                  child: TextFormField(
                    controller: _controllers[index],
                    focusNode: _focusNodes[index],
                    textAlign: TextAlign.center,
                    keyboardType: TextInputType.number,
                    maxLength: 1,
                    onChanged: (value) {
                      if (value.isNotEmpty && index < 5) {
                        _focusNodes[index + 1].requestFocus();
                      } else if (value.isEmpty && index > 0) {
                        _focusNodes[index - 1].requestFocus();
                      }
                    },
                    decoration: InputDecoration(
                      counterText: '',
                      filled: true,
                      fillColor: AppColors.cardBg,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                );
              }),
            ),
            
            const SizedBox(height: 48),
            
            ElevatedButton(
              onPressed: () async {
                String code = _controllers.map((e) => e.text).join();
                if (code.length == 6) {
                  final repository = AuthRepository();
                  final result = await repository.verifyOtp(
                    email: widget.email,
                    code: code,
                  );
                  
                  if (result != null && mounted) {
                    // Success!
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Account verified successfully!')),
                    );
                    Navigator.pushAndRemoveUntil(
                      context,
                      MaterialPageRoute(builder: (context) => const DashboardScreen()),
                      (route) => false,
                    );
                  } else if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Invalid code. Please check and try again.')),
                    );
                  }
                }
              },
              child: const Text('Verify Now'),
            ),
            
            const SizedBox(height: 24),
            
            Center(
              child: TextButton(
                onPressed: () {},
                child: const Text('Resend Code', style: TextStyle(color: AppColors.accentBlue)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
