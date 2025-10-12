import { Stack } from 'expo-router';

export default function DispatcherLayout() {
  return (
    <Stack screenOptions={{ headerShown: true }}>
      <Stack.Screen 
        name="index" 
        options={{ title: 'Dispatch Dashboard' }}
      />
      <Stack.Screen 
        name="technicians" 
        options={{ title: 'Technicians' }}
      />
    </Stack>
  );
}