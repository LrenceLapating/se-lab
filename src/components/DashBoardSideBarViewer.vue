<template>
  <div class="sidebar" :class="{ expanded: isExpanded }" @mouseenter="expand" @mouseleave="collapse">
    <div class="logo-section">
      <img src="../assets/Logo-100px-white.png" alt="LabClass Logo" class="logo" />
      <span class="logo-text" v-show="isExpanded">LabClass</span>
    </div>

    <nav class="nav-links">
      <router-link to="/dashboard-viewer" class="nav-link" :class="{ active: $route.path === '/dashboard-viewer' }">
        <div class="icon-container">
          <i class="fas fa-home"></i>
        </div>
        <span v-show="isExpanded">Dashboard</span>
      </router-link>

      <router-link to="/notifications-viewer" class="nav-link" :class="{ active: $route.path === '/notifications-viewer' }">
        <div class="icon-container">
          <i class="fas fa-bell"></i>
        </div>
        <span v-show="isExpanded">Notifications</span>
      </router-link>

      <router-link to="/schedule-viewer" class="nav-link" :class="{ active: $route.path === '/schedule-viewer' }">
        <div class="icon-container">
          <i class="fas fa-calendar"></i>
        </div>
        <span v-show="isExpanded">Schedule</span>
      </router-link>

      <router-link to="/user-profile-viewer" class="nav-link" :class="{ active: $route.path === '/user-profile-viewer' }">
        <div class="icon-container">
          <i class="fas fa-user"></i>
        </div>
        <span v-show="isExpanded">Profile</span>
      </router-link>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'DashBoardSideBarViewer',
  data() {
    return {
      isExpanded: false
    }
  },
  methods: {
    expand() {
      this.isExpanded = true
    },
    collapse() {
      this.isExpanded = false
    }
  }
}
</script>

<style scoped>
.sidebar {
  background-color: #DD385A;
  height: 100vh;
  width: 70px;
  position: fixed;
  left: 0;
  top: 0;
  transition: all 0.3s ease;
  overflow: hidden;
  z-index: 1000;
  font-family: 'Inter', sans-serif;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.sidebar.expanded {
  width: 250px;
}

.logo-section {
  padding: 1.5rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
}

.logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.logo-text {
  color: white;
  font-size: 1.5rem;
  font-weight: 500;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.875rem 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  border-left: 3px solid transparent;
}

.nav-link:hover, .nav-link.active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  border-left-color: white;
}

.icon-container {
  width: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-link i {
  font-size: 1.1rem;
}

.nav-link span {
  margin-left: 1rem;
  font-weight: 400;
  flex: 1;
}
</style>