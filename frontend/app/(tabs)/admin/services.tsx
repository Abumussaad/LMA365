import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Alert,
  Modal,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { useAuthStore } from '../../../store/authStore';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL + '/api';

export default function AdminServices() {
  const token = useAuthStore(state => state.token);
  const [services, setServices] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [price, setPrice] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState('60');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/services`);
      setServices(response.data);
    } catch (error) {
      Alert.alert('Error', 'Failed to fetch services');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateService = async () => {
    if (!name || !category || !price) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    setSaving(true);
    try {
      await axios.post(
        `${API_URL}/services`,
        {
          name,
          category,
          base_price: parseFloat(price),
          description: description || undefined,
          duration_minutes: parseInt(duration)
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      Alert.alert('Success', 'Service created successfully');
      setShowModal(false);
      resetForm();
      fetchServices();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create service');
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setName('');
    setCategory('');
    setPrice('');
    setDescription('');
    setDuration('60');
  };

  const renderService = ({ item }: any) => (
    <View style={styles.serviceCard}>
      <View style={styles.serviceHeader}>
        <Text style={styles.serviceName}>{item.name}</Text>
        <Text style={styles.servicePrice}>SAR {item.base_price}</Text>
      </View>
      <Text style={styles.serviceCategory}>{item.category}</Text>
      {item.description && (
        <Text style={styles.serviceDescription}>{item.description}</Text>
      )}
      <Text style={styles.serviceDuration}>
        <Ionicons name="time" size={14} color="#666" /> {item.duration_minutes} minutes
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>Service Catalog</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowModal(true)}
        >
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={services}
        renderItem={renderService}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={fetchServices} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="construct-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No services yet</Text>
          </View>
        }
      />

      <Modal
        visible={showModal}
        animationType="slide"
        transparent={true}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>New Service</Text>
              <TouchableOpacity onPress={() => {
                setShowModal(false);
                resetForm();
              }}>
                <Ionicons name="close" size={28} color="#000" />
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.input}
              placeholder="Service Name *"
              value={name}
              onChangeText={setName}
            />

            <TextInput
              style={styles.input}
              placeholder="Category *"
              value={category}
              onChangeText={setCategory}
            />

            <TextInput
              style={styles.input}
              placeholder="Base Price (SAR) *"
              value={price}
              onChangeText={setPrice}
              keyboardType="decimal-pad"
            />

            <TextInput
              style={styles.input}
              placeholder="Duration (minutes)"
              value={duration}
              onChangeText={setDuration}
              keyboardType="number-pad"
            />

            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Description"
              value={description}
              onChangeText={setDescription}
              multiline
              numberOfLines={4}
            />

            <TouchableOpacity
              style={[styles.saveButton, saving && styles.saveButtonDisabled]}
              onPress={handleCreateService}
              disabled={saving}
            >
              {saving ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.saveButtonText}>Create Service</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    padding: 16,
  },
  serviceCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  serviceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  serviceName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    flex: 1,
  },
  servicePrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  serviceCategory: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  serviceDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  serviceDuration: {
    fontSize: 12,
    color: '#999',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    marginTop: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '90%',
    padding: 16,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
  },
  input: {
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 12,
    backgroundColor: '#fff',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  saveButton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});