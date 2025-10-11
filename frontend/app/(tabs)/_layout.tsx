import React from 'react';
import { Stack } from 'expo-router';

export default function TabsLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="customer" />
      <Stack.Screen name="dispatcher" />
      <Stack.Screen name="technician" />
      <Stack.Screen name="admin" />
    </Stack>
  );
}