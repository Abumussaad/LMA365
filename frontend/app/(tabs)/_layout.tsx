import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';

export default function TabsLayout() {
  const user = useAuthStore(state => state.user);
  const role = user?.role;

  // Customer tabs
  if (role === 'customer') {
    return (
      <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
        <Tabs.Screen
          name="customer/index"
          options={{
            title: 'Requests',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="list" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="customer/new-request"
          options={{
            title: 'New Request',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="add-circle" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="customer/profile"
          options={{
            title: 'Profile',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="person" size={size} color={color} />
            ),
          }}
        />
        {/* Hide other role screens */}
        <Tabs.Screen name="dispatcher/index" options={{ href: null }} />
        <Tabs.Screen name="technician/index" options={{ href: null }} />
        <Tabs.Screen name="admin/index" options={{ href: null }} />
      </Tabs>
    );
  }

  // Dispatcher tabs
  if (role === 'dispatcher') {
    return (
      <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
        <Tabs.Screen
          name="dispatcher/index"
          options={{
            title: 'Dashboard',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="grid" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="dispatcher/technicians"
          options={{
            title: 'Technicians',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="people" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen name="customer/index" options={{ href: null }} />
        <Tabs.Screen name="customer/new-request" options={{ href: null }} />
        <Tabs.Screen name="customer/profile" options={{ href: null }} />
        <Tabs.Screen name="technician/index" options={{ href: null }} />
        <Tabs.Screen name="admin/index" options={{ href: null }} />
      </Tabs>
    );
  }

  // Technician tabs
  if (role === 'technician') {
    return (
      <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
        <Tabs.Screen
          name="technician/index"
          options={{
            title: 'Jobs',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="briefcase" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="technician/profile"
          options={{
            title: 'Profile',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="person" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen name="customer/index" options={{ href: null }} />
        <Tabs.Screen name="customer/new-request" options={{ href: null }} />
        <Tabs.Screen name="customer/profile" options={{ href: null }} />
        <Tabs.Screen name="dispatcher/index" options={{ href: null }} />
        <Tabs.Screen name="admin/index" options={{ href: null }} />
      </Tabs>
    );
  }

  // Admin tabs
  if (role === 'admin') {
    return (
      <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
        <Tabs.Screen
          name="admin/index"
          options={{
            title: 'Dashboard',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="stats-chart" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="admin/services"
          options={{
            title: 'Services',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="settings" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="admin/promotions"
          options={{
            title: 'Promotions',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="pricetag" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen name="customer/index" options={{ href: null }} />
        <Tabs.Screen name="customer/new-request" options={{ href: null }} />
        <Tabs.Screen name="customer/profile" options={{ href: null }} />
        <Tabs.Screen name="dispatcher/index" options={{ href: null }} />
        <Tabs.Screen name="technician/index" options={{ href: null }} />
        <Tabs.Screen name="technician/profile" options={{ href: null }} />
      </Tabs>
    );
  }

  // Default fallback
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
      <Tabs.Screen
        name="customer/profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen name="customer/index" options={{ href: null }} />
      <Tabs.Screen name="customer/new-request" options={{ href: null }} />
      <Tabs.Screen name="dispatcher/index" options={{ href: null }} />
      <Tabs.Screen name="technician/index" options={{ href: null }} />
      <Tabs.Screen name="admin/index" options={{ href: null }} />
    </Tabs>
  );
}