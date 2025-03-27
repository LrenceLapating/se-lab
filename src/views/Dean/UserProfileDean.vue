<template>
  <div class="dashboard-layout">
    <DashBoardSideBarDean />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="dashboard-header">
          <div class="welcome-section">
            <h2>User Profile</h2>
            <p class="date">{{ formattedDate }}</p>
          </div>
        </div>

        <div class="profile-content">
          <div class="profile-container">
            <div class="profile-header">
              <div class="profile-avatar">
                <img v-if="profileData.avatarUrl" :src="profileData.avatarUrl" alt="Profile Avatar" />
                <div v-else class="avatar-placeholder">
                  {{ getInitials(profileData.fullName) }}
                </div>
              </div>
              <div class="profile-info">
                <h3 class="profile-name">{{ profileData.fullName }}</h3>
                <div class="profile-role">
                  <span class="role-badge dean">{{ profileData.role }}</span>
                </div>
                <p class="profile-details">{{ profileData.department }}</p>
                <p class="profile-details">{{ profileData.email }}</p>
              </div>
            </div>

            <div class="profile-tabs">
              <button 
                class="tab-btn" 
                :class="{ active: activeTab === 'personal' }"
                @click="activeTab = 'personal'"
              >
                Personal Information
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeTab === 'security' }"
                @click="activeTab = 'security'"
              >
                Security
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeTab === 'preferences' }"
                @click="activeTab = 'preferences'"
              >
                Preferences
              </button>
            </div>

            <div class="profile-tab-content">
              <!-- Personal Information Tab -->
              <div v-if="activeTab === 'personal'" class="tab-panel">
                <form @submit.prevent="updatePersonalInfo" class="profile-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Full Name</label>
                      <input type="text" v-model="profileData.fullName" />
                    </div>
                    <div class="form-group">
                      <label>Email</label>
                      <input type="email" v-model="profileData.email" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Department</label>
                      <input type="text" v-model="profileData.department" />
                    </div>
                    <div class="form-group">
                      <label>Phone Number</label>
                      <input type="tel" v-model="profileData.phoneNumber" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Bio</label>
                      <textarea v-model="profileData.bio" rows="4"></textarea>
                    </div>
                  </div>
                  <div class="form-actions">
                    <button type="submit" class="btn-save">Save Changes</button>
                  </div>
                </form>
              </div>

              <!-- Security Tab -->
              <div v-if="activeTab === 'security'" class="tab-panel">
                <form @submit.prevent="changePassword" class="profile-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Current Password</label>
                      <input type="password" v-model="securityData.currentPassword" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>New Password</label>
                      <input type="password" v-model="securityData.newPassword" />
                    </div>
                    <div class="form-group">
                      <label>Confirm New Password</label>
                      <input type="password" v-model="securityData.confirmPassword" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Two-Factor Authentication</label>
                      <div class="toggle-switch">
                        <input type="checkbox" id="twoFactor" v-model="securityData.twoFactorEnabled" />
                        <label for="twoFactor"></label>
                        <span>{{ securityData.twoFactorEnabled ? 'Enabled' : 'Disabled' }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="form-actions">
                    <button type="submit" class="btn-save">Save Changes</button>
                  </div>
                </form>
              </div>

              <!-- Preferences Tab -->
              <div v-if="activeTab === 'preferences'" class="tab-panel">
                <form @submit.prevent="savePreferences" class="profile-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Language</label>
                      <select v-model="preferencesData.language">
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>Timezone</label>
                      <select v-model="preferencesData.timezone">
                        <option value="GMT-8">Pacific Time (GMT-8)</option>
                        <option value="GMT-7">Mountain Time (GMT-7)</option>
                        <option value="GMT-6">Central Time (GMT-6)</option>
                        <option value="GMT-5">Eastern Time (GMT-5)</option>
                        <option value="GMT">Greenwich Mean Time (GMT)</option>
                        <option value="GMT+1">Central European Time (GMT+1)</option>
                        <option value="GMT+8">Philippines Time (GMT+8)</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Email Notifications</label>
                      <div class="toggle-switch">
                        <input type="checkbox" id="emailNotif" v-model="preferencesData.emailNotifications" />
                        <label for="emailNotif"></label>
                        <span>{{ preferencesData.emailNotifications ? 'Enabled' : 'Disabled' }}</span>
                      </div>
                    </div>
                    <div class="form-group">
                      <label>Dark Mode</label>
                      <div class="toggle-switch">
                        <input type="checkbox" id="darkMode" v-model="preferencesData.darkMode" />
                        <label for="darkMode"></label>
                        <span>{{ preferencesData.darkMode ? 'Enabled' : 'Disabled' }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="form-actions">
                    <button type="submit" class="btn-save">Save Changes</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSuccessMessage" class="success-message">
      <div class="success-content">
        <i class="fas fa-check-circle"></i>
        <p>Changes saved successfully!</p>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSideBarDean from '../../components/DashBoardSideBarDean.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'UserProfileDean',
  components: {
    DashBoardSideBarDean,
    DashBoardTopbar
  },
  data() {
    return {
      currentDate: new Date(),
      activeTab: 'personal',
      showSuccessMessage: false,
      profileData: {
        fullName: 'Dr. Jane Smith',
        role: 'Dean',
        department: 'College of Computer Science',
        email: 'jane.smith@example.edu',
        phoneNumber: '+63 912 345 6789',
        bio: 'Dr. Jane Smith is the Dean of the College of Computer Science with over 15 years of experience in computer science education and research.',
        avatarUrl: null
      },
      securityData: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
        twoFactorEnabled: false
      },
      preferencesData: {
        language: 'en',
        timezone: 'GMT+8',
        emailNotifications: true,
        darkMode: false
      }
    }
  },
  computed: {
    formattedDate() {
      const options = { month: 'long', day: 'numeric', year: 'numeric' };
      return this.currentDate.toLocaleDateString('en-US', options);
    }
  },
  created() {
    this.checkAuth();
    this.loadUserData();
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
    loadUserData() {
      // In a real app, you would fetch the user profile from an API
      // For now, we'll use the default mock data in the data() function
      const userDataStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      if (userDataStr) {
        try {
          const userData = JSON.parse(userDataStr);
          if (userData.full_name) {
            this.profileData.fullName = userData.full_name;
          }
          if (userData.email) {
            this.profileData.email = userData.email;
          }
          if (userData.role) {
            this.profileData.role = userData.role;
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    },
    getInitials(name) {
      if (!name) return '';
      
      return name
        .split(' ')
        .map(part => part[0])
        .join('')
        .toUpperCase();
    },
    updatePersonalInfo() {
      // In a real app, you would send the updated profile to an API
      console.log('Updating personal info:', this.profileData);
      this.showSuccess();
    },
    changePassword() {
      // Validate password change
      if (this.securityData.newPassword !== this.securityData.confirmPassword) {
        alert('New passwords do not match');
        return;
      }
      
      if (!this.securityData.currentPassword) {
        alert('Please enter your current password');
        return;
      }
      
      if (this.securityData.newPassword.length < 8) {
        alert('New password must be at least 8 characters long');
        return;
      }
      
      // In a real app, you would send the password change request to an API
      console.log('Changing password');
      
      // Clear password fields after submission
      this.securityData.currentPassword = '';
      this.securityData.newPassword = '';
      this.securityData.confirmPassword = '';
      
      this.showSuccess();
    },
    savePreferences() {
      // In a real app, you would send the updated preferences to an API
      console.log('Saving preferences:', this.preferencesData);
      this.showSuccess();
    },
    showSuccess() {
      this.showSuccessMessage = true;
      setTimeout(() => {
        this.showSuccessMessage = false;
      }, 3000);
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

.profile-content {
  width: 100%;
}

.profile-container {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.profile-header {
  display: flex;
  padding: 2rem;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin-right: 2rem;
  overflow: hidden;
  flex-shrink: 0;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background-color: #DD385A;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 600;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.profile-role {
  margin-bottom: 0.75rem;
}

.role-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.role-badge.dean {
  background-color: #805AD5;
}

.profile-details {
  font-size: 0.875rem;
  color: #4a5568;
  margin-bottom: 0.25rem;
}

.profile-tabs {
  display: flex;
  padding: 0 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.tab-btn {
  padding: 1rem 1.5rem;
  font-size: 0.875rem;
  color: #718096;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #2d3748;
}

.tab-btn.active {
  color: #DD385A;
  border-bottom-color: #DD385A;
}

.profile-tab-content {
  padding: 2rem;
}

.tab-panel {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

.profile-form {
  max-width: 100%;
}

.form-row {
  display: flex;
  margin-bottom: 1.5rem;
  gap: 1.5rem;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 0.875rem;
  color: #4a5568;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  font-size: 0.875rem;
  color: #4a5568;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #CBD5E0;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.toggle-switch {
  display: flex;
  align-items: center;
}

.toggle-switch input {
  display: none;
}

.toggle-switch label {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  background-color: #CBD5E0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  margin-right: 0.75rem;
  margin-bottom: 0;
}

.toggle-switch label::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: white;
  top: 2px;
  left: 2px;
  transition: all 0.3s;
}

.toggle-switch input:checked + label {
  background-color: #DD385A;
}

.toggle-switch input:checked + label::after {
  transform: translateX(24px);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.btn-save {
  padding: 0.75rem 1.5rem;
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save:hover {
  background-color: #C52F4E;
}

.success-message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #48BB78;
  color: white;
  padding: 1rem;
  border-radius: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  animation: slideIn 0.3s ease-out, fadeOut 0.3s ease-in 2.7s forwards;
}

.success-content {
  display: flex;
  align-items: center;
}

.success-content i {
  margin-right: 0.75rem;
  font-size: 1.25rem;
}

.success-content p {
  margin: 0;
}

@keyframes slideIn {
  0% { transform: translateX(100%); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
}

@keyframes fadeOut {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 1rem;
  }
  
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .profile-avatar {
    margin-right: 0;
    margin-bottom: 1.5rem;
  }
  
  .profile-tabs {
    overflow-x: auto;
    padding: 0;
  }
  
  .form-row {
    flex-direction: column;
    gap: 1rem;
  }
}
</style> 