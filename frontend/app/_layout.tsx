import React, { useEffect } from 'react';
import { Slot } from 'expo-router';
import { useAuthStore } from '../store/authStore';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function RootLayout() {
  const loadToken = useAuthStore(state => state.loadToken);

  useEffect(() => {
    loadToken();
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <Slot />
    </GestureHandlerRootView>
  );
}