// lib/main.dart
import 'package:flutter/material.dart';
import 'package:lanchonete_mobile_app/services/api_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lanchonete App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const AuthScreen(),
    );
  }
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String _message = '';
  List<dynamic> _users = [];
  bool _isLoginScreen = true; // <--- NOVA VARIÁVEL DE ESTADO

  // Funções de manipulação
  Future<void> _handleRegister(bool isOwner) async {
    try {
      final responseData = await registerUser(_emailController.text, _passwordController.text, isOwner);
      _message = 'Registro de ${isOwner ? 'Proprietário' : 'Cliente'} bem-sucedido! (${responseData['email']}). Agora faça Login.';
      setState(() {
        _isLoginScreen = true; // Volta para a tela de login após o registro
      });
      _emailController.clear(); // Limpa os campos
      _passwordController.clear();
    } catch (e) {
      _message = 'Erro no registro: ${e.toString()}';
      setState(() {});
    }
  }

  Future<void> _handleLogin() async {
    try {
      await login(_emailController.text, _passwordController.text);
      _message = 'Login bem-sucedido!';
      setState(() {});
      // TODO: Redirecionar para a próxima tela do aplicativo após o login
      // Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => HomeScreen()));
    } catch (e) {
      _message = 'Erro no login: ${e.toString()}';
      setState(() {});
    }
  }

  Future<void> _fetchUsers() async {
    try {
      final users = await getUsers();
      setState(() {
        _users = users;
        _message = 'Usuários carregados!';
      });
    } catch (e) {
      setState(() {
        _message = 'Erro ao buscar usuários: ${e.toString()}';
        _users = [];
      });
    }
  }

  // Novo método para alternar entre login e registro
  void _toggleAuthMode() {
    setState(() {
      _isLoginScreen = !_isLoginScreen;
      _message = ''; // Limpa a mensagem ao alternar
      _emailController.clear();
      _passwordController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_isLoginScreen ? 'Login' : 'Cadastro')), // Título dinâmico
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Senha'),
              obscureText: true,
            ),
            const SizedBox(height: 20),
            if (_isLoginScreen) // Exibe botões de Login se for a tela de Login
              Column(
                children: [
                  ElevatedButton(
                    onPressed: _handleLogin,
                    child: const Text('Entrar'),
                  ),
                  TextButton( // Botão para ir para o cadastro
                    onPressed: _toggleAuthMode,
                    child: const Text('Não tem conta? Cadastre-se'),
                  ),
                ],
              )
            else // Exibe botões de Cadastro se for a tela de Cadastro
              Column(
                children: [
                  ElevatedButton(
                    onPressed: () => _handleRegister(false),
                    child: const Text('Cadastrar como Cliente'),
                  ),
                  ElevatedButton(
                    onPressed: () => _handleRegister(true),
                    child: const Text('Cadastrar como Proprietário'),
                  ),
                  TextButton( // Botão para ir para o login
                    onPressed: _toggleAuthMode,
                    child: const Text('Já tem conta? Fazer Login'),
                  ),
                ],
              ),
            const SizedBox(height: 20),
            Text(_message, style: const TextStyle(color: Colors.red, fontSize: 16)), // Mensagem de feedback
            const SizedBox(height: 20),

            // Botão "Buscar Usuários" e a lista de usuários só visíveis após login (ou para teste)
            // Você pode adicionar uma condição aqui para mostrar só depois de um login bem-sucedido
            ElevatedButton(
              onPressed: _fetchUsers,
              child: const Text('Buscar Usuários (requer login Proprietário)'),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: ListView.builder(
                itemCount: _users.length,
                itemBuilder: (context, index) {
                  final user = _users[index];
                  return ListTile(
                    title: Text(user['email']),
                    subtitle: Text(user['is_owner'] ? 'Proprietário' : 'Cliente'),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}