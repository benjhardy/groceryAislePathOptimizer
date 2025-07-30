# Mobile App Architecture

This document outlines how to extend the Grocery Route Optimizer to mobile platforms (Android and iOS).

## Mobile Development Options

### 1. Kivy (Python-based, Cross-platform)
**Pros:**
- Reuse existing Python code
- Single codebase for Android and iOS
- Native-looking UI components

**Cons:**
- Larger app size
- Performance limitations
- Less native feel

### 2. React Native (JavaScript)
**Pros:**
- Near-native performance
- Large community and ecosystem
- Hot reloading for development
- Access to native APIs

**Cons:**
- Need to rewrite in JavaScript/TypeScript
- Some platform-specific code needed

### 3. Flutter (Dart)
**Pros:**
- Excellent performance
- Beautiful UI out of the box
- Single codebase
- Growing ecosystem

**Cons:**
- Need to learn Dart
- Complete rewrite required

## Recommended Architecture: React Native

### Core Components to Port

1. **Store Finder Service**
   ```javascript
   class StoreFinderService {
     async findNearbyStores(zipCode) {
       // Use native geolocation API
       const location = await Geolocation.getCurrentPosition();
       // Call Kroger API or scraping service
       return fetchStores(location);
     }
   }
   ```

2. **Item Location Service**
   ```javascript
   class ItemLocationService {
     async findItemLocations(items, storeId) {
       // Could use a backend service for scraping
       return await api.post('/items/locate', { items, storeId });
     }
   }
   ```

3. **Route Optimizer**
   ```javascript
   class RouteOptimizer {
     optimizeRoute(itemsWithLocations) {
       // Port the TSP algorithm to JavaScript
       // Or call a backend service
       return optimizedRoute;
     }
   }
   ```

### Mobile-Specific Features

1. **GPS Navigation**
   - Real-time location tracking
   - Turn-by-turn directions in store
   - Proximity alerts for items

2. **Barcode Scanning**
   - Scan items to add to list
   - Verify correct items found

3. **Push Notifications**
   - Sale alerts for list items
   - Store crowd levels
   - Pickup order ready

4. **Offline Mode**
   - Cache store layouts
   - Save lists locally
   - Sync when connected

### Backend Requirements

Create a REST API backend to:
- Handle web scraping (avoid doing on mobile)
- Store user data and lists
- Cache store information
- Process route optimization for complex lists

### Example React Native Screen

```javascript
import React, { useState } from 'react';
import { View, FlatList, Button, Text } from 'react-native';

const ShoppingRouteScreen = ({ route }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const { optimizedRoute } = route.params;

  const markItemFound = () => {
    if (currentIndex < optimizedRoute.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const currentItem = optimizedRoute[currentIndex];

  return (
    <View style={styles.container}>
      <View style={styles.currentItem}>
        <Text style={styles.itemName}>{currentItem.name}</Text>
        <Text style={styles.location}>{currentItem.location}</Text>
        <Button 
          title="Found Item ✓" 
          onPress={markItemFound}
          color="#4CAF50"
        />
      </View>
      
      <FlatList
        data={optimizedRoute}
        renderItem={({ item, index }) => (
          <View style={[
            styles.listItem,
            index === currentIndex && styles.currentListItem,
            index < currentIndex && styles.completedItem
          ]}>
            <Text>{index + 1}. {item.name}</Text>
            <Text style={styles.sublabel}>{item.location}</Text>
          </View>
        )}
      />
    </View>
  );
};
```

## Data Flow

1. **Mobile App** → Makes API calls
2. **Backend API** → Handles heavy processing
3. **Database** → Stores user data, lists, store info
4. **Scraping Service** → Separate service for web scraping
5. **Cache Layer** → Redis for frequently accessed data

## Deployment

### Android
- Build APK with React Native CLI
- Deploy to Google Play Store
- Consider using Expo for easier deployment

### iOS
- Build with Xcode
- Deploy to Apple App Store
- Need Apple Developer account

## Migration Path

1. **Phase 1**: Create backend API
   - Move scraping logic to server
   - Create REST endpoints
   - Set up database

2. **Phase 2**: Build mobile UI
   - Create React Native app
   - Implement core screens
   - Connect to backend

3. **Phase 3**: Add mobile features
   - GPS integration
   - Push notifications
   - Offline support

4. **Phase 4**: Polish and deploy
   - Performance optimization
   - User testing
   - Store deployment