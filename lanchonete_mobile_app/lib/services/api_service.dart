import 'dart:convert';
import 'package:http/http.dart' as http;

const String API_BASE_URL = 'http://localhost:8000';

String? _authToken; // Variável para armazenar o token

void setAuthToken(String? token){
  _authToken = token;
}

// exemplo de função de login
Future<Map<String, dynamic>> registerUser(String email, String password, bool isOwner) async{
  final response = await http.post(
    Uri.parse('$API_BASE_URL/users/register/'),
    headers: {
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'email': email,
      'password': password,
      'is_active': true,
      'is_owner': isOwner,
    }),
  );
  if (response.statusCode == 201){
    return json.decode(response.body);
  } else{
    final errorBody = json.decode(response.body);
    throw Exception('Falha no registro: ${response.statusCode} - ${errorBody['detail'] ?? 'Erro desconhecido'}');
  }
}

Future<Map<String, dynamic>> login(String email, String password) async { // <--- Verifique esta linha
  final response = await http.post(
    Uri.parse('$API_BASE_URL/users/token'),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'username=$email&password=$password',
  );

  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    setAuthToken(data['access_token']);
    return data;
  } else {
    final errorBody = json.decode(response.body);
    throw Exception('Falha no login: ${response.statusCode} - ${errorBody['detail'] ?? 'Erro desconhecido'}');
  }
}

// Exemplo de requisição autenticada(Get users)
Future<List<dynamic>> getUsers() async{
  if (_authToken == null) {
    throw Exception('Usuário não autenticado. Faça login primeiro.');
  }
  final response = await http.get(
    Uri.parse('$API_BASE_URL/users/'),
    headers: {
      'Authorization': 'Bearer $_authToken',
      'Content-Type': 'application/json',
    },
  );

  if (response.statusCode == 200){
    return json.decode(response.body);
  } else if (response.statusCode == 401 || response.statusCode == 403){
    setAuthToken(null); // Limpa o token se for não autorizado/proibido
    throw Exception('Não autorizado ou token inválido: ${response.body}');
  }
  else{
    throw Exception('Falha ao carregar usuários: ${response.statusCode} - ${response.body}');
  }
}