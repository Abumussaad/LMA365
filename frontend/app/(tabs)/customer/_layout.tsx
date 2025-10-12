import { Stack } from 'expo-router';

export default function CustomerLayout() {
  return (
    <Stack screenOptions={{ headerShown: true }}>
      <Stack.Screen 
        name="index" 
        options={{ title: 'My Requests' }}
      />
      <Stack.Screen 
        name="new-request" 
        options={{ title: 'New Request' }}
      />
      <Stack.Screen 
        name="profile" 
        options={{ title: 'Profile' }}
      />
    </Stack>
  );
}