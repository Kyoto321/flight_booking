import 'package:flutter/material.dart';
import 'core/theme.dart';
import 'features/auth/presentation/pages/splash_screen.dart';

void main() {
  runApp(const Book4meApp());
}

class Book4meApp extends StatelessWidget {
  const Book4meApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Book4me',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const SplashScreen(),
    );
  }
}
