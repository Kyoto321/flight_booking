import '../../../core/api_service.dart';

class AuthRepository {
  final ApiService _apiService = ApiService();

  Future<bool> register({
    required String email,
    required String phone,
    required String password,
  }) async {
    try {
      final response = await _apiService.post('/auth/register/', data: {
        'email': email,
        'phone': phone,
        'password': password,
      });
      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> verifyOtp({
    required String email,
    required String code,
  }) async {
    try {
      final response = await _apiService.post('/auth/otp/verify/', data: {
        'email': email,
        'code': code,
        'purpose': 'REGISTER',
      });
      return response.data;
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiService.post('/auth/login/', data: {
        'email': email,
        'password': password,
      });
      return response.data;
    } catch (e) {
      return null;
    }
  }
}
