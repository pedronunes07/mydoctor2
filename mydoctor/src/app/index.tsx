import { Link } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { getApiBaseUrl, isApiMode } from '@/lib/api-config';

export default function Index() {
  const apiUrl = getApiBaseUrl();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>MyDoctor</Text>
      <Text style={styles.subtitle}>Consultas, chat e receitas médicas</Text>

      {isApiMode() ? (
        <>
          <Text style={styles.hint}>API: {apiUrl}</Text>
          <Link href="/app-web" style={styles.button}>
            Abrir sistema web
          </Link>
        </>
      ) : (
        <Text style={styles.warn}>
          Defina EXPO_PUBLIC_API_URL no arquivo .env (ex.: http://127.0.0.1:8000)
        </Text>
      )}

      <Link href="/login" style={styles.link}>
        Tela de login (local)
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: '700', marginBottom: 8 },
  subtitle: { fontSize: 16, color: '#555', marginBottom: 24 },
  hint: { fontSize: 12, color: '#888', marginBottom: 12 },
  warn: { color: '#c0392b', marginBottom: 16 },
  button: {
    backgroundColor: '#2E86DE',
    color: '#fff',
    padding: 14,
    textAlign: 'center',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 16,
  },
  link: { color: '#2E86DE', fontSize: 16 },
});
