import React from 'react';
import { Redirect } from 'expo-router';
import { useAuthStore } from '../../store/authStore';

export default function TabsRedirect() {
  const user = useAuthStore(state => state.user);
  
  if (!user) {
    return <Redirect href="/auth/login" />;
  }
  
  // Redirect to role-specific home
  switch (user.role) {
    case 'customer':
      return <Redirect href="/(tabs)/customer" />;
    case 'dispatcher':
      return <Redirect href="/(tabs)/dispatcher" />;
    case 'technician':
      return <Redirect href="/(tabs)/technician" />;
    case 'admin':
      return <Redirect href="/(tabs)/admin" />;
    default:
      return <Redirect href="/auth/login" />;
  }
}