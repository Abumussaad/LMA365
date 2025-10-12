import { Stack } from 'expo-router';

export default function AdminLayout() {
  return (
    <Stack screenOptions={{ headerShown: true }}>
      <Stack.Screen 
        name="index" 
        options={{ title: 'Admin Dashboard' }}
      />
      <Stack.Screen 
        name="services" 
        options={{ title: 'Service Catalog' }}
      />
      <Stack.Screen 
        name="promotions" 
        options={{ title: 'Promotions' }}
      />
    </Stack>
  );
}