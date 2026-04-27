class Passenger {
  final int? id;
  final String firstName;
  final String lastName;
  final String dob;
  final String gender;
  final String nationality;
  final String passengerType;
  final String relationship;
  final String idType;
  final String idNumber;

  Passenger({
    this.id,
    required this.firstName,
    required this.lastName,
    required this.dob,
    required this.gender,
    required this.nationality,
    required this.passengerType,
    required this.relationship,
    required this.idType,
    required this.idNumber,
  });

  factory Passenger.fromJson(Map<String, dynamic> json) {
    return Passenger(
      id: json['id'],
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      dob: json['dob'] ?? '',
      gender: json['gender'] ?? '',
      nationality: json['nationality'] ?? 'Nigerian',
      passengerType: json['passenger_type'] ?? '',
      relationship: json['relationship'] ?? '',
      idType: json['id_type'] ?? '',
      idNumber: json['id_number'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'first_name': firstName,
      'last_name': lastName,
      'dob': dob,
      'gender': gender,
      'nationality': nationality,
      'passenger_type': passengerType,
      'relationship': relationship,
      'id_type': idType,
      'id_number': idNumber,
    };
  }
}
