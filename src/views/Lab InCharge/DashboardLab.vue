// DashboardLab.vue
<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="dashboard-header">
          <div class="welcome-section">
            <h2>Welcome, {{ userName }}!</h2>
            <p class="date">{{ formattedDate }}</p>
          </div>
        </div>

        <div class="dashboard-content">
          <div class="left-panel">
            <div class="calendar-box">
              <Calendar @date-selected="generateWeekDays" ref="calendar" />
              <div class="calendar-navigation">
                <button class="cal-nav-btn" @click="previousMonth"><span>‹</span></button>
                <button class="today-btn" @click="goToToday">Today</button>
                <button class="cal-nav-btn" @click="nextMonth"><span>›</span></button>
              </div>
            </div>
          </div>

          <div class="right-panel">
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
              
              <div class="lab-dropdown-wrapper">
                <select v-model="selectedLab" class="lab-dropdown">
                  <option v-for="lab in labs" :key="lab" :value="lab">{{ lab }}</option>
                </select>
              </div>
            </div>

            <div class="schedule-container">
              <div class="schedule-table">
                <div class="table-header">
                  <div class="time-header">Time</div>
                  <div class="day-headers">
                    <div class="day-header" v-for="(day, index) in weekDays" :key="index">
                      <div class="day-name">{{ day.name }}</div>
                      <div class="day-date">{{ day.date }}</div>
                    </div>
                  </div>
                </div>
                
                <div class="table-body">
                  <div class="time-column">
                    <div class="time-slot" v-for="time in displayTimeSlots" :key="time">
                      {{ time }}
                    </div>
                  </div>
                  
                  <div class="days-grid">
                    <div class="day-column" v-for="(day, dayIndex) in weekDays" :key="dayIndex">
                      <div class="time-slots">
                        <div class="slot" v-for="(time, timeIndex) in displayTimeSlots" :key="timeIndex">
                          <div 
                            v-if="isTimeSlotWithinSchedule(day.name, time)"
                            class="schedule-item" 
                            :style="getScheduleStyle(day.name, time)"
                          >
                            <div 
                              v-if="isScheduleStart(day.name, time)" 
                              class="schedule-content"
                              @click="showScheduleDetails(day.name, time)"
                            >
                              <div class="schedule-lab">{{ selectedLab }}</div>
                              <div class="schedule-time">{{ getScheduleTime(day.name, time) }}</div>
                              <div class="course-title">{{ getScheduleTitle(day.name, time) }}</div>
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
      </div>
    </div>
    
    <!-- Schedule Details Popup -->
    <div class="schedule-popup" v-if="showPopup">
      <div class="popup-content">
        <div class="popup-header">
          <h3>{{ selectedSchedule.title }}</h3>
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
import DashBoardSidebarLab from '../../components/DashBoardSidebarLab.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import Calendar from '../../components/Calendar.vue'

export default {
  name: 'DashboardLab',
  components: {
    DashBoardSidebar: DashBoardSidebarLab,
    DashBoardTopbar,
    Calendar
  },
  data() {
    return {
      selectedLab: 'L202',
      labs: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM',
        '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM',
        '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM',
        '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM',
        '7:30 PM', '8:00 PM'
      ],
      schedules: [],
      weekDays: [],
      currentDate: new Date(),
      showPopup: false,
      selectedSchedule: {},
      userName: 'User'
    }
  },
  computed: {
    formattedDate() {
      const options = { month: 'long', day: 'numeric', year: 'numeric' };
      return this.currentDate.toLocaleDateString('en-US', options);
    }
  },
  mounted() {
    this.loadSchedulesFromStorage();
    this.generateWeekDays();
    this.getUserName();
  },
  methods: {
    previousLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex > 0) {
        this.selectedLab = this.labs[currentIndex - 1]
      }
    },
    nextLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex < this.labs.length - 1) {
        this.selectedLab = this.labs[currentIndex + 1]
      }
    },
    generateWeekDays(date) {
      if (date) {
        this.currentDate = date;
      }
      
      const monday = new Date(this.currentDate);
      monday.setDate(this.currentDate.getDate() - this.currentDate.getDay() + 1);

      this.weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((name, index) => {
        const date = new Date(monday)
        date.setDate(monday.getDate() + index)
        
        // Format the date as "Mar 17, 2025" 
        const formattedDate = date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          year: 'numeric'
        });
        
        return {
          name,
          date: formattedDate
        }
      })
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
        
        const minutePeriod = minutePeriodStr.trim();
        const minuteStr = minutePeriod.split(' ')[0];
        const period = minutePeriod.split(' ')[1];
        
        if (!hourStr || !minuteStr || !period) {
          console.error('Invalid time components:', { hourStr, minuteStr, period });
          return 0;
        }
        
        let hour = parseInt(hourStr);
        const minute = parseInt(minuteStr);
        
        // Convert to 24-hour format
        if (period === 'PM' && hour < 12) hour += 12;
        if (period === 'AM' && hour === 12) hour = 0;
        
        const totalMinutes = hour * 60 + minute;
        
        // Return total minutes
        return totalMinutes;
      } catch (error) {
        console.error('Error converting time to minutes:', time, error);
        return 0;
      }
    },
    isTimeSlotWithinSchedule(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        const isEndTimeSlot = timeSlot === schedule.endTime;
        
        return (timeSlotMinutes >= startMinutes && timeSlotMinutes < endMinutes) || isEndTimeSlot;
      });
    },
    isScheduleStart(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        return timeSlotMinutes === startMinutes;
      });
    },
    getScheduleTitle(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return relevantSchedules[0].title;
    },
    getScheduleTime(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return `${relevantSchedules[0].startTime} - ${relevantSchedules[0].endTime}`;
    },
    getScheduleDetails(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      
      const schedule = relevantSchedules[0];
      // Format to match example: course name, section, instructor
      return `${schedule.courseName}\n${schedule.section}\n${schedule.instructorName}`;
    },
    getScheduleStyle(dayName, timeSlot) {
      // Filter by current lab room
      const schedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        return slotMinutes >= startMinutes && slotMinutes < endMinutes;
      });
      
      if (schedules.length === 0) return {};
      
      return {
        backgroundColor: schedules[0].color || '#DD385A'
      };
    },
    loadSchedulesFromStorage() {
      try {
        this.schedules = []; // Initialize as empty array
        
        // Load lab schedules
        const labSchedules = localStorage.getItem('labSchedules');
        if (labSchedules) {
          const parsedLabSchedules = JSON.parse(labSchedules);
          if (Array.isArray(parsedLabSchedules)) {
            const approvedLabSchedules = parsedLabSchedules.filter(schedule => schedule.status === 'approved');
            this.schedules = [...this.schedules, ...approvedLabSchedules];
          }
        }

        // Load viewer schedules
        const viewerSchedules = localStorage.getItem('viewer_schedules');
        if (viewerSchedules) {
          const parsedViewerSchedules = JSON.parse(viewerSchedules);
          if (Array.isArray(parsedViewerSchedules)) {
            const approvedViewerSchedules = parsedViewerSchedules.filter(schedule => schedule.status === 'approved');
            this.schedules = [...this.schedules, ...approvedViewerSchedules];
          }
        }

        // Load generic schedules
        const genericSchedules = localStorage.getItem('generic_schedules');
        if (genericSchedules) {
          const parsedGenericSchedules = JSON.parse(genericSchedules);
          if (Array.isArray(parsedGenericSchedules)) {
            const approvedGenericSchedules = parsedGenericSchedules.filter(schedule => schedule.status === 'approved');
            this.schedules = [...this.schedules, ...approvedGenericSchedules];
          }
        }

        // De-duplicate schedules based on composite key (day + startTime + labRoom)
        const uniqueSchedules = [];
        const seen = new Set();
        
        this.schedules.forEach(schedule => {
          const key = `${schedule.day}-${schedule.startTime}-${schedule.labRoom}`;
          if (!seen.has(key)) {
            seen.add(key);
            uniqueSchedules.push(schedule);
          }
        });

        // Filter schedules for the lab in charge's assigned lab
        this.schedules = uniqueSchedules.filter(schedule => schedule.labRoom === this.selectedLab);
      } catch (error) {
        console.error('Error loading schedules from localStorage:', error);
        this.schedules = []; // Ensure schedules is an array even if loading fails
      }
    },
    previousMonth() {
      if (this.$refs.calendar) {
        this.$refs.calendar.previousMonth();
      }
    },
    nextMonth() {
      if (this.$refs.calendar) {
        this.$refs.calendar.nextMonth();
      }
    },
    goToToday() {
      if (this.$refs.calendar) {
        this.$refs.calendar.goToToday();
      }
    },
    showScheduleDetails(dayName, timeSlot) {
      // Find the schedule for this day and timeSlot
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return;
      
      this.selectedSchedule = relevantSchedules[0];
      this.showPopup = true;
    },
    closePopup() {
      this.showPopup = false;
    },
    getUserName() {
      // Get user data from session or local storage
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      if (userStr) {
        try {
          const userData = JSON.parse(userStr);
          if (userData.full_name) {
            // Get first name only
            this.userName = userData.full_name.split(' ')[0];
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
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
  display: flex;
  flex-direction: column;
  width: calc(100% - 70px);
}

.content-wrapper {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.dashboard-header {
  margin-bottom: 1.5rem;
}

.welcome-section h2 {
  color: #e91e63;
  font-size: 1.75rem;
  margin: 0;
  font-weight: 500;
}

.welcome-section .date {
  color: #666;
  margin: 5px 0 0 0;
  font-size: 1rem;
}

.dashboard-content {
  display: flex;
  gap: 1.5rem;
}

.left-panel {
  width: 340px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.calendar-box {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.calendar-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0;
}

.cal-nav-btn {
  background: none;
  border: none;
  color: #e91e63;
  font-size: 1.5rem;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.cal-nav-btn span {
  line-height: 1;
  position: relative;
  top: -2px;
}

.today-btn {
  background: #e91e63;
  border: none;
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.controls-top {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 250px;
}

.search-icon {
  color: #999;
  margin-right: 0.5rem;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 0.9rem;
  width: 100%;
}

.lab-dropdown-wrapper {
  width: 150px;
}

.lab-dropdown {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.6rem 0.5rem;
  font-size: 0.9rem;
  color: #333;
  width: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  padding-right: 28px;
  cursor: pointer;
}

.schedule-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  height: 100%;
}

.schedule-table {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-header {
  display: flex;
  border-bottom: 1px solid #eaeaea;
}

.time-header {
  width: 80px;
  padding: 0.75rem 0.5rem;
  text-align: center;
  font-weight: 500;
  color: #e91e63;
  font-size: 0.9rem;
  border-right: 1px solid #eaeaea;
}

.day-headers {
  flex: 1;
  display: flex;
}

.day-header {
  flex: 1;
  padding: 0.75rem 0.5rem;
  text-align: center;
  background-color: #e91e63;
  color: white;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.day-header:last-child {
  border-right: none;
}

.day-name {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.day-date {
  font-size: 0.8rem;
  opacity: 0.9;
}

.table-body {
  display: flex;
  flex: 1;
  overflow-y: auto;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
  border-right: 1px solid #eaeaea;
}

.time-slot {
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 0.85rem;
}

.days-grid {
  display: flex;
  flex: 1;
}

.day-column {
  flex: 1;
  border-right: 1px solid #eaeaea;
}

.day-column:last-child {
  border-right: none;
}

.time-slots {
  display: flex;
  flex-direction: column;
}

.slot {
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  position: relative;
}

.schedule-item {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background-color: #DD385A;
  color: white;
  padding: 0.5rem;
  overflow: hidden;
  z-index: 5;
}

.schedule-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
  cursor: pointer;
  text-align: center;
}

.schedule-title {
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.schedule-lab {
  font-weight: 600;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
  background-color: rgba(0, 0, 0, 0.15);
  padding: 2px 5px;
  border-radius: 3px;
  display: inline-block;
}

.schedule-time {
  font-size: 0.75rem;
  opacity: 0.9;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.schedule-details {
  font-size: 0.75rem;
  opacity: 0.9;
  white-space: pre-wrap;
}

.table-body::-webkit-scrollbar {
  width: 8px;
}

.table-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-body::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.table-body::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.schedule-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background-color: white;
  border-radius: 8px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.popup-header {
  background-color: #e91e63;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.popup-body {
  padding: 1.5rem;
}

.detail-row {
  margin-bottom: 0.75rem;
  display: flex;
}

.detail-label {
  font-weight: 500;
  width: 100px;
  color: #666;
}

.detail-value {
  flex: 1;
}
</style>