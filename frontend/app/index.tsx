import { Redirect } from 'expo-router';
import { useAuthStore } from '../store/authStore';
import { View, ActivityIndicator } from 'react-native';

export default function Index() {
  const { isAuthenticated, isLoading, user } = useAuthStore();

  // Show loading while checking auth
  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  // Redirect based on auth state
  if (!isAuthenticated || !user) {
    return <Redirect href="/auth/login" />;
  }

  // Redirect to role-specific home
  const paths: Record<string, string> = {
    customer: '/(tabs)/customer',
    dispatcher: '/(tabs)/dispatcher',
    technician: '/(tabs)/technician',
    admin: '/(tabs)/admin',
  };

  return <Redirect href={paths[user.role] || '/auth/login'} />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  text: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
});