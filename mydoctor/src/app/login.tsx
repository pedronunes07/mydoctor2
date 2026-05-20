import { Link } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

export default function LoginScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>
      <Text style={styles.text}>
        Use &quot;Abrir sistema web&quot; na tela inicial para acessar o login Django
        (email ou CRM + senha).
      </Text>
      <Link href="/" style={styles.link}>
        Voltar
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: '600', marginBottom: 12 },
  text: { fontSize: 15, color: '#444', marginBottom: 24 },
  link: { color: '#2E86DE' },
});
