import React from 'react';
import { View, Text } from 'react-native';

export default function TabsLayout() {
  // This should never be rendered - navigation happens from index.tsx
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Redirecting...</Text>
    </View>
  );
}