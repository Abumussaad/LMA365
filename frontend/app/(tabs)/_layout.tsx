import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';

export default function TabsLayout() {
  const user = useAuthStore(state => state.user);
  const role = user?.role;

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        headerShown: false,
      }}
    >
      {/* Customer Tabs */}
      <Tabs.Screen
        name="customer"
        options={{
          title: 'Requests',
          href: role === 'customer' ? undefined : null,
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="list" size={size} color={color} />
          ),
        }}
      />

      {/* Dispatcher Tabs */}
      <Tabs.Screen
        name="dispatcher"
        options={{
          title: 'Dashboard',
          href: role === 'dispatcher' ? undefined : null,
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="grid" size={size} color={color} />
          ),
        }}
      />

      {/* Technician Tabs */}
      <Tabs.Screen
        name="technician"
        options={{
          title: 'Jobs',
          href: role === 'technician' ? undefined : null,
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="briefcase" size={size} color={color} />
          ),
        }}
      />

      {/* Admin Tabs */}
      <Tabs.Screen
        name="admin"
        options={{
          title: 'Dashboard',
          href: role === 'admin' ? undefined : null,
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="stats-chart" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}