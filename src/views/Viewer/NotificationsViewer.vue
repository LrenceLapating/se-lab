// NotificationsViewer.vue
<template>
  <div class="dashboard-layout">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar :pageTitle="'Notifications'" />
      <div class="content-wrapper">
        <h1>Notifications</h1>
        
        <div class="filters">
          <div class="dropdown-container">
            <select v-model="selectedFilter" class="filter-dropdown">
              <option value="all">All Notifications</option>
              <option value="schedule">Schedule Updates</option>
              <option value="system">System Announcements</option>
            </select>
          </div>
          
          <div class="dropdown-container">
            <select v-model="sortBy" class="filter-dropdown">
              <option value="newest">Sort By: Newest</option>
              <option value="oldest">Sort By: Oldest</option>
            </select>
          </div>
        </div>

        <div class="notifications-list">
          <div v-if="notifications.length === 0" class="no-notifications">
            No notifications available
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebar from '../../components/DashBoardSideBarViewer.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'NotificationsViewer',
  components: {
    DashBoardSidebar,
    DashBoardTopbar
  },
  data() {
    return {
      selectedFilter: 'all',
      sortBy: 'newest',
      notifications: [] // Empty array ready for backend data
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', sans-serif;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  width: 100%;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  transition: margin-left 0.3s;
  display: flex;
  flex-direction: column;
  width: calc(100% - 70px);
}

.main-content.expanded {
  margin-left: 240px;
  width: calc(100% - 240px);
}

.content-wrapper {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.content-wrapper::-webkit-scrollbar {
  width: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: #DD385A;
  border-radius: 4px;
}

h1 {
  font-size: 1.75rem;
  font-weight: 500;
  color: #DD385A;
  margin-bottom: 1.5rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.dropdown-container {
  position: relative;
}

.filter-dropdown {
  padding: 0.5rem 1rem;
  border: none;
  background: #ffebee;
  color: #DD385A;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.no-notifications {
  text-align: center;
  padding: 2rem;
  color: #DD385A;
  background: #ffebee;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
}
</style>