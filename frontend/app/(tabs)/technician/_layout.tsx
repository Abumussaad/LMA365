import { Stack } from 'expo-router';

export default function TechnicianLayout() {
  return (
    <Stack screenOptions={{ headerShown: true }}>
      <Stack.Screen 
        name="index" 
        options={{ title: 'My Jobs' }}
      />
      <Stack.Screen 
        name="profile" 
        options={{ title: 'Profile' }}
      />
    </Stack>
  );
}