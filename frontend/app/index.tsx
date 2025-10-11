import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../store/authStore';

export default function Index() {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuthStore();
  const [hasRedirected, setHasRedirected] = useState(false);

  useEffect(() => {
    if (!isLoading && !hasRedirected) {
      setHasRedirected(true);
      
      if (isAuthenticated && user) {
        // Navigate to role-specific home screen
        switch (user.role) {
          case 'customer':
            router.replace('/(tabs)/customer');
            break;
          case 'dispatcher':
            router.replace('/(tabs)/dispatcher');
            break;
          case 'technician':
            router.replace('/(tabs)/technician');
            break;
          case 'admin':
            router.replace('/(tabs)/admin');
            break;
          default:
            router.replace('/auth/login');
        }
      } else {
        router.replace('/auth/login');
      }
    }
  }, [isAuthenticated, isLoading, user, hasRedirected]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#007AFF" />
      <Text style={styles.text}>Loading...</Text>
    </View>
  );
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