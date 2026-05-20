import { StyleSheet, View } from 'react-native';
import { WebView } from 'react-native-webview';

import { getApiBaseUrl } from '@/lib/api-config';

export default function AppWebScreen() {
  const base = getApiBaseUrl() ?? 'http://127.0.0.1:8000';

  return (
    <View style={styles.container}>
      <WebView source={{ uri: base }} style={styles.web} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  web: { flex: 1 },
});
