import '../../../core/api_service.dart';
import 'passenger_model.dart';

class PassengerRepository {
  final ApiService _apiService = ApiService();

  Future<List<Passenger>> getPassengers() async {
    try {
      final response = await _apiService.get('/profile/passengers/');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Passenger.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<bool> createPassenger(Passenger passenger) async {
    try {
      final response = await _apiService.post('/profile/passengers/', data: passenger.toJson());
      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  Future<bool> updatePassenger(int id, Passenger passenger) async {
    try {
      final response = await _apiService.put('/profile/passengers/$id/', data: passenger.toJson());
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<bool> deletePassenger(int id) async {
    try {
      final response = await _apiService.delete('/profile/passengers/$id/');
      return response.statusCode == 204;
    } catch (e) {
      return false;
    }
  }
}
