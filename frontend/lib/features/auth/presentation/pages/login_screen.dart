import 'package:flutter/material.dart';
import '../../../../core/colors.dart';
import 'register_screen.dart';
import '../../../booking/presentation/pages/dashboard_screen.dart';
import '../../data/auth_repository.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 60),
                Text(
                  'Welcome Back',
                  style: Theme.of(context).textTheme.displayLarge?.copyWith(
                    fontSize: 32,
                    color: AppColors.white,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Sign in to explore your next journey',
                  style: TextStyle(color: AppColors.grey, fontSize: 16),
                ),
                const SizedBox(height: 48),
                
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
                
                // Password Field
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.lock_outline, color: AppColors.grey),
                    hintText: 'Password',
                    suffixIcon: Icon(Icons.visibility_off_outlined, color: AppColors.grey),
                  ),
                  validator: (value) => 
                      (value?.isEmpty ?? true) ? 'Please enter password' : null,
                ),
                const SizedBox(height: 12),
                
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () {},
                    child: const Text('Forgot Password?', 
                        style: TextStyle(color: AppColors.accentBlue)),
                  ),
                ),
                const SizedBox(height: 32),
                
                ElevatedButton(
                  onPressed: () async {
                    if (_formKey.currentState!.validate()) {
                      final repository = AuthRepository();
                      final result = await repository.login(
                        email: _emailController.text,
                        password: _passwordController.text,
                      );
                      
                      if (result != null && mounted) {
                        Navigator.pushAndRemoveUntil(
                          context,
                          MaterialPageRoute(builder: (context) => const DashboardScreen()),
                          (route) => false,
                        );
                      } else if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Invalid credentials. Please try again.')),
                        );
                      }
                    }
                  },
                  child: const Text('Login'),
                ),
                const SizedBox(height: 24),
                
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text("Don't have an account?", 
                        style: TextStyle(color: AppColors.grey)),
                    TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => const RegisterScreen()),
                        );
                      },
                      child: const Text('Register', 
                          style: TextStyle(color: AppColors.accentBlue)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
