<template>
  <div class="dashboard-layout">
    <DashBoardSideBarDean />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="dashboard-header">
          <div class="welcome-section">
            <h2>Notifications</h2>
            <p class="date">{{ formattedDate }}</p>
          </div>
        </div>

        <div class="notifications-content">
          <div class="controls-top">
            <div class="search-box">
              <span class="search-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </span>
              <input type="text" placeholder="Search notifications..." v-model="searchQuery" />
            </div>

            <div class="filter-controls">
              <select v-model="selectedFilter" class="filter-dropdown">
                <option value="all">All Notifications</option>
                <option value="unread">Unread</option>
                <option value="read">Read</option>
              </select>
            </div>
          </div>

          <div class="notifications-container">
            <div v-if="filteredNotifications.length === 0" class="no-notifications">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"></path>
              </svg>
              <p>No notifications to display</p>
            </div>

            <div v-else class="notifications-list">
              <div 
                v-for="notification in filteredNotifications" 
                :key="notification.id" 
                class="notification-item"
                :class="{ 'unread': !notification.read }"
                @click="markAsRead(notification)"
              >
                <div class="notification-icon" :class="notification.type">
                  <i :class="getIconClass(notification.type)"></i>
                </div>
                <div class="notification-content">
                  <div class="notification-header">
                    <h3 class="notification-title">{{ notification.title }}</h3>
                    <span class="notification-time">{{ formatTime(notification.timestamp) }}</span>
                  </div>
                  <p class="notification-message">{{ notification.message }}</p>
                </div>
                <div v-if="!notification.read" class="unread-indicator"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSideBarDean from '../../components/DashBoardSideBarDean.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'NotificationsDean',
  components: {
    DashBoardSideBarDean,
    DashBoardTopbar
  },
  data() {
    return {
      currentDate: new Date(),
      searchQuery: '',
      selectedFilter: 'all',
      notifications: [
        {
          id: 1,
          type: 'info',
          title: 'New Schedule Added',
          message: 'A new laboratory schedule has been added for the Database Management class.',
          timestamp: new Date(new Date().setHours(new Date().getHours() - 1)),
          read: false
        },
        {
          id: 2,
          type: 'alert',
          title: 'Schedule Conflict',
          message: 'There is a scheduling conflict for the Web Development class in L203.',
          timestamp: new Date(new Date().setHours(new Date().getHours() - 3)),
          read: false
        },
        {
          id: 3,
          type: 'success',
          title: 'Schedule Approved',
          message: 'The proposed schedule for the Programming Fundamentals class has been approved.',
          timestamp: new Date(new Date().setDate(new Date().getDate() - 1)),
          read: true
        },
        {
          id: 4,
          type: 'info',
          title: 'Department Meeting',
          message: 'Reminder: Department meeting tomorrow at 10:00 AM in the conference room.',
          timestamp: new Date(new Date().setDate(new Date().getDate() - 2)),
          read: true
        },
        {
          id: 5,
          type: 'alert',
          title: 'Maintenance Schedule',
          message: 'Laboratory L205 will be under maintenance next Monday. Please adjust schedules accordingly.',
          timestamp: new Date(new Date().setDate(new Date().getDate() - 3)),
          read: true
        }
      ]
    }
  },
  computed: {
    formattedDate() {
      const options = { month: 'long', day: 'numeric', year: 'numeric' };
      return this.currentDate.toLocaleDateString('en-US', options);
    },
    filteredNotifications() {
      let filtered = this.notifications;
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(notification => 
          notification.title.toLowerCase().includes(query) || 
          notification.message.toLowerCase().includes(query)
        );
      }
      
      if (this.selectedFilter === 'unread') {
        filtered = filtered.filter(notification => !notification.read);
      } else if (this.selectedFilter === 'read') {
        filtered = filtered.filter(notification => notification.read);
      }
      
      // Sort by timestamp, newest first
      return filtered.sort((a, b) => b.timestamp - a.timestamp);
    }
  },
  created() {
    this.checkAuth();
  },
  mounted() {
    this.checkAuth();
  },
  methods: {
    checkAuth() {
      // Check if user is authenticated and has the correct role
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      
      if (!token || !userStr) {
        console.error('No authentication found, redirecting to login');
        this.$router.push('/login');
        return;
      }
      
      try {
        const userData = JSON.parse(userStr);
        
        // Verify the user has Dean role
        if (userData.role !== 'Dean') {
          console.error('User does not have Dean role');
          // Redirect to the appropriate dashboard based on role
          if (userData.role === 'System Administrator') {
            this.$router.push('/dashboard-sysad');
          } else if (userData.role === 'Academic Coordinator') {
            this.$router.push('/dashboard-acad-coor');
          } else if (userData.role === 'Lab InCharge') {
            this.$router.push('/dashboard-lab');
          } else {
            this.$router.push('/dashboard-viewer');
          }
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        this.$router.push('/login');
      }
    },
    formatTime(timestamp) {
      const now = new Date();
      const diff = Math.floor((now - timestamp) / 1000); // diff in seconds
      
      if (diff < 60) {
        return 'Just now';
      } else if (diff < 3600) {
        const minutes = Math.floor(diff / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      } else if (diff < 86400) {
        const hours = Math.floor(diff / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      } else if (diff < 604800) {
        const days = Math.floor(diff / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
      } else {
        const options = { month: 'short', day: 'numeric' };
        return timestamp.toLocaleDateString('en-US', options);
      }
    },
    getIconClass(type) {
      switch (type) {
        case 'info': return 'fas fa-info-circle';
        case 'alert': return 'fas fa-exclamation-triangle';
        case 'success': return 'fas fa-check-circle';
        default: return 'fas fa-bell';
      }
    },
    markAsRead(notification) {
      // Mark the notification as read
      if (!notification.read) {
        notification.read = true;
        // In a real app, you would send this update to a backend API
      }
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: 100vh;
  width: 100%;
  position: relative;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  transition: margin-left 0.3s ease;
  overflow: hidden;
  width: calc(100% - 70px);
  background-color: #f5f7fa;
}

.content-wrapper {
  padding: 2rem;
  overflow-y: auto;
  height: calc(100vh - 80px);
}

.dashboard-header {
  margin-bottom: 2rem;
}

.welcome-section h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.welcome-section .date {
  font-size: 1rem;
  color: #718096;
}

.controls-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  font-size: 0.875rem;
  color: #4a5568;
  background-color: white;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #CBD5E0;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.filter-controls {
  display: flex;
  align-items: center;
}

.filter-dropdown {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  font-size: 0.875rem;
  color: #4a5568;
  background-color: white;
  min-width: 160px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-dropdown:focus {
  outline: none;
  border-color: #CBD5E0;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.notifications-container {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  min-height: 300px;
}

.no-notifications {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  color: #a0aec0;
}

.no-notifications svg {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-notifications p {
  font-size: 1rem;
}

.notifications-list {
  display: flex;
  flex-direction: column;
}

.notification-item {
  display: flex;
  padding: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background-color: #f8fafc;
}

.notification-item.unread {
  background-color: #f0f9ff;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.notification-icon.info {
  background-color: #ebf8ff;
  color: #3182ce;
}

.notification-icon.alert {
  background-color: #fff5f5;
  color: #e53e3e;
}

.notification-icon.success {
  background-color: #f0fff4;
  color: #38a169;
}

.notification-content {
  flex: 1;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.notification-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.notification-time {
  font-size: 0.75rem;
  color: #a0aec0;
}

.notification-message {
  font-size: 0.875rem;
  color: #4a5568;
  margin: 0;
  line-height: 1.5;
}

.unread-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #3182ce;
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 1rem;
  }
  
  .controls-top {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: 100%;
    margin-bottom: 1rem;
  }
}
</style> 