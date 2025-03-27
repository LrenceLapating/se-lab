<template>
  <div class="dashboard-layout">
    <DashBoardSideBarDean />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="dashboard-header">
          <div class="welcome-section">
            <h2>Schedule Management</h2>
            <p class="date">{{ formattedDate }}</p>
          </div>
        </div>

        <div class="schedule-content">
          <div class="controls-top">
            <div class="search-box">
              <span class="search-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </span>
              <input type="text" placeholder="Search..." />
            </div>
            
            <div class="lab-controls">
              <div class="lab-dropdown-wrapper">
                <select v-model="selectedLab" class="lab-dropdown">
                  <option v-for="lab in labs" :key="lab" :value="lab">{{ lab }}</option>
                </select>
              </div>
            </div>
          </div>

          <div class="schedule-container">
            <div class="schedule-nav">
              <button class="nav-btn" @click="previousDay">
                <i class="fas fa-chevron-left"></i>
              </button>
              <div class="date-display">
                <span class="current-date">{{ currentDateFormatted }}</span>
              </div>
              <button class="nav-btn" @click="nextDay">
                <i class="fas fa-chevron-right"></i>
              </button>
              <button class="today-btn" @click="goToToday">Today</button>
            </div>
            
            <div class="schedule-table">
              <div class="table-header">
                <div class="time-header">Time</div>
                <div class="day-header">
                  <div class="day-name">{{ currentDayName }}</div>
                  <div class="day-date">{{ currentDateFormatted }}</div>
                </div>
              </div>
              
              <div class="table-body">
                <div class="time-column">
                  <div class="time-slot" v-for="time in displayTimeSlots" :key="time">
                    {{ time }}
                  </div>
                </div>
                
                <div class="day-column">
                  <div class="time-slots">
                    <div class="slot" v-for="(time, timeIndex) in displayTimeSlots" :key="timeIndex">
                      <div 
                        v-if="isTimeSlotWithinSchedule(currentDayName, time)"
                        class="schedule-item" 
                        :style="getScheduleStyle(currentDayName, time)"
                      >
                        <div 
                          v-if="isScheduleStart(currentDayName, time)" 
                          class="schedule-content"
                          @click="showScheduleDetails(currentDayName, time)"
                        >
                          <div class="schedule-lab">{{ selectedLab }}</div>
                          <div class="schedule-time">{{ getScheduleTime(currentDayName, time) }}</div>
                          <div class="schedule-title">{{ getScheduleTitle(currentDayName, time) }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedule Details Popup -->
    <div class="schedule-popup" v-if="showPopup">
      <div class="popup-content">
        <div class="popup-header">
          <h3>{{ selectedSchedule.courseName }}</h3>
          <button class="close-btn" @click="closePopup">×</button>
        </div>
        <div class="popup-body">
          <div class="detail-row">
            <span class="detail-label">Lab:</span>
            <span class="detail-value">{{ selectedSchedule.labRoom }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Course:</span>
            <span class="detail-value">{{ selectedSchedule.courseName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Section:</span>
            <span class="detail-value">{{ selectedSchedule.section }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Instructor:</span>
            <span class="detail-value">{{ selectedSchedule.instructorName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Time:</span>
            <span class="detail-value">{{ selectedSchedule.startTime }} - {{ selectedSchedule.endTime }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Day:</span>
            <span class="detail-value">{{ selectedSchedule.day }}</span>
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
  name: 'ScheduleDean',
  components: {
    DashBoardSideBarDean,
    DashBoardTopbar
  },
  data() {
    return {
      selectedLab: 'L201',
      labs: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM',
        '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM',
        '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM',
        '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM',
        '7:30 PM', '8:00 PM'
      ],
      schedules: [],
      currentDate: new Date(),
      showPopup: false,
      selectedSchedule: {}
    }
  },
  computed: {
    formattedDate() {
      const options = { month: 'long', day: 'numeric', year: 'numeric' };
      return this.currentDate.toLocaleDateString('en-US', options);
    },
    currentDateFormatted() {
      const options = { month: 'short', day: 'numeric', year: 'numeric' };
      return this.currentDate.toLocaleDateString('en-US', options);
    },
    currentDayName() {
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      return days[this.currentDate.getDay()];
    }
  },
  created() {
    this.checkAuth();
  },
  mounted() {
    this.checkAuth();
    this.loadSchedulesFromStorage();
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
    previousDay() {
      const date = new Date(this.currentDate);
      date.setDate(date.getDate() - 1);
      this.currentDate = date;
    },
    nextDay() {
      const date = new Date(this.currentDate);
      date.setDate(date.getDate() + 1);
      this.currentDate = date;
    },
    goToToday() {
      this.currentDate = new Date();
    },
    isTimeSlotInSchedule(timeSlot, startTime, endTime) {
      try {
        // Convert timeSlot, startTime, and endTime to minutes for easy comparison
        const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
        const startTimeMinutes = this.convertTimeToMinutes(startTime);
        const endTimeMinutes = this.convertTimeToMinutes(endTime);
        
        // Check if timeSlot is within or at the start of the schedule
        return timeSlotMinutes >= startTimeMinutes && timeSlotMinutes < endTimeMinutes;
      } catch (error) {
        console.error('Error checking if time slot is in schedule:', error);
        return false;
      }
    },
    convertTimeToMinutes(time) {
      try {
        // Parse time string (format: "HH:MM AM/PM")
        const [hourStr, minutePeriodStr] = time.split(':');
        if (!minutePeriodStr) {
          console.error('Invalid time format:', time);
          return 0;
        }
        
        let hour = parseInt(hourStr, 10);
        
        // Extract minutes and period (AM/PM)
        let minuteStr, period;
        if (minutePeriodStr.includes('AM') || minutePeriodStr.includes('PM')) {
          const periodsIndex = minutePeriodStr.indexOf('AM') !== -1 ? minutePeriodStr.indexOf('AM') : minutePeriodStr.indexOf('PM');
          minuteStr = minutePeriodStr.substring(0, periodsIndex).trim();
          period = minutePeriodStr.substring(periodsIndex).trim();
        } else {
          minuteStr = minutePeriodStr;
          period = '';
        }
        
        const minute = parseInt(minuteStr, 10);
        
        // Convert 12-hour format to 24-hour format
        if (period === 'PM' && hour < 12) {
          hour += 12;
        } else if (period === 'AM' && hour === 12) {
          hour = 0;
        }
        
        return hour * 60 + minute;
      } catch (error) {
        console.error('Error converting time to minutes:', error, time);
        return 0;
      }
    },
    loadSchedulesFromStorage() {
      try {
        // Try to load the schedules from localStorage
        const schedulesJson = localStorage.getItem('labSchedules');
        if (schedulesJson) {
          this.schedules = JSON.parse(schedulesJson);
        } else {
          // If no schedules in localStorage, initialize with mock data
          this.initializeMockSchedules();
        }
      } catch (error) {
        console.error('Error loading schedules from storage:', error);
        this.initializeMockSchedules();
      }
    },
    initializeMockSchedules() {
      // Sample data
      this.schedules = [
        {
          id: 1,
          labRoom: 'L201',
          day: 'Monday',
          startTime: '9:00 AM',
          endTime: '11:00 AM',
          courseName: 'Database Management Systems',
          section: 'IT3A',
          instructorName: 'Dr. Jane Smith',
          color: '#FFD700'
        },
        {
          id: 2,
          labRoom: 'L201',
          day: 'Monday',
          startTime: '1:00 PM',
          endTime: '3:00 PM',
          courseName: 'Web Development',
          section: 'CS2B',
          instructorName: 'Prof. Michael Johnson',
          color: '#32CD32'
        },
        {
          id: 3,
          labRoom: 'L201',
          day: 'Wednesday',
          startTime: '10:00 AM',
          endTime: '12:00 PM',
          courseName: 'Networking Fundamentals',
          section: 'IT2A',
          instructorName: 'Dr. Robert Chen',
          color: '#4169E1'
        }
      ];
      
      // Save to localStorage for persistence
      localStorage.setItem('labSchedules', JSON.stringify(this.schedules));
    },
    isTimeSlotWithinSchedule(day, timeSlot) {
      return this.getSchedulesForTimeslot(day, timeSlot, this.selectedLab).length > 0;
    },
    getSchedulesForTimeslot(day, timeSlot, labRoom) {
      return this.schedules.filter(schedule => 
        schedule.day === day && 
        schedule.labRoom === labRoom &&
        this.isTimeSlotInSchedule(timeSlot, schedule.startTime, schedule.endTime)
      );
    },
    isScheduleStart(day, timeSlot) {
      const relevantSchedules = this.getSchedulesForTimeslot(day, timeSlot, this.selectedLab);
      if (relevantSchedules.length === 0) return false;
      
      // Check if this is the starting timeslot for any of the schedules
      return relevantSchedules.some(schedule => {
        const scheduleStartMinutes = this.convertTimeToMinutes(schedule.startTime);
        const timeslotMinutes = this.convertTimeToMinutes(timeSlot);
        
        // True if the timeslot is within 30 minutes of the start time (first slot)
        return Math.abs(scheduleStartMinutes - timeslotMinutes) <= 30;
      });
    },
    getScheduleStyle(day, timeSlot) {
      const schedules = this.getSchedulesForTimeslot(day, timeSlot, this.selectedLab);
      if (schedules.length === 0) return {};
      
      return {
        backgroundColor: schedules[0].color || '#4169E1',
        opacity: this.isScheduleStart(day, timeSlot) ? 1 : 0.7
      };
    },
    getScheduleTime(day, timeSlot) {
      const schedules = this.getSchedulesForTimeslot(day, timeSlot, this.selectedLab);
      if (schedules.length === 0) return '';
      
      return `${schedules[0].startTime} - ${schedules[0].endTime}`;
    },
    getScheduleTitle(day, timeSlot) {
      const schedules = this.getSchedulesForTimeslot(day, timeSlot, this.selectedLab);
      if (schedules.length === 0) return '';
      
      return schedules[0].courseName;
    },
    showScheduleDetails(day, timeSlot) {
      const schedules = this.getSchedulesForTimeslot(day, timeSlot, this.selectedLab);
      if (schedules.length === 0) return;
      
      this.selectedSchedule = schedules[0];
      this.showPopup = true;
    },
    closePopup() {
      this.showPopup = false;
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

.schedule-content {
  width: 100%;
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
  max-width: 300px;
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

.lab-controls {
  display: flex;
  align-items: center;
}

.lab-dropdown-wrapper {
  margin-left: 1rem;
}

.lab-dropdown {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  font-size: 0.875rem;
  color: #4a5568;
  background-color: white;
  min-width: 120px;
  cursor: pointer;
  transition: all 0.2s;
}

.lab-dropdown:focus {
  outline: none;
  border-color: #CBD5E0;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.schedule-container {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.schedule-nav {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.nav-btn {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.875rem;
  color: #4a5568;
  transition: all 0.2s;
}

.nav-btn:hover {
  background-color: #edf2f7;
}

.date-display {
  margin: 0 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
}

.today-btn {
  margin-left: auto;
  background-color: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.today-btn:hover {
  background-color: #edf2f7;
}

.schedule-table {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.table-header {
  display: flex;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.time-header {
  width: 100px;
  padding: 1rem;
  font-weight: 600;
  color: #4a5568;
  text-align: center;
  border-right: 1px solid #e2e8f0;
}

.day-header {
  flex: 1;
  padding: 1rem;
  text-align: center;
}

.day-name {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.day-date {
  font-size: 0.75rem;
  color: #718096;
}

.table-body {
  display: flex;
  height: 600px;
  overflow-y: auto;
}

.time-column {
  width: 100px;
  flex-shrink: 0;
  border-right: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.time-slot {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: #718096;
  border-bottom: 1px solid #e2e8f0;
}

.day-column {
  flex: 1;
}

.time-slots {
  display: flex;
  flex-direction: column;
}

.slot {
  height: 60px;
  border-bottom: 1px solid #e2e8f0;
  position: relative;
}

.schedule-item {
  position: absolute;
  top: 0;
  left: 5%;
  width: 90%;
  height: 100%;
  border-radius: 5px;
  overflow: hidden;
}

.schedule-content {
  padding: 0.5rem;
  height: 100%;
  color: white;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.schedule-lab {
  font-size: 0.7rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.schedule-time {
  font-size: 0.7rem;
  margin-bottom: 0.25rem;
}

.schedule-title {
  font-size: 0.8rem;
  font-weight: 500;
}

.schedule-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.popup-content {
  background-color: white;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.popup-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #a0aec0;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #4a5568;
}

.popup-body {
  padding: 1.5rem;
}

.detail-row {
  display: flex;
  margin-bottom: 1rem;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  width: 100px;
  font-weight: 600;
  color: #4a5568;
}

.detail-value {
  flex: 1;
  color: #2d3748;
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 1rem;
  }
  
  .time-header {
    width: 60px;
  }
  
  .time-column {
    width: 60px;
  }
}
</style> 