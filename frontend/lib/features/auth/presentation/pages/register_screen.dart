import 'package:flutter/material.dart';
import '../../../../core/colors.dart';
import '../pages/otp_verification_screen.dart';
import '../../data/auth_repository.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: AppColors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Join Book4me',
                  style: Theme.of(context).textTheme.displayLarge?.copyWith(
                    fontSize: 32,
                    color: AppColors.white,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Your domestic flight concierge awaits',
                  style: TextStyle(color: AppColors.grey, fontSize: 16),
                ),
                const SizedBox(height: 40),
                
                // Email Field
                TextFormField(
                  controller: _emailController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.email_outlined, color: AppColors.grey),
                    hintText: 'Email Address',
                  ),
                  validator: (value) => 
                      (value?.isEmpty ?? true) ? 'Please enter email' : null,
                ),
                const SizedBox(height: 20),
                
                // Phone Field
                TextFormField(
                  controller: _phoneController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.phone_outlined, color: AppColors.grey),
                    hintText: 'Phone Number',
                  ),
                  validator: (value) => 
                      (value?.isEmpty ?? true) ? 'Please enter phone' : null,
                ),
                const SizedBox(height: 20),
                
                // Password Field
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.lock_outline, color: AppColors.grey),
                    hintText: 'Create Password',
                  ),
                  validator: (value) => 
                      (value?.length ?? 0) < 6 ? 'Minimum 6 characters' : null,
                ),
                const SizedBox(height: 48),
                
                ElevatedButton(
                  onPressed: () async {
                    if (_formKey.currentState!.validate()) {
                      final repository = AuthRepository();
                      final success = await repository.register(
                        email: _emailController.text,
                        phone: _phoneController.text,
                        password: _passwordController.text,
                      );
                      
                      if (success && mounted) {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => OTPVerificationScreen(
                              email: _emailController.text,
                            ),
                          ),
                        );
                      } else if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Registration failed. Try again.')),
                        );
                      }
                    }
                  },
                  child: const Text('Create Account'),
                ),
                const SizedBox(height: 24),
                
                const Center(
                  child: Text(
                    'By continuing, you agree to our Terms of Service',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppColors.grey, fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
