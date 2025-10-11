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
import { format } from 'date-fns';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Platform } from 'react-native';
import { Picker } from '@react-native-picker/picker';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL + '/api';

export default function AdminPromotions() {
  const token = useAuthStore(state => state.token);
  const [promotions, setPromotions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  
  const [code, setCode] = useState('');
  const [discountType, setDiscountType] = useState('PERCENT');
  const [discountValue, setDiscountValue] = useState('');
  const [minSpend, setMinSpend] = useState('0');
  const [effectiveStart, setEffectiveStart] = useState(new Date());
  const [effectiveEnd, setEffectiveEnd] = useState(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000));
  const [showStartPicker, setShowStartPicker] = useState(false);
  const [showEndPicker, setShowEndPicker] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchPromotions();
  }, []);

  const fetchPromotions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/promotions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPromotions(response.data);
    } catch (error) {
      Alert.alert('Error', 'Failed to fetch promotions');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePromotion = async () => {
    if (!code || !discountValue) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    setSaving(true);
    try {
      await axios.post(
        `${API_URL}/promotions`,
        {
          code: code.toUpperCase(),
          discount_type: discountType,
          discount_value: parseFloat(discountValue),
          effective_start: effectiveStart.toISOString(),
          effective_end: effectiveEnd.toISOString(),
          min_spend: parseFloat(minSpend)
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      Alert.alert('Success', 'Promotion created successfully');
      setShowModal(false);
      resetForm();
      fetchPromotions();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create promotion');
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setCode('');
    setDiscountType('PERCENT');
    setDiscountValue('');
    setMinSpend('0');
    setEffectiveStart(new Date());
    setEffectiveEnd(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000));
  };

  const renderPromotion = ({ item }: any) => {
    const isActive = item.active &&
      new Date(item.effective_start) <= new Date() &&
      new Date(item.effective_end) >= new Date();

    return (
      <View style={styles.promoCard}>
        <View style={styles.promoHeader}>
          <Text style={styles.promoCode}>{item.code}</Text>
          <View style={[styles.statusBadge, { backgroundColor: isActive ? '#34C759' : '#8E8E93' }]}>
            <Text style={styles.statusText}>{isActive ? 'ACTIVE' : 'INACTIVE'}</Text>
          </View>
        </View>
        
        <Text style={styles.promoDiscount}>
          {item.discount_type === 'PERCENT' 
            ? `${item.discount_value}% OFF`
            : `SAR ${item.discount_value} OFF`
          }
        </Text>
        
        <Text style={styles.promoDetails}>Min spend: SAR {item.min_spend}</Text>
        <Text style={styles.promoDetails}>
          Valid: {format(new Date(item.effective_start), 'MMM dd, yyyy')} - {format(new Date(item.effective_end), 'MMM dd, yyyy')}
        </Text>
        
        {item.usage_limit && (
          <Text style={styles.promoDetails}>
            Used: {item.used_count}/{item.usage_limit}
          </Text>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>Promotions</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowModal(true)}
        >
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={promotions}
        renderItem={renderPromotion}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={fetchPromotions} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="pricetag-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No promotions yet</Text>
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
              <Text style={styles.modalTitle}>New Promotion</Text>
              <TouchableOpacity onPress={() => {
                setShowModal(false);
                resetForm();
              }}>
                <Ionicons name="close" size={28} color="#000" />
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.input}
              placeholder="Coupon Code *"
              value={code}
              onChangeText={(text) => setCode(text.toUpperCase())}
              autoCapitalize="characters"
            />

            <Text style={styles.label}>Discount Type</Text>
            <Picker
              selectedValue={discountType}
              onValueChange={setDiscountType}
              style={styles.picker}
            >
              <Picker.Item label="Percentage (%)" value="PERCENT" />
              <Picker.Item label="Fixed Amount (SAR)" value="FIXED_AMOUNT" />
            </Picker>

            <TextInput
              style={styles.input}
              placeholder="Discount Value *"
              value={discountValue}
              onChangeText={setDiscountValue}
              keyboardType="decimal-pad"
            />

            <TextInput
              style={styles.input}
              placeholder="Minimum Spend (SAR)"
              value={minSpend}
              onChangeText={setMinSpend}
              keyboardType="decimal-pad"
            />

            <Text style={styles.label}>Start Date</Text>
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowStartPicker(true)}
            >
              <Ionicons name="calendar" size={20} color="#007AFF" />
              <Text style={styles.dateText}>
                {format(effectiveStart, 'MMM dd, yyyy HH:mm')}
              </Text>
            </TouchableOpacity>

            {showStartPicker && (
              <DateTimePicker
                value={effectiveStart}
                mode="datetime"
                display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                onChange={(event, date) => {
                  setShowStartPicker(Platform.OS === 'ios');
                  if (date) setEffectiveStart(date);
                }}
              />
            )}

            <Text style={styles.label}>End Date</Text>
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowEndPicker(true)}
            >
              <Ionicons name="calendar" size={20} color="#007AFF" />
              <Text style={styles.dateText}>
                {format(effectiveEnd, 'MMM dd, yyyy HH:mm')}
              </Text>
            </TouchableOpacity>

            {showEndPicker && (
              <DateTimePicker
                value={effectiveEnd}
                mode="datetime"
                display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                onChange={(event, date) => {
                  setShowEndPicker(Platform.OS === 'ios');
                  if (date) setEffectiveEnd(date);
                }}
                minimumDate={effectiveStart}
              />
            )}

            <TouchableOpacity
              style={[styles.saveButton, saving && styles.saveButtonDisabled]}
              onPress={handleCreatePromotion}
              disabled={saving}
            >
              {saving ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.saveButtonText}>Create Promotion</Text>
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
  promoCard: {
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
  promoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  promoCode: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  promoDiscount: {
    fontSize: 18,
    fontWeight: '600',
    color: '#007AFF',
    marginBottom: 8,
  },
  promoDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
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
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#000',
    marginBottom: 8,
    marginTop: 8,
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
  picker: {
    marginBottom: 12,
  },
  dateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    gap: 12,
    marginBottom: 12,
  },
  dateText: {
    fontSize: 16,
    color: '#000',
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